import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Set, Any


def clip(value, low, high):
    return max(low, min(high, value))


@dataclass
class UpdateContext:
    interaction_sets: Dict[int, List[Any]]
    compliance_scores: Dict[int, float]
    societal_compliance: float
    audited_agents: Set[int]
    n_agents: int


class BeliefStrategy:
    def __init__(self, config):
        self.config = config
        self.params = config.belief_strategies[config.belief_strategy]
    
    def update_all(self, agents: List, context: UpdateContext):
        for agent in agents:
            self.update(agent, context)
    
    def update(self, agent, context: UpdateContext):
        raise NotImplementedError


class HashimzadeStrategy(BeliefStrategy):
    
    @staticmethod
    def update_audit_belief_personal(agent, config: dict):
        traits = agent.traits
        audit = agent.interventions.get("audit")
        
        if audit:
            if np.random.random() < 0.5:
                traits.subjective_audit_prob = 100.0
            else:
                traits.subjective_audit_prob = 0.0
        
        traits.subjective_audit_prob = clip(traits.subjective_audit_prob, 0.0, 100.0)
    
    def update(self, agent, context: UpdateContext):
        self.update_audit_belief_personal(agent, self.params)


class CustomStrategy(BeliefStrategy):
    
    @staticmethod
    def update_subjective_audit_prob(agent, neighbors: list, config: dict, audited_neighbors: list = None):
        if not neighbors:
            return
            
        p = agent.traits.subjective_audit_prob
        
        mu = config["mu"]
        audit_signal_strength = config["audit_signal_strength"]
        perception_weight = config["perception_weight"]
        
        audit_effect = 0
        if audited_neighbors:
            fraction = len(audited_neighbors) / len(neighbors)
            audit_effect = audit_signal_strength * fraction * (100 - p)
        
        neighbor_probs = [n.traits.subjective_audit_prob for n in neighbors]
        median_n = np.median(neighbor_probs)
        perception_effect = perception_weight * (median_n - p)
        
        social_update = (1 - mu) * (audit_effect + perception_effect)
        agent.traits.subjective_audit_prob = clip(p + social_update, 0.0, 100.0)
    
    @staticmethod
    def update_audit_belief_personal(agent, config: dict):
        traits = agent.traits
        old_prob = traits.subjective_audit_prob
        audit = agent.interventions.get("audit")
        
        if audit:
            delta = config.get("audit_prob_response_delta", 10.0)
            target_prob = config.get("audit_target_prob", 0.5)
            
            # If random < target_prob, we increase belief (Target effect)
            if np.random.random() < target_prob:
                traits.subjective_audit_prob += delta
            else:
                traits.subjective_audit_prob -= delta
        else:
            drift_rate = config["audit_prob_drift_rate"]
            if drift_rate > 0:
                initial_prob = agent.initial_audit_prob
                gap = initial_prob - old_prob
                traits.subjective_audit_prob += drift_rate * gap
            
        traits.subjective_audit_prob = clip(traits.subjective_audit_prob, 0.0, 100.0)
    
    @staticmethod
    def update_trust(agent, config: dict):
        audit = agent.interventions.get("audit")
        if not audit:
            return
        
        traits = agent.traits
        sigma_trust = config["sigma_trust"]
        
        if audit.get("compliant"):
            traits.p_trust += 0.5 * sigma_trust
        else:
            p_unfair = config["p_unfair"]
            if np.random.random() < p_unfair:
                traits.p_trust -= 1.0 * sigma_trust
        
        traits.p_trust = clip(traits.p_trust, 1.0, 5.0)
    
    @staticmethod
    def update_pso(agent, config: dict):
        occ_cfg = config[agent.occupation]
            
        traits = agent.traits
        sigma_pso = config["sigma_pso"]
        
        phone_delta_satisfied = config["phone_delta_satisfied"]
        phone_delta_dissatisfied = config["phone_delta_dissatisfied"]
        webcare_delta = config["webcare_delta"]
        huba_delta = config["huba_delta"]
        
        if np.random.random() < occ_cfg["phone_prob"]:
            if np.random.random() < occ_cfg["phone_satisfied_prob"]:
                multiplier = 1.0 if agent.occupation == "business" else 0.5
                traits.pso += phone_delta_satisfied * multiplier * sigma_pso
            else:
                traits.pso -= phone_delta_dissatisfied * sigma_pso
        
        satisfaction = np.random.normal(occ_cfg["webcare_mean"], occ_cfg["webcare_std"])
        if satisfaction > 3.0:
            traits.pso += webcare_delta * sigma_pso
        else:
            traits.pso -= webcare_delta * sigma_pso
        
        if np.random.random() < occ_cfg.get("huba_prob", 0):
            traits.pso += huba_delta
        
        pso_drift_rate = config["pso_drift_rate"]
        if pso_drift_rate > 0:
            drift = pso_drift_rate * (agent.initial_pso - traits.pso)
            traits.pso += drift
        
        traits.pso = clip(traits.pso, 1.0, 5.0)
    
    @staticmethod
    def update_social_norms(agent, neighbors: list, compliance_scores: dict, config: dict):
        if not neighbors:
            return
            
        raw = sum(compliance_scores.get(n.unique_id, 0) for n in neighbors) / len(neighbors)
        scale = config["social_norm_scale"][agent.occupation]
        
        traits = agent.traits
        traits.social_norms = clip(traits.social_norms + raw * scale, 1.0, 5.0)
    
    @staticmethod
    def update_societal_norms(agent, societal_compliance: float, n_agents: int, config: dict):
        normalized = (2 * societal_compliance / n_agents) - 1
        scale = config["societal_norm_scale"][agent.occupation]
        
        traits = agent.traits
        traits.societal_norms = clip(traits.societal_norms + normalized * scale, 1.0, 5.0)
    
    def update(self, agent, context: UpdateContext):
        neighbors = context.interaction_sets.get(agent.unique_id, [])
        audited_neighbors = [n for n in neighbors if n.unique_id in context.audited_agents]
        
        belief_cfg = self.config.config_data["belief_update"]
        trust_cfg = self.config.config_data["trust_update"]
        pso_cfg = self.config.config_data["pso_update"]
        norm_cfg = self.config.config_data["norm_update"]
        
        self.update_audit_belief_personal(agent, belief_cfg)
        self.update_subjective_audit_prob(agent, neighbors, belief_cfg, audited_neighbors)
        self.update_trust(agent, trust_cfg)
        self.update_pso(agent, pso_cfg)
        self.update_social_norms(agent, neighbors, context.compliance_scores, norm_cfg)
        self.update_societal_norms(agent, context.societal_compliance, context.n_agents, norm_cfg)


BELIEF_STRATEGIES = {
    "hashimzade": HashimzadeStrategy,
    "custom": CustomStrategy,
}


def create_belief_strategy(config) -> BeliefStrategy:
    strategy_name = config.belief_strategy
    strategy_class = BELIEF_STRATEGIES[strategy_name]
    return strategy_class(config)


def compute_compliance_score(agent) -> float:
    if agent.evaded_income == 0:
        return 1.0
    elif agent.true_income > 0:
        return -agent.evaded_income / agent.true_income
    return 0.0
