import numpy as np
from .base_agent import BaseAgent

class PrivateAgent(BaseAgent):
    def __init__(self, model):
        super().__init__(model, occupation="private")
        self.true_income = self.sample_income()

    def sample_income(self):
        income_cfg = self.model.config.private["income"]
        mu = income_cfg["mean"]
        sigma = income_cfg["std"]
        
        variance = sigma ** 2
        mu_log = np.log(mu ** 2 / np.sqrt(variance + mu ** 2))
        sigma_log = np.sqrt(np.log(1 + variance / mu ** 2))
        
        return float(np.random.lognormal(mu_log, sigma_log))

    def calculate_opportunity(self):
        return 0.10

    @property
    def group_key(self):
        return "private"
