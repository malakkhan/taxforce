import json
from pathlib import Path

DEFAULT_CONFIG_DIR = Path(__file__).parent / "configs" / "default"

def deep_merge(base, updates):
    for key, value in updates.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            deep_merge(base[key], value)
        else:
            base[key] = value
    return base

def load_config_dir(config_dir: Path) -> dict:
    merged = {}
    for json_file in sorted(config_dir.glob("*.json")):
        with open(json_file, "r") as f:
            merged.update(json.load(f))
    return merged


class SimulationConfig:
    def __init__(self, data: dict):
        self.config_data = data

    @classmethod
    def load_defaults(cls):
        return load_config_dir(DEFAULT_CONFIG_DIR)

    @classmethod
    def default(cls):
        return cls(cls.load_defaults())

    @classmethod
    def from_json(cls, path: str):
        defaults = cls.load_defaults()
        with open(path, "r") as f:
            custom = json.load(f)
        merged = deep_merge(defaults, custom)
        return cls(merged)

    def to_json(self, path: str):
        with open(path, "w") as f:
            json.dump(self.config_data, f, indent=2)

    @property
    def simulation(self):
        return self.config_data["simulation"]

    @property
    def enforcement(self):
        return self.config_data["enforcement"]

    @property
    def network(self):
        return self.config_data["network"]

    @property
    def belief_strategy(self):
        return self.config_data["belief_strategy"]

    @property
    def belief_strategies(self):
        return self.config_data["belief_strategies"]

    @property
    def social(self):
        return self.config_data["social"]

    @property
    def traits(self):
        return self.config_data["traits"]

    @property
    def filters(self):
        return self.config_data["filters"]

    @property
    def behaviors(self):
        return self.config_data["behaviors"]

    @property
    def norm_update(self):
        return self.config_data["norm_update"]

    @property
    def trust_update(self):
        return self.config_data["trust_update"]

    @property
    def private(self):
        return self.config_data["private"]

    @property
    def sme(self):
        return self.config_data["sme"]
