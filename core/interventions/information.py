import numpy as np

from core.interventions.base import InterventionStrategy, register_intervention
from core.interventions.letter import apply_trait_deltas


@register_intervention("information")
class InformationCampaignIntervention(InterventionStrategy):
    def select(self, agents: list, config: dict) -> list:
        rates = config["rate"]
        selected = []
        for agent in agents:
            rate = rates[agent.occupation]
            if np.random.random() < rate:
                selected.append(agent)
        return selected
    
    def apply(self, agent, model, config: dict) -> dict:
        effects = config["effects"]
        changes = apply_trait_deltas(agent, effects)
        outcome = {"type": "information", "changes": changes}
        agent.interventions["information"] = outcome
        return outcome
