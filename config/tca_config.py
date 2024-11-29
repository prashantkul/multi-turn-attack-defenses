import yaml


class WeightConfig:

    def __init__(self):
        self.alpha = None
        self.beta = None
        self.gamma = None

    def load_from_dict(self, data: dict):
        self.alpha = data["alpha"]
        self.beta = data["beta"]
        self.gamma = data["gamma"]
        return self


class PatternWeights:

    def __init__(self):
        self.language = None
        self.domain = None
        self.time_sensitivity = None
        self.prohibited_content = None

    def load_from_dict(self, data: dict):
        self.language = data["language"]
        self.domain = data["domain"]
        self.time_sensitivity = data["time_sensitivity"]
        self.prohibited_content = data["prohibited_content"]
        return self


class RiskConfig:

    def __init__(self):
        self.weights = WeightConfig()
        self.pattern_weights = PatternWeights()
        self.warn_threshold = None
        self.block_threshold = None

    def load_from_dict(self, data: dict):
        self.weights.load_from_dict(data["weights"])
        self.pattern_weights.load_from_dict(data["pattern_weights"])
        self.warn_threshold = data["warn_threshold"]
        self.block_threshold = data["block_threshold"]
        return self


class TCAConfig:

    def __init__(self, config_path: str):
        with open(config_path) as f:
            data = yaml.safe_load(f)
            self.risk = RiskConfig().load_from_dict(data["risk"])
            self.file_path = data["file_path"]
            self.log_level = data.get("log_level", "INFO")
            self.gcp_project_id = data.get("gcp_project_id", None)


# Usage
# config = TCAConfig("config/config.yaml")
