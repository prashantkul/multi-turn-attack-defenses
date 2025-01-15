import yaml


class WeightConfig:
    def __init__(self):
        self.alpha = None
        self.beta = None
        self.gamma = None

    def load_from_dict(self, data: dict):
        self.alpha = data.get("alpha", 0.3)
        self.beta = data.get("beta", 0.5)
        self.gamma = data.get("gamma", 0.2)
        return self

    def validate_weights(self):
        total = self.alpha + self.beta + self.gamma
        if not 0.99 <= total <= 1.01:
            raise ValueError(
                f"Invalid weights: alpha={self.alpha}, beta={self.beta}, gamma={self.gamma}. "
                "The total must sum to 1."
            )

class PatternWeights:
    def __init__(self):
        self.language_change = None
        self.domain_shift = None
        self.time_sensitivity = None
        self.prohibited_content = None

    def load_from_dict(self, data: dict):
        self.language_change = data.get("language_change", 0.2)
        self.domain_shift = data.get("domain_shift", 0.3)
        self.time_sensitivity = data.get("time_sensitivity", 0.2)
        self.prohibited_content = data.get("prohibited_content", 0.3)
        return self

    def validate_weights(self):
        total = (
            self.language_change
            + self.domain_shift
            + self.time_sensitivity
            + self.prohibited_content
        )
        if not 0.99 <= total <= 1.01:
            raise ValueError(
                f"Invalid pattern weights: language_change={self.language_change}, "
                f"domain_shift={self.domain_shift}, time_sensitivity={self.time_sensitivity}, "
                f"prohibited_content={self.prohibited_content}. The total must sum to 1."
            )

    def to_dict(self):
        return {
            "language_change": self.language_change,
            "domain_shift": self.domain_shift,
            "time_sensitivity": self.time_sensitivity,
            "prohibited_content": self.prohibited_content,
        }


class RiskConfig:
    def __init__(self):
        self.weights = WeightConfig()
        self.pattern_weights = PatternWeights()
        self.warn_threshold = None
        self.block_threshold = None

    def load_from_dict(self, data: dict):
        self.weights.load_from_dict(data["weights"])
        self.pattern_weights.load_from_dict(data["pattern_weights"])
        self.warn_threshold = data.get("warn_threshold", 0.7)
        self.block_threshold = data.get("block_threshold", 0.9)
        return self

    def validate_weights(self):
        print("Validating weights...")
        self.weights.validate_weights()
        self.pattern_weights.validate_weights()
        print("Weights validation passed.")

    def log_config(self):
        print("Risk Configuration:")
        self.weights.log_config()
        print(f"  Pattern Weights: {self.pattern_weights.__dict__}")
        print(f"  Warn Threshold: {self.warn_threshold}")
        print(f"  Block Threshold: {self.block_threshold}")


class TCAConfig:
    def __init__(self, config_path: str):
        try:
            with open(config_path) as f:
                data = yaml.safe_load(f)
                self.risk = RiskConfig().load_from_dict(data["risk"])
                self.file_path = data["file_path"]
                self.log_level = data.get("log_level", "INFO")
                self.gcp_project_id = data.get("gcp_project_id", None)

            # Validate weights after loading
            self.risk.validate_weights()

        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing YAML file: {config_path}, Error: {e}")
        except ValueError as ve:
            raise ValueError(f"Validation error in configuration: {ve}")
