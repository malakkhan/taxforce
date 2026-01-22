import mesa
import numpy as np
from abc import abstractmethod
from dataclasses import dataclass

from core.behaviors import assign_behavior
from core.simcache import sim_cache

@dataclass
class AgentTraits:
    personal_norms: float
    subjective_audit_prob: float
    perceived_service_orientation: float
    perceived_trustworthiness: float
    social_norms: float
    societal_norms: float
    risk_aversion: float

def sample_clamped(mean, std, low, high):
    sampled = np.random.normal(mean, std)
    clipped = np.clip(sampled, low, high)
    return float(clipped)

def sample_trait(trait_params, name):
    p = trait_params[name]
    return sample_clamped(p["mean"], p["std"], p["min"], p["max"])

def create_traits(occupation, config):
    trait_params = config.traits[occupation]
    traits = list(AgentTraits.__dataclass_fields__.keys())
    trait_values = {t: sample_trait(trait_params, t) for t in traits}
    return AgentTraits(**trait_values)

class BaseAgent(mesa.Agent):
    def __init__(self, model, occupation):
        super().__init__(model)
        self.occupation = occupation
        self.behavior = assign_behavior(model.config, occupation)
        self.traits = create_traits(occupation, model.config)
        
        self.true_income = 0.0
        self.declared_income = 0.0
        self.neighbors = []
        self.neighbor_ids = []
        self.interventions = {}
        self.prev_evasion_rate = 0.0
    
    @abstractmethod
    def calculate_opportunity(self):
        pass

    @property
    def behavior_type(self):
        return self.behavior.__class__.__name__.replace("Behavior", "").lower()

    @property
    @abstractmethod
    def group_key(self) -> str:
        pass
    
    @property
    def evaded_income(self):
        return self.true_income - self.declared_income
    
    @property
    def is_compliant(self):
        return self.declared_income >= self.true_income - 0.01 # small tolerance for floating point issues
    
    # @sim_cache
    def get_evasion_rate(self):
        max_evadable = self.calculate_opportunity() * self.true_income
        if max_evadable <= 0: return 0.0
        rate = self.evaded_income / max_evadable
        return max(0.0, min(1.0, rate))
    
    def step(self):
        self.declared_income = self.behavior.decide(self)
