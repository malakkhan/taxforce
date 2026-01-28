import numpy as np
from .base_agent import BaseAgent, sample_clamped
from core.simcache import sim_cache


class SMEAgent(BaseAgent):
    def __init__(self, model):
        super().__init__(model, occupation="business")
        
        self.size_class = self.sample_size_class()
        self.turnover = self.sample_turnover()
        self.true_income = self.sample_income()
        self.declared_income = self.true_income
        self.sector, self.branch = self.sample_sector_branch()
        self.cash_intensity = self.sample_cash_intensity()
        self.digitalization = self.sample_digitalization()
        self.has_advisor = self.sample_advisor()
        self.audit_history = self.sample_audit_history()
        self.base_risk_score = self.calculate_base_risk()

        self.apply_sector_risk_aversion()

    @property
    def sme(self):
        return self.model.config.sme

    @property
    def group_key(self):
        return self.sector

    def sample_size_class(self):
        return np.random.choice(["Micro", "Small", "Medium"], p=self.sme["size_class_probs"])

    def sample_turnover(self):
        low, high = self.sme["turnover_ranges"][self.size_class]
        return float(np.random.uniform(low, high))

    def sample_income(self):
        margin = self.sme["profit_margin"]
        return self.turnover * np.random.uniform(margin["min"], margin["max"])

    def sample_sector_branch(self):
        sector_probs = self.sme["sector_probs"]
        sectors = list(sector_probs.keys())
        probs = list(sector_probs.values())
        total = sum(probs)
        probs = [p / total for p in probs]
        sector = np.random.choice(sectors, p=probs)
        
        sector_config = self.sme["sectors"][sector]
        branches = sector_config["branches"]
        branch = np.random.choice(branches) if branches else f"{sector}_Branch"
        return sector, branch

    def sample_cash_intensity(self):
        sector_config = self.sme["sectors"][self.sector]
        high_risk = sector_config["high_risk_branches"]
        if self.branch in high_risk: 
            return True
        return np.random.random() < sector_config["cash_prob"]

    def sample_digitalization(self):
        weights = self.sme["sectors"][self.sector]["digital_weights"]
        return np.random.choice(["Low", "Medium", "High"], p=weights)

    def sample_advisor(self):
        adv = self.sme["advisor_probs"]
        prob = adv["base"]
        if self.size_class != "Micro":
            prob += adv["size_bonus"]
        if self.digitalization == "High":
            prob += adv["digi_bonus"]
        return np.random.random() < min(prob, adv["max"])

    def sample_audit_history(self):
        return np.random.choice(
            ["geen", "administratief", "boekenonderzoek"],
            p=self.sme["audit_history_probs"]
        )

    def calculate_base_risk(self):
        sme = self.sme
        r = sme["base_risk_baseline"]
        
        sector_config = sme["sectors"][self.sector]
        if sector_config["risk"] == "high":
            r += sme["delta_sector_high_risk"]
        
        high_risk_branches = sector_config["high_risk_branches"]
        if self.branch in high_risk_branches:
            r += sme["delta_branch_high_risk"]
        
        size_deltas = {"Micro": sme["delta_size_micro"], "Medium": sme["delta_size_medium"]}
        r += size_deltas.get(self.size_class, 0)
        
        if self.cash_intensity:
            r += sme["delta_cash_intensive"]
        
        digi_deltas = {"High": sme["delta_digi_high"], "Low": sme["delta_digi_low"]}
        r += digi_deltas.get(self.digitalization, 0)
        
        r += sme["delta_advisor_yes"] if self.has_advisor else sme["delta_advisor_no"]
        
        hist_deltas = {"boekenonderzoek": sme["delta_audit_books"], "administratief": sme["delta_audit_admin"]}
        r += hist_deltas.get(self.audit_history, 0)
        
        return float(np.clip(r, 0.05, 0.90))

    @sim_cache
    def calculate_opportunity(self):
        opp = self.sme["opportunity"]
        phi = opp["base"]
        
        if self.cash_intensity:
            phi += opp["cash_bonus"]
        
        digi_adj = {"Low": opp["low_digi_bonus"], "High": -opp["high_digi_penalty"]}
        phi += digi_adj.get(self.digitalization, 0)
        
        if self.size_class == "Micro":
            phi += opp["micro_bonus"]
        elif self.size_class == "Medium":
            phi += opp["medium_penalty"]
        
        sector_config = self.sme["sectors"][self.sector]
        if sector_config["risk"] == "high":
            phi += opp["high_risk_sector_bonus"]
        
        return float(np.clip(phi, opp["min"], opp["max"]))

    def update_audit_history(self, audit_type):
        if audit_type in ["administratief", "boekenonderzoek"]:
            self.audit_history = audit_type
            self.base_risk_score = self.calculate_base_risk()

    def apply_sector_risk_aversion(self):
        sector_config = self.sme["sectors"][self.sector]
        if "risk_aversion" in sector_config:
            ra = sector_config["risk_aversion"]
            self.traits.risk_aversion = sample_clamped(
                ra["mean"], ra["std"], ra["min"], ra["max"]
            )
