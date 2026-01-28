from abc import ABC, abstractmethod

INTERVENTION_REGISTRY = {}

def register_intervention(name: str):
    def decorator(cls):
        INTERVENTION_REGISTRY[name] = cls
        cls.name = name
        return cls
    return decorator

class InterventionStrategy(ABC):
    name: str
    
    @abstractmethod
    def select(self, agents: list, config: dict) -> list:
        pass
    
    @abstractmethod
    def apply(self, agent, model, config: dict) -> dict:
        pass

class InterventionManager:
    def __init__(self, config: dict):
        self.active = []
        interventions_cfg = config["interventions"]
        for name, cls in INTERVENTION_REGISTRY.items():
            cfg = interventions_cfg.get(name)
            if cfg and cfg["enabled"]:
                self.active.append((cls(), cfg))
    
    def reset_agents(self, agents):
        registered = list(INTERVENTION_REGISTRY.keys())
        reset_interventions = {name: None for name in registered}
        for agent in agents:
            agent.interventions = reset_interventions.copy()
    
    def run_all(self, model):
        results = {}
        for intervention, cfg in self.active:
            selected = intervention.select(list(model.agents), cfg)
            outcomes = []
            for agent in selected:
                outcome = intervention.apply(agent, model, cfg)
                outcomes.append(outcome)
            results[intervention.name] = {"agents": selected, "outcomes": outcomes}
        return results

