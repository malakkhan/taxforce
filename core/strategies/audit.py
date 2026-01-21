from abc import ABC, abstractmethod
import numpy as np


class AuditStrategy(ABC):
    @abstractmethod
    def select(self, agents: list, rate: float) -> list:
        pass


class RandomAudit(AuditStrategy):
    def select(self, agents: list, rate: float):
        n_audits = max(1, int(len(agents) * rate))
        if n_audits >= len(agents):
            return agents
        indices = np.random.choice(len(agents), size=n_audits, replace=False)
        return [agents[i] for i in indices]


class RiskBasedAudit(AuditStrategy):
    def select(self, agents: list, rate: float):
        n_audits = max(1, int(len(agents) * rate))

        private = [a for a in agents if a.occupation == "private"]
        business = [a for a in agents if a.occupation == "business"]

        n_private = int(n_audits * len(private) / len(agents)) if agents else 0
        n_business = n_audits - n_private

        selected = []

        if private and n_private > 0:
            indices = np.random.choice(len(private), size=min(n_private, len(private)), replace=False)
            selected.extend([private[i] for i in indices])

        if business and n_business > 0:
            sorted_business = sorted(business, key=lambda a: a.base_risk_score, reverse=True)
            selected.extend(sorted_business[:n_business])

        return selected


class NetworkAudit(AuditStrategy):
    def select(self, agents: list, rate: float):
        n_audits = max(1, int(len(agents) * rate))
        sorted_agents = sorted(agents, key=lambda a: a.closeness_centrality, reverse=True)
        return sorted_agents[:n_audits]


AUDIT_STRATEGIES = {
    "random": RandomAudit,
    "risk": RiskBasedAudit,
    "network": NetworkAudit,
}


def get_audit_strategy(name: str):
    if name not in AUDIT_STRATEGIES:
        raise ValueError(f"Unknown audit strategy: {name}. Options: {list(AUDIT_STRATEGIES.keys())}")
    return AUDIT_STRATEGIES[name]()
