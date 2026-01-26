import numpy as np

from core.interventions.base import InterventionStrategy, register_intervention
from core.strategies import get_audit_strategy


@register_intervention("audit")
class AuditIntervention(InterventionStrategy):
    def select(self, agents: list, config: dict) -> list:
        rates = config["rate"]
        strategy_name = config["selection_strategy"]
        strategy = get_audit_strategy(strategy_name)
        
        private = [a for a in agents if a.occupation == "private"]
        business = [a for a in agents if a.occupation == "business"]
        
        selected_private = strategy.select(private, rates["private"])
        selected_business = strategy.select(business, rates["business"])
        
        return selected_private + selected_business
    
    def apply(self, agent, model, config: dict) -> dict:
        was_compliant = agent.is_compliant
        penalty = 0
        if not was_compliant:
            penalty = agent.evaded_income * model.tax_rate * model.penalty_rate
        
        outcome = {"compliant": was_compliant, "penalty": penalty}
        agent.interventions["audit"] = outcome
        
        probs = config["audit_type_probs"]
        audit_type = np.random.choice(
            ["administratief", "boekenonderzoek"],
            p=[probs["admin"], probs["books"]]
        )
        agent.update_audit_history(audit_type)
        
        return outcome
