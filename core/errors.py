import numpy as np


def calculate_error_probability(agent, config: dict) -> float:
    error_cfg = config["error_model"]
    
    if agent.occupation == "private":
        base = error_cfg["private"]["base"]
    else:
        base = error_cfg["business"]["base"]
        
        if agent.digitalization == "Low":
            base += error_cfg["business"]["digi_low_bonus"]
        elif agent.digitalization == "High":
            base -= error_cfg["business"]["digi_high_reduction"]
        
        if agent.cash_intensity:
            base += error_cfg["business"]["cash_bonus"]
        
        if agent.has_advisor:
            base -= error_cfg["business"]["advisor_reduction"]
        
        if agent.size_class == "Micro":
            base += error_cfg["business"]["micro_bonus"]
        
        sector_cfg = agent.model.config.sme["sectors"][agent.sector]
        if sector_cfg["risk"] == "high":
            base += error_cfg["business"]["high_risk_bonus"]
    
    pso_norm = (agent.traits.pso - 1) / 4
    pso_reduction = error_cfg["pso_reduction_factor"] * pso_norm
    base *= (1 - pso_reduction)
    
    trust_norm = (agent.traits.p_trust - 1) / 4
    trust_reduction = error_cfg["trust_reduction_factor"] * trust_norm
    base *= (1 - trust_reduction)
    
    norms_norm = (agent.traits.personal_norms - 1) / 4
    norms_reduction = error_cfg["norms_reduction_factor"] * norms_norm
    base *= (1 - norms_reduction)
    
    min_prob = error_cfg["min_probability"]
    max_prob = error_cfg["max_probability"]
    
    return max(min_prob, min(max_prob, base))


def calculate_error_amount(agent, config: dict) -> float:
    error_cfg = config["error_model"]
    magnitude_cfg = error_cfg["magnitude"]
    
    magnitude = np.random.uniform(magnitude_cfg["min"], magnitude_cfg["max"])
    
    under_report_prob = error_cfg["under_report_prob"]
    direction = 1 if np.random.random() < under_report_prob else -1
    
    return agent.true_income * magnitude * direction


def apply_error(agent, config: dict) -> tuple:
    error_cfg = config["error_model"]
    
    if not error_cfg["enabled"]:
        return agent.true_income, False, 0.0
    
    error_prob = calculate_error_probability(agent, config)
    
    if np.random.random() >= error_prob:
        return agent.true_income, False, 0.0
    
    error_amount = calculate_error_amount(agent, config)
    declared = agent.true_income - error_amount
    declared = max(0.0, declared)
    
    return declared, True, error_amount
