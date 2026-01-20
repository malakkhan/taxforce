import numpy as np
from statistics import median

from .simcache import sim_cache

def clip(value, low, high):
    return max(low, min(high, value))

class BeliefStrategy:
    def __init__(self, config, strategy_name):
        self.config = config
        self.params = config.belief_strategies[strategy_name]

    def update(self, agent, was_audited, was_caught, audited_neighbors):
        raise NotImplementedError


class HashimzadeBeliefStrategy(BeliefStrategy):
    def update(self, agent, was_audited, was_caught, audited_neighbors):
        mu = self.params["mu"]
        traits = agent.traits

        if was_audited:
            if np.random.random() < 0.5:
                traits.subjective_audit_prob = 100.0
            else:
                traits.subjective_audit_prob = 0.0
        else:
            drift = self.params["drift"][agent.occupation]
            mean = drift["mean"]
            step = drift["step"]
            direction = np.sign(mean - traits.subjective_audit_prob)
            traits.subjective_audit_prob += step * direction

        if audited_neighbors:
            neighbor_probs = [n.traits.subjective_audit_prob for n in audited_neighbors]
            median_prob = median(neighbor_probs)  # Use statistics.median
            omega = agent.model.social_influence
            traits.subjective_audit_prob = (1 - omega) * traits.subjective_audit_prob + omega * median_prob

        traits.subjective_audit_prob = clip(traits.subjective_audit_prob, 0.0, 100.0)


class AndreiBeliefStrategy(BeliefStrategy):
    def update(self, agent, was_audited, was_caught, audited_neighbors):
        raise NotImplementedError


class LlacerBeliefStrategy(BeliefStrategy):
    def update(self, agent, was_audited, was_caught, audited_neighbors):
        raise NotImplementedError


BELIEF_STRATEGIES = {
    "hashimzade": HashimzadeBeliefStrategy,
    "andrei": AndreiBeliefStrategy,
    "llacer": LlacerBeliefStrategy,
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


def update_trust_pso(agent, was_audited, was_compliant):
    if not was_audited: return

    config = agent.model.config.trust_update
    traits = agent.traits

    if was_compliant:
        traits.perceived_service_orientation += config["pso_compliant_delta"]
    else:
        fairness = config["procedural_fairness"]
        traits.perceived_service_orientation += config["pso_caught_delta"] * (1 - fairness)

    traits.perceived_service_orientation = clip(traits.perceived_service_orientation, 1.0, 5.0)

    coefficient = config["pt_pso_coefficient"]
    traits.perceived_trustworthiness = coefficient * traits.perceived_service_orientation
    traits.perceived_trustworthiness = clip(traits.perceived_trustworthiness, 1.0, 5.0)

