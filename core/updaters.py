import numpy as np
from statistics import median

from .simcache import sim_cache

def clip(value, low, high):
    return max(low, min(high, value))

class BeliefStrategy:
    def __init__(self, config, strategy_name):
        self.config = config
        self.params = config.belief_strategies[strategy_name]

    def update(self, agent):
        raise NotImplementedError

class HashimzadeBeliefStrategy(BeliefStrategy):
    def update(self, agent):
        self.update_subj_audit_prob(agent)

    def update_subj_audit_prob(self, agent):
        traits = agent.traits
        
        audit = agent.interventions.get("audit")
        if audit:
            # Audited: 50/50 target vs bomb-crater effect
            if np.random.random() < 0.5:
                traits.subjective_audit_prob = 100.0
            else:
                traits.subjective_audit_prob = 0.0
        else:
            # Not audited: drift towards mean
            drift = self.params["drift"][agent.occupation]
            mean = drift["mean"]
            step = drift["step"]
            direction = np.sign(mean - traits.subjective_audit_prob)
            traits.subjective_audit_prob += step * direction

        traits.subjective_audit_prob = clip(traits.subjective_audit_prob, 0.0, 100.0)

class AndreiBeliefStrategy(BeliefStrategy):
    def update(self, agent):
        raise NotImplementedError


class LlacerBeliefStrategy(BeliefStrategy):
    def update(self, agent):
        raise NotImplementedError

class CustomBeliefStrategy(HashimzadeBeliefStrategy):
    def update(self, agent):
        self.update_subj_audit_prob(agent)
        self.update_trust(agent)
        self.update_pso(agent)

    def update_trust(self, agent):
        audit = agent.interventions.get("audit")
        if not audit: return  
    
        config = agent.model.config.trust_update
        traits = agent.traits
        sigma_trust = config["sigma_trust"]
    
        if audit["compliant"]:
            traits.perceived_trustworthiness += 0.5 * sigma_trust
        else:
            p_unfair = config["p_unfair"]
            if np.random.random() < p_unfair:
                traits.perceived_trustworthiness -= 1.0 * sigma_trust
    
        traits.perceived_trustworthiness = clip(traits.perceived_trustworthiness, 1.0, 5.0)

    def update_pso(self, agent):
        config = agent.model.config.config_data.get("pso_update", {})
        sigma_pso = config["sigma_pso"]
        occ_cfg = config[agent.occupation]
        traits = agent.traits
        
        if np.random.random() < occ_cfg["phone_prob"]:
            if np.random.random() < occ_cfg["phone_satisfied_prob"]:
                delta = 1.0 if agent.occupation == "business" else 0.5
                traits.perceived_service_orientation += delta * sigma_pso
            else:
                traits.perceived_service_orientation -= 1.0 * sigma_pso
        
        satisfaction = np.random.normal(occ_cfg["webcare_mean"], occ_cfg["webcare_std"])
        if satisfaction > 3.0:
            traits.perceived_service_orientation += 0.5 * sigma_pso
        else:
            traits.perceived_service_orientation -= 0.5 * sigma_pso
        
        if np.random.random() < occ_cfg.get("huba_prob", 0):
            traits.perceived_service_orientation = 5.0
        
        traits.perceived_service_orientation = clip(traits.perceived_service_orientation, 1.0, 5.0)


BELIEF_STRATEGIES = {
    "hashimzade": HashimzadeBeliefStrategy,
    "andrei": AndreiBeliefStrategy,
    "llacer": LlacerBeliefStrategy,
    "custom": CustomBeliefStrategy,
}

def create_belief_strategy(config):
    strategy_name = config.belief_strategy
    strategy_class = BELIEF_STRATEGIES.get(strategy_name)
    if not strategy_class:
        raise ValueError(f"Unknown belief strategy: {strategy_name}")
    return strategy_class(config, strategy_name)


@sim_cache
def compute_compliance_score(agent):
    if agent.evaded_income == 0:
        return 1.0
    elif agent.true_income > 0:
        return -agent.evaded_income / agent.true_income
    return 0.0


def update_social_norms(agent, raw_score):
    if raw_score is None:
        return

    config = agent.model.config.norm_update
    scale = config["social_norm_scale"][agent.occupation]

    traits = agent.traits
    traits.social_norms = clip(traits.social_norms + raw_score * scale, 1.0, 5.0)


def update_societal_norms(agent, societal_raw_score, n_agents):
    normalized = (2 * societal_raw_score / n_agents) - 1

    config = agent.model.config.norm_update
    scale = config["societal_norm_scale"][agent.occupation]

    traits = agent.traits
    traits.societal_norms = clip(traits.societal_norms + normalized * scale, 1.0, 5.0)


