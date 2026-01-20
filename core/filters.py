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
    tax_compliance_intention = (
        beta["PN"] * norm(traits.personal_norms) +
        beta["SN"] * norm(traits.social_norms) +
        beta["StN"] * norm(traits.societal_norms) +
        beta["PT"] * norm(traits.perceived_trustworthiness) +
        beta["PSO"] * norm(traits.perceived_service_orientation)
    )

    willingness_to_hide = max_concealable * (1 - tax_compliance_intention)
    return willingness_to_hide

def social_influence_filter(agent, willingness: float, max_concealable: float):
    if max_concealable <= 0: return 0.0
    
    own_rate = willingness / max_concealable
    
    if not agent.neighbors: return willingness
    
    neighbor_rates = [n.get_evasion_rate() for n in agent.neighbors if n.true_income > 0]
    if not neighbor_rates: return willingness
    
    omega = agent.model.social_influence
    median_rate = median(neighbor_rates)
    
    adjusted_rate = (1 - omega) * own_rate + omega * median_rate
    adjusted_rate = clip(adjusted_rate, 0.0, 1.0)
    
    return adjusted_rate * max_concealable

def rational_choice_filter(agent, willingness: float) -> float:
    if willingness <= 0.0: return 0.0

    p = agent.traits.subjective_audit_prob / 100.0
    f = agent.model.penalty_rate
    rho = agent.traits.risk_aversion

    if p >= 1.0: return 0.0
    if p <= 0.0: return willingness

    threshold = 1.0 / (1.0 + f)  # ASY threshold
    if p >= threshold: return 0.0

    margin = (threshold - p) / threshold
    rho_normalized = (rho - 0.5) / 4.5
    risk_dampening = 1.0 - (0.8 * rho_normalized)

    evasion_rate = margin * risk_dampening
    evasion_rate = clip(evasion_rate, 0.0, 1.0)
    return evasion_rate * willingness




