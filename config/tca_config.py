@dataclass
class WeightConfig:
    alpha: float
    beta: float
    gamma: float

    def __post_init__(self):
        if not (0.2 <= self.alpha <= 0.4):
            raise ValueError("Alpha must be between 0.2 and 0.4")
        if not (0.4 <= self.beta <= 0.6):
            raise ValueError("Beta must be between 0.4 and 0.6")
        if not (0.1 <= self.gamma <= 0.3):
            raise ValueError("Gamma must be between 0.1 and 0.3")
        if not abs(self.alpha + self.beta + self.gamma - 1.0) < 1e-6:
            raise ValueError("Weights must sum to 1.0")


@dataclass
class PatternWeights:
    language: float
    domain: float
    time_sensitivity: float
    prohibited_content: float

    def __post_init__(self):
        weights_sum = sum(
            (self.language, self.domain, self.time_sensitivity, self.prohibited_content)
        )
        if not abs(weights_sum - 1.0) < 1e-6:
            raise ValueError("Pattern weights must sum to 1.0")


@dataclass
class RiskConfig:
    weights: WeightConfig
    pattern_weights: PatternWeights
    warn_threshold: float = 0.7
    block_threshold: float = 0.9


@dataclass
class TCAConfig:
    risk: RiskConfig
    log_level: str = "INFO"
