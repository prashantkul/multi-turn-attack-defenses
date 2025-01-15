import asyncio
import os
import json

from config.tca_config import TCAConfig
from dataset.dataset_manager import DatasetManager
from dotenv import load_dotenv, find_dotenv

class RiskCalculator:
    def __init__(self, alpha=0.5, beta=0.3, gamma=0.2):
        """
        Initialize the RiskCalculator with weights for historical, interaction, and pattern risks.

        Args:
            alpha (float): Weight for historical risk.
            beta (float): Weight for interaction risk.
            gamma (float): Weight for pattern risk.
        """
        self.historical_risk = 0  # Initialize historical risk as 0
        self.config = TCAConfig("config/config.yaml")
        self.pattern_weights = (
            self.config.risk.pattern_weights.to_dict()
        )  
        self.alpha = self.config.risk.weights.alpha
        self.beta = self.config.risk.weights.beta
        self.gamma = self.config.risk.weights.gamma

    def calculate_pattern_risk(self, patterns):
        """
        Calculate the risk score based on detected patterns.

        Args:
            patterns (dict): Patterns dictionary from the analysis response.

        Returns:
            int: Total pattern risk score.
        """
        print("\n" + "=" * 40)
        print("Pattern Risk Calculation:")
        print(f"Incoming patterns: {patterns}")
        print("-" * 40)

        risk_score = 0
        for pattern, details in patterns.items():
            detected = details.get("detected", False)
            weight = self.pattern_weights.get(pattern, 0)
            contribution = weight if detected else 0
            print(f"  Pattern: {pattern}")
            print(f"    Detected: {detected}")
            print(f"    Weight: {weight:.4f}")
            print(f"    Contribution to Risk: {contribution:.4f}")
            print("-" * 40)
            risk_score += contribution

        print(f"Total Pattern Risk Score: {risk_score:.4f}")
        print("=" * 40 + "\n")
        return risk_score

    def calculate_progressive_risk(self, historical_risk, interaction_risk, pattern_risk):
        """
        Calculate the progressive risk score for the current step.

        Args:
            interaction_risk (float): Risk level from the current interaction.
            pattern_risk (float): Risk score from detected patterns.

        Returns:
            float: The progressive risk score.
        """
        progressive_risk = (
            self.alpha * historical_risk
            + self.beta * interaction_risk
            + self.gamma * pattern_risk
        )
        self.historical_risk = progressive_risk  # Update historical risk
        # Print calculation details
        print("\n" + "=" * 40)
        print("Progressive Risk Calculation:")
        print("Progressive risk = α * Historical Risk + β * Interaction Risk + γ * Pattern Risk")
        print(f"The weights α: {self.alpha}, β: {self.beta}, γ: {self.gamma}")
        print(f"  Historical Risk (α * {historical_risk}): {self.alpha * historical_risk:.4f}")
        print(f"  Interaction Risk (β * {interaction_risk}): {self.beta * interaction_risk:.4f}")
        print(f"  Pattern Risk (γ * {pattern_risk}): {self.gamma * pattern_risk:.4f}")
        print(f"  Progressive Risk: {progressive_risk:.4f}")
        print("=" * 40 + "\n")
        return progressive_risk

    def reset_historical_risk(self):
        """
        Reset the historical risk to 0. Useful when starting a new analysis.
        """
        self.historical_risk = 0

    def __str__(self):
        """
        Return the current state of the RiskCalculator as a string.
        """
        return (
            f"RiskCalculator(alpha={self.alpha}, beta={self.beta}, gamma={self.gamma}, "
            f"historical_risk={self.historical_risk})"
        )
