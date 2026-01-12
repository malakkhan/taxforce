import mesa
import random
import numpy as np

class SMEAgent(mesa.Agent):
    """
    An agent representing a Micro, Small or Medium Enterprise (SME).
    """
    def __init__(self, model, sme_category):
        super().__init__(model)
        # 1. Structural Attributes 
        self.category = sme_category  # Micro, Small, or Medium; initialized in the TaxComplianceModel class
        self.legal_form = random.choice(["Sole Proprietorship", "BV"]) # 
        self.digitalization = random.choice(["Low", "Medium", "High"]) # 
        self.has_advisor = random.random() < 0.4 # Fiscal Advisor (F) 
        
        # 2. Financial Variables 
        # True taxable profit (W) before tax
        self.true_profit = random.uniform(20000, 100000) 
        self.declared_profit = 0 # (X) The primary behavioral output
        
        # 3. Behavioral & Psychological State 
        self.tax_morale = random.uniform(1, 5) # Intrinsic motivation (chi)
        self.trust_in_authorities = random.uniform(0.5, 1.0) # Belief in benevolence
        self.subjective_audit_prob = model.audit_rate # Perceived risk (p_e)
        
    def step(self):
        """
        Decision logic based on the 'Slippery Slope' framework.
        Combines Rational Choice and Normative Filters.
        """
        ### Social Influence Filter ###
        # Agents blend their morale with neighbors (Network Topology impact) 
        neighbors = self.model.grid.get_neighbors(self.pos, moore=True, include_center=False)
        if neighbors:
            avg_neighbor_morale = np.mean([n.tax_morale for n in neighbors])
            # Social influence weight (w) 
            self.tax_morale = (self.tax_morale + avg_neighbor_morale * self.model.social_influence) / (1 + self.model.social_influence)

        ### Opportunity Matrix ###
        # Max % of income concealable per category 
        # Micro firms often have higher cash intensity (K) 
        opportunity_rate = 0.8 if self.category == "Micro" else 0.3
        
        ### Decision Logic ###
        # If Trust and Morale are high, compliance is voluntary (Synergistic climate) 
        if self.tax_morale > 4.2 and self.trust_in_authorities > 0.8:
            self.declared_profit = self.true_profit
        else:
            # Rational Choice Filter: Weighing gain vs risk of Penalty Rate 
            expected_penalty = self.subjective_audit_prob * self.model.penalty_rate
            if expected_penalty < 0.2: # Low deterrence threshold
                evasion_perc = opportunity_rate * (1 - expected_penalty)
                self.declared_profit = self.true_profit * (1 - evasion_perc)
            else:
                self.declared_profit = self.true_profit
