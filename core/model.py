import mesa
import numpy as np

from .agents import PrivateAgent, SMEAgent
from .network import build_network
from .strategies import get_audit_strategy
from .config import SimulationConfig
from .simcache import clear_all_caches
from . import updaters


class TaxComplianceModel(mesa.Model):
    def __init__(self, config: SimulationConfig = None, seed: int = None):
        super().__init__()
        np.random.seed(seed)

        config = config or SimulationConfig.default()

        self.config = config
        self.n_agents = config.simulation["n_agents"]
        self.n_steps = config.simulation["n_steps"]
        self.penalty_rate = config.enforcement["penalty_rate"]
        self.tax_rate = config.enforcement["tax_rate"]
        self.social_influence = config.social["social_influence"]

        self.audit_strategy = get_audit_strategy(config.enforcement["audit_strategy"])
        self.belief_strategy = updaters.create_belief_strategy(config)

        self.create_agents()
        self.apply_boosts()
        self.network = build_network(list(self.agents), self.config)

        self.current_step = 0
        self.audited_this_step: set[int] = set()
        self.total_audits = 0  # Track cumulative audits

        self.datacollector = mesa.DataCollector(
            model_reporters={
                "Tax_Gap": lambda m: m.calc_tax_gap(),
                "Compliance_Rate": lambda m: m.calc_compliance_rate(),
                "Total_Taxes": lambda m: m.calc_total_taxes(),
                "Audits": lambda m: len(m.audited_this_step),
                "Avg_Declaration_Ratio": lambda m: m.calc_avg_declaration_ratio(),
            }
        )

    def create_agents(self):
        business_ratio = self.config.simulation["business_ratio"]
        n_business = int(self.n_agents * business_ratio)
        n_private = self.n_agents - n_business

        for _ in range(n_private): PrivateAgent(self)
        for _ in range(n_business): SMEAgent(self)

    def apply_boosts(self):
        pso_boost = self.config.social["pso_boost"]
        trust_boost = self.config.social["trust_boost"]

        for agent in self.agents:
            t = agent.traits
            t.perceived_service_orientation = np.clip(t.perceived_service_orientation + pso_boost, 1, 5)
            t.perceived_trustworthiness = np.clip(t.perceived_trustworthiness + trust_boost, 1, 5)

    def step(self):
        self.current_step += 1
        self.agents.shuffle_do("step")
        self.run_audits()
        self.update_norms()
        self.datacollector.collect(self)
        clear_all_caches()

    def run_audits(self):
        agents_list = list(self.agents)
        private = [a for a in agents_list if a.occupation == "private"]
        business = [a for a in agents_list if a.occupation == "business"]
        
        # Apply occupation-specific audit rates
        rates = self.config.enforcement["audit_rate"]
        selected = []
        selected.extend(self.audit_strategy.select(private, rates["private"]))
        selected.extend(self.audit_strategy.select(business, rates["business"]))
        
        self.audited_this_step = {a.unique_id for a in selected}

        for agent in selected:
            was_compliant = agent.is_compliant
            self.belief_strategy.update(
                agent,
                was_audited=True,
                was_caught=not was_compliant,
                audited_neighbors=[]
            )
            updaters.update_trust_pso(agent, was_audited=True, was_compliant=was_compliant)

            if hasattr(agent, "update_audit_history"):
                probs = self.config.enforcement["audit_type_probs"]
                audit_type = np.random.choice(
                    ["administratief", "boekenonderzoek"],
                    p=[probs["admin"], probs["books"]]
                )
                agent.update_audit_history(audit_type)

    def update_norms(self):
        agents_list = list(self.agents)
        n_agents = len(agents_list)

        interaction_sets = {}
        for agent in agents_list:
            if agent.neighbors:
                mask = np.random.random(len(agent.neighbors)) < 0.5
                interaction_sets[agent.unique_id] = [n for n, m in zip(agent.neighbors, mask) if m]
            else:
                interaction_sets[agent.unique_id] = []

        for agent in agents_list:
            if agent.unique_id not in self.audited_this_step:
                interacting = interaction_sets[agent.unique_id]
                audited_interacting = [n for n in interacting if n.unique_id in self.audited_this_step]
                self.belief_strategy.update(
                    agent,
                    was_audited=False,
                    was_caught=False,
                    audited_neighbors=audited_interacting
                )

        compliance_scores = {a.unique_id: updaters.compute_compliance_score(a) for a in agents_list}
        
        agent_raw_scores = {}
        for agent in agents_list:
            interacting = interaction_sets[agent.unique_id]
            if interacting:
                raw = sum(compliance_scores[n.unique_id] for n in interacting) / len(interacting)
                agent_raw_scores[agent.unique_id] = raw
        
        societal_raw = sum(compliance_scores.values())

        for agent in agents_list:
            raw_score = agent_raw_scores.get(agent.unique_id)
            updaters.update_social_norms(agent, raw_score)
            updaters.update_societal_norms(agent, societal_raw, n_agents)

    def calc_tax_gap(self):
        return sum(a.evaded_income * self.tax_rate for a in self.agents)

    def calc_compliance_rate(self):
        agents = list(self.agents)
        if not agents: return 0.0
        return sum(1 for a in agents if a.is_compliant) / len(agents)

    def calc_total_taxes(self):
        return sum(a.declared_income * self.tax_rate for a in self.agents)

    def calc_avg_declaration_ratio(self):
        """Calculate average declaration ratio (declared/true income)."""
        agents = list(self.agents)
        if not agents:
            return 1.0
        ratios = [min(a.declared_income / max(a.true_income, 1), 1.0) for a in agents]
        return sum(ratios) / len(agents)

    def run(self, steps: int = None):
        n = steps or self.n_steps
        for _ in range(n):
            self.step()