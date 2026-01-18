import numpy as np

from core.filters import (
    opportunity_filter,
    normative_filter,
    rational_choice_filter,
    social_influence_filter,
)

class BehaviorStrategy:
    def decide(self, agent) -> float:
        raise NotImplementedError

class HonestBehavior(BehaviorStrategy):
    def decide(self, agent):
        return agent.true_income

class DishonestBehavior(BehaviorStrategy):
    def decide(self, agent):
        max_concealable = opportunity_filter(agent)
        willingness = normative_filter(agent, max_concealable)
        provisional = rational_choice_filter(agent, willingness)
        final_evasion = social_influence_filter(agent, provisional, max_concealable)
        
        declared = agent.true_income - final_evasion
        return max(0.0, declared)


BEHAVIORS = {
    "honest": HonestBehavior,
    "dishonest": DishonestBehavior,
}


def create_behavior(behavior_type: str) -> BehaviorStrategy:
    behavior_class = BEHAVIORS.get(behavior_type)
    if not behavior_class:
        raise ValueError(f"Unknown behavior: {behavior_type}")
    return behavior_class()

def assign_behavior(config) -> BehaviorStrategy:
    distribution = config.behaviors["distribution"]
    types = list(distribution.keys())
    probs = list(distribution.values())
    
    chosen = np.random.choice(types, p=probs)
    return create_behavior(chosen)
