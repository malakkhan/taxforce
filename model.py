import mesa
import numpy as np
from agents import SMEAgent

class TaxComplianceModel(mesa.Model):
    """
    The global simulation environment.
    Defines policy interventions and structural constraints.
    """    
    def __init__(self,  N=100, audit_rate=0.07, penalty_rate=3.0, social_influence=0.5):
        super().__init__()
        self.num_agents = N
        self.grid = mesa.space.MultiGrid(20, 20, True) # Height, width and torus behavior -> Simple torus grid as network topology right now, will likely change
        
        # Global Parameters (G)
        self.audit_rate = audit_rate # Probability of audit (p_a)
        self.penalty_rate = penalty_rate # Rate of fine
        self.social_influence = social_influence # Strength of peer influence (w)
        
        # Initialize Agents
        for i in range(self.num_agents):
            # SME Category distribution based on Synthetic Dataset Methodology 
            cat = random.choices(["Micro", "Small", "Medium"], weights=[0.7, 0.2, 0.1])[0]
            a = SMEAgent(self, cat)
            
            # Place agent on the grid (representing the Network Topology) 
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x, y))

        # Output Metrics (O) for Dashboard
        self.datacollector = mesa.DataCollector(
            model_reporters={
                "Tax Gap": lambda m: sum([a.true_profit - a.declared_profit for a in m.agents]),
                "Compliance Rate": lambda m: sum([1 for a in m.agents if a.declared_profit >= a.true_profit]) / m.num_agents,
                "Avg Tax Morale": lambda m: np.mean([a.tax_morale for a in m.agents])
            }
        )

    def step(self):
        """
        Executes one simulation round (one tax year).
        """
        # 1. Enforcement Phase (Audit Strategy) 
        num_audits = int(self.audit_rate * self.num_agents)
        audited_agents = self.random.sample(list(self.agents), num_audits)
        
        for agent in audited_agents:
            if agent.declared_profit < agent.true_profit:
                # Target effect: Perceived risk increases after being caught 
                agent.subjective_audit_prob = min(1.0, agent.subjective_audit_prob * 1.2)
                # Intrinsic morale might drop if penalty feels unfair 
                agent.tax_morale *= 0.95
            else:
                # Bomb-crater effect: Perceived risk decreases after 'clean' audit 
                agent.subjective_audit_prob *= 0.9
        
        # 2. Advance all agents and collect data 
        self.agents.shuffle_do("step")
        self.datacollector.collect(self)