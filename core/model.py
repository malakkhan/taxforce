import mesa
import numpy as np

from .agents import PrivateAgent, SMEAgent
from .network import build_network
from .strategies import get_audit_strategy
from .config import SimulationConfig
from .simcache import clear_all_caches
from .interventions import InterventionManager
from . import beliefs



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
        self.belief_strategy = beliefs.create_belief_strategy(config)

        self.create_agents()
        self.apply_boosts()
        self.network = build_network(list(self.agents), self.config)
        self.initialize_evasion_rates()

        self.current_step = 0
        self.intervened_this_step: dict = {}
        self.total_audits = 0  
        self.penalties_this_step = 0
        self.penalties_split_this_step = (0, 0) 

        
        self.intervention_manager = InterventionManager(config.config_data)

        self.datacollector = mesa.DataCollector(
            model_reporters={
                "Tax_Gap": lambda m: m.calc_tax_gap(),
                "Compliance_Rate": lambda m: m.calc_compliance_rate(),
                "Total_Taxes": lambda m: m.calc_total_taxes(),
                "Audits": lambda m: m.calc_audits_split(),
                "Avg_Declaration_Ratio": lambda m: m.calc_avg_declaration_ratio(),
                "Tax_Morale": lambda m: m.calc_tax_morale(),
                "Avg_FOUR": lambda m: m.calc_avg_four(),
                "Avg_PSO": lambda m: m.calc_avg_pso(),
                "MGTR": lambda m: m.calc_mgtr(),
                "Penalties": lambda m: m.calc_penalties_split(),
                "MKB_Total_Gap": lambda m: m.calc_mkb_total_gap(),
                "MKB_Error_Gap": lambda m: m.calc_mkb_error_gap(),
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
            t.pso = np.clip(t.pso + pso_boost, 1, 5)
            t.p_trust = np.clip(t.p_trust + trust_boost, 1, 5)

    def initialize_evasion_rates(self):
        for agent in self.agents:
            declared = agent.behavior.decide(agent, initial_step=True)
            evasion = agent.true_income - declared
            
            opportunity = agent.calculate_opportunity() * agent.true_income
            if opportunity > 0:
                agent.prev_evasion_rate = np.clip(evasion / opportunity, 0.0, 1.0)
            else:
                agent.prev_evasion_rate = 0.0

    def step(self):
        self.current_step += 1
        
        for agent in self.agents:
            agent.prev_evasion_rate = agent.get_evasion_rate()
        
        self.agents.shuffle_do("step")
        self.run_interventions()
        self.update_norms()
        self.datacollector.collect(self)
        clear_all_caches()

    def run_interventions(self):
        agents_list = list(self.agents)
        self.intervention_manager.reset_agents(agents_list)
        results = self.intervention_manager.run_all(self)
        
        self.intervened_this_step = {
            name: {a.unique_id for a in data["agents"]} 
            for name, data in results.items()
        }

        self.penalties_this_step = sum(
            o.get("penalty", 0) 
            for data in results.values() 
            for o in data["outcomes"]
        )
        
        priv_p = 0
        biz_p = 0
        
        for data in results.values():
            agents = data["agents"]
            outcomes = data["outcomes"]
            for i, outcome in enumerate(outcomes):
                if i < len(agents):
                    agent = agents[i]
                    penalty = outcome.get("penalty", 0)
                    if penalty > 0:
                        if agent.occupation == 'private': 
                            priv_p += penalty
                        else: 
                            biz_p += penalty
        
        self.penalties_split_this_step = (priv_p, biz_p)

    def update_norms(self):
        agents_list = list(self.agents)
        n_agents = len(agents_list)

        interaction_sets = {}
        for agent in agents_list:
            if agent.neighbors:
                mask = np.random.random(len(agent.neighbors)) < 0.5
                interating_neighbors = [n for n, m in zip(agent.neighbors, mask) if m]
                interaction_sets[agent.unique_id] = interating_neighbors
            else:
                interaction_sets[agent.unique_id] = []

        compliance_scores = {a.unique_id: beliefs.compute_compliance_score(a) for a in agents_list}
        societal_raw = sum(compliance_scores.values())
        
        audited_agents = self.intervened_this_step.get("audit", set())
        
        context = beliefs.UpdateContext(
            interaction_sets=interaction_sets,
            compliance_scores=compliance_scores,
            societal_compliance=societal_raw,
            audited_agents=audited_agents,
            n_agents=n_agents
        )
        
        self.belief_strategy.update_all(agents_list, context)

    def calc_tax_gap(self):
        priv_gap = sum(a.evaded_income * self.tax_rate for a in self.agents if a.occupation == 'private')
        biz_gap = sum(a.evaded_income * self.tax_rate for a in self.agents if a.occupation == 'business')
        return (priv_gap, biz_gap)

    def calc_compliance_rate(self):
        priv_agents = [a for a in self.agents if a.occupation == 'private']
        biz_agents = [a for a in self.agents if a.occupation == 'business']
        
        priv_compliance = sum(1 for a in priv_agents if a.is_compliant) / len(priv_agents) if priv_agents else 0.0
        biz_compliance = sum(1 for a in biz_agents if a.is_compliant) / len(biz_agents) if biz_agents else 0.0
        
        return (priv_compliance, biz_compliance)

    def calc_total_taxes(self):
        priv_tax = sum(a.declared_income * self.tax_rate for a in self.agents if a.occupation == 'private')
        biz_tax = sum(a.declared_income * self.tax_rate for a in self.agents if a.occupation == 'business')
        return (priv_tax, biz_tax)

    def calc_avg_declaration_ratio(self):
        priv_agents = [a for a in self.agents if a.occupation == 'private']
        biz_agents = [a for a in self.agents if a.occupation == 'business']
        
        def avg_ratio(agents):
            if not agents: return 1.0
            ratios = [min(a.declared_income / max(a.true_income, 1), 1.0) for a in agents]
            return sum(ratios) / len(agents)

        return (avg_ratio(priv_agents), avg_ratio(biz_agents))

    def calc_tax_morale(self):
        agents = list(self.agents)
        if not agents: return 0.0
        
        total = 0.0
        for agent in agents:
            t = agent.traits
            norm = lambda val: (val - 1) / 4
            
            morale = (
                0.18 * norm(t.social_norms) +   
                0.23 * norm(t.societal_norms) +  
                0.27 * norm(t.pso) + 
                0.32 * norm(t.p_trust)
            )
            total += morale
        
        priv_morale = []
        biz_morale = []
        
        for agent in agents:
            t = agent.traits
            norm = lambda val: (val - 1) / 4
            morale = (
                0.18 * norm(t.social_norms) +   
                0.23 * norm(t.societal_norms) +  
                0.27 * norm(t.pso) + 
                0.32 * norm(t.p_trust)
            ) * 100
            
            if agent.occupation == 'private':
                priv_morale.append(morale)
            else:
                biz_morale.append(morale)
                
        avg_priv = sum(priv_morale) / len(priv_morale) if priv_morale else 0.0
        avg_biz = sum(biz_morale) / len(biz_morale) if biz_morale else 0.0
        
        return (avg_priv, avg_biz)

    def calc_avg_four(self):
        priv_rates = []
        biz_rates = []
        
        for a in self.agents:
            if a.behavior_type != "honest":
                opportunity = a.calculate_opportunity()
                if opportunity > 0:
                    rate = a.get_evasion_rate()
                    if a.occupation == 'private':
                        priv_rates.append(rate)
                    else:
                        biz_rates.append(rate)
                        
        avg_priv = sum(priv_rates) / len(priv_rates) if priv_rates else 0.0
        avg_biz = sum(biz_rates) / len(biz_rates) if biz_rates else 0.0
        return (avg_priv, avg_biz)

    def calc_avg_pso(self):
        agents = list(self.agents)
        if not agents: return 0.0
        return sum(a.traits.pso for a in agents) / len(agents)

    def calc_mgtr(self):
        total_true = sum(a.true_income for a in self.agents)
        if total_true <= 0: return 0.0
        revenue = sum(a.declared_income * self.tax_rate for a in self.agents)
        return (revenue + self.penalties_this_step) / total_true


    def calc_mkb_total_gap(self):
        sme_agents = [a for a in self.agents if a.occupation == 'business']
        if not sme_agents: return 0.0
        return sum(a.evaded_income * self.tax_rate for a in sme_agents)

    def calc_mkb_error_gap(self):
        sme_agents = [a for a in self.agents if a.occupation == 'business']
        if not sme_agents: return 0.0
        return sum(a.error_amount * self.tax_rate for a in sme_agents)

    def calc_audits_split(self):
        audited_ids = self.intervened_this_step.get("audit", set())
        priv_audits = 0
        biz_audits = 0
        for aid in audited_ids:
            agent = next((a for a in self.agents if a.unique_id == aid), None)
            if agent:
                 if agent.occupation == 'private': priv_audits += 1
                 else: biz_audits += 1
        return (priv_audits, biz_audits)

    def calc_penalties_split(self):
        return self.penalties_split_this_step if hasattr(self, 'penalties_split_this_step') else (0, 0)


    def run(self, steps: int = None):
        n = steps or self.n_steps
        for _ in range(n):
            self.step()