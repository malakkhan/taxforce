import numpy as np

from core.filters import (
    opportunity_filter,
    normative_filter,
    rational_choice_filter,
    social_influence_filter,
)
from core.errors import apply_error


class BehaviorStrategy:
    def decide(self, agent) -> float:
        raise NotImplementedError


class HonestBehavior(BehaviorStrategy):
    def decide(self, agent, initial_step=False):
        if initial_step:
            return agent.true_income
        config = agent.model.config.config_data
        declared, error_occurred, error_amount = apply_error(agent, config)
        agent.error_amount = error_amount
        return declared


class DishonestBehavior(BehaviorStrategy):
    def decide(self, agent, initial_step=False):
        agent.error_amount = 0.0
        max_concealable = opportunity_filter(agent)
        willingness = normative_filter(agent, max_concealable)

        if not initial_step:
            willingness = social_influence_filter(agent, willingness, max_concealable)
        final_evasion = rational_choice_filter(agent, willingness)
        
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


def assign_behavior(config, occupation: str) -> BehaviorStrategy:
    behavior_cfg = config.behaviors
    
    if behavior_cfg.get("override_distribution"):
        dist = behavior_cfg["distribution"]
        behavior_type = np.random.choice(list(dist.keys()), p=list(dist.values()))
    else:
        params = behavior_cfg["compliance_inclination"][occupation]
        sampled = np.random.normal(params["mean"], params["std"])
        score = np.clip(sampled, 1.0, 5.0)
        behavior_type = "dishonest" if score < params["threshold"] else "honest"
    
    return create_behavior(behavior_type)
