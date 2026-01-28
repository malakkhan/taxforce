import numpy as np
from statistics import median


def clip(value, low, high):
    return max(low, min(high, value))


def opportunity_filter(agent):
    phi = agent.calculate_opportunity()
    return agent.true_income * phi


def normative_filter(agent, max_concealable: float):
    occupation = agent.occupation
    beta = agent.model.config.filters["beta"][occupation]
    traits = agent.traits

    norm = lambda val: (val - 1) / 4
    
    contribs = {
        "PN": beta["PN"] * norm(traits.personal_norms),
        "SN": beta["SN"] * norm(traits.social_norms),
        "StN": beta["StN"] * norm(traits.societal_norms),
        "PT": beta["PT"] * norm(traits.p_trust),
        "PSO": beta["PSO"] * norm(traits.pso)
    }
    
    beta_sum = sum(beta.values())
    raw_tci = sum(contribs.values())
    tax_compliance_intention = raw_tci / beta_sum if beta_sum > 0 else raw_tci
    tax_compliance_intention = max(0.0, min(1.0, tax_compliance_intention))
    
    tci_weight = agent.model.config.filters["tci_weight"][agent.behavior_type]
    
    return max_concealable * (1 - tci_weight * tax_compliance_intention)


def social_influence_filter(agent, willingness: float, max_concealable: float):
    if max_concealable <= 0: 
        return 0.0
    
    own_rate = willingness / max_concealable
    
    if not agent.neighbors: 
        return willingness
    
    neighbor_rates = [n.prev_evasion_rate for n in agent.neighbors if n.true_income > 0]
    
    if not neighbor_rates: 
        return willingness
    
    omega = agent.model.social_influence
    median_rate = median(neighbor_rates)
    
    adjusted_rate = (1 - omega) * own_rate + omega * median_rate
    adjusted_rate = clip(adjusted_rate, 0.0, 1.0)
    
    return adjusted_rate * max_concealable


def rational_choice_filter(agent, willingness: float) -> float:
    if willingness <= 0.0: return 0.0

    p_permanent = agent.traits.subjective_audit_prob
    p_temporary = agent.temporary_audit_boost
    p_raw = p_permanent + p_temporary
    p = p_raw / 100.0
    f = agent.model.penalty_rate
    rho = agent.traits.risk_aversion
    threshold = 1.0 / (1.0 + f)

    if p >= threshold: evasion_rate = 0.0
    elif p <= 0.0: evasion_rate = 1.0
    else:
        margin = (threshold - p) / threshold
        
        if margin < 0.2:
            rho_normalized = (rho - 0.5) / 4.5
            deterrence_chance = (0.2 - margin) * rho_normalized
            if deterrence_chance > 0.3:
                evasion_rate = 0.0
            else:
                evasion_rate = 1.0
        else:
            evasion_rate = 1.0

    return evasion_rate * willingness



