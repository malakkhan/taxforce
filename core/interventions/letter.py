import numpy as np

from core.interventions.base import InterventionStrategy, register_intervention


def clip(value, low, high):
    return max(low, min(high, value))

def apply_trait_deltas(agent, effects: dict):
    traits = agent.traits
    changes = {}
    
    permanent_delta = effects.get("subjective_audit_prob_permanent", 0.0)
    temporary_delta = effects.get("subjective_audit_prob_temporary", 0.0)
    
    if "subjective_audit_prob_delta" in effects and permanent_delta == 0.0 and temporary_delta == 0.0:
        permanent_delta = effects["subjective_audit_prob_delta"]
    
    if permanent_delta != 0.0 or temporary_delta != 0.0:
        old = traits.subjective_audit_prob
        
        traits.subjective_audit_prob = clip(
            traits.subjective_audit_prob + permanent_delta,
            0.0, 100.0
        )
        
        agent.temporary_audit_boost += temporary_delta
        
        changes["subjective_audit_prob"] = (old, traits.subjective_audit_prob)
        changes["temporary_audit_boost"] = (0.0, agent.temporary_audit_boost)
    
    if "pso_delta" in effects:
        old = traits.pso
        traits.pso = clip(traits.pso + effects["pso_delta"], 1.0, 5.0)
        changes["pso"] = (old, traits.pso)
    
    if "trust_delta" in effects:
        old = traits.p_trust
        traits.p_trust = clip(traits.p_trust + effects["trust_delta"], 1.0, 5.0)
        changes["trust"] = (old, traits.p_trust)
    
    if "social_norm_delta" in effects:
        old = traits.social_norms
        traits.social_norms = clip(traits.social_norms + effects["social_norm_delta"], 1.0, 5.0)
        changes["social_norms"] = (old, traits.social_norms)
    
    if "societal_norm_delta" in effects:
        old = traits.societal_norms
        traits.societal_norms = clip(traits.societal_norms + effects["societal_norm_delta"], 1.0, 5.0)
        changes["societal_norms"] = (old, traits.societal_norms)
    
    if "personal_norm_delta" in effects:
        old = traits.personal_norms
        traits.personal_norms = clip(traits.personal_norms + effects["personal_norm_delta"], 1.0, 5.0)
        changes["personal_norms"] = (old, traits.personal_norms)
    
    return changes

@register_intervention("letter_deterrence")
class DeterrenceLetterIntervention(InterventionStrategy):
    def select(self, agents: list, config: dict) -> list:
        rates = config["rate"]
        strategy = config["selection_strategy"]
        selected = []
        for agent in agents:
            rate = rates[agent.occupation]
            if strategy == "risk_based":
                risk_multiplier = 1.0 + agent.base_risk_score
                rate = min(rate * risk_multiplier, 1.0)
            if np.random.random() < rate:
                selected.append(agent)
        return selected
    
    def apply(self, agent, model, config: dict) -> dict:
        effects = config["effects"]
        changes = apply_trait_deltas(agent, effects)
        outcome = {"type": "deterrence", "changes": changes}
        agent.interventions["letter_deterrence"] = outcome
        return outcome



