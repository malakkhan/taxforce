import numpy as np

from core.interventions.base import InterventionStrategy, register_intervention
from core.interventions.letter import apply_trait_deltas


@register_intervention("call")
class PhoneCallIntervention(InterventionStrategy):
    def select(self, agents: list, config: dict) -> list:
        rates = config["rate"]
        strategy = config["selection_strategy"]
        selected = []
        for agent in agents:
            rate = rates[agent.occupation]
            if strategy == "risk_based":
                risk_multiplier = 1.0 + agent.base_risk_score
                rate = min(rate * risk_multiplier, 1.0)
                if agent.prev_evasion_rate > 0.3:
                    rate = min(rate * 1.5, 1.0)
            if np.random.random() < rate:
                selected.append(agent)
        return selected
    
    def apply(self, agent, model, config: dict) -> dict:
        satisfied_prob = config["satisfied_prob"]
        effects = config["effects"]
        
        is_satisfied = np.random.random() < satisfied_prob
        effect_key = "satisfied" if is_satisfied else "dissatisfied"
        
        specific_effects = effects[effect_key]
        changes = apply_trait_deltas(agent, specific_effects)
        
        outcome = {"type": "call", "satisfied": is_satisfied, "changes": changes}
        agent.interventions["call"] = outcome
        return outcome
