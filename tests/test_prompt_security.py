import asyncio
import os
import json

from prompts.prompt_templates import PromptManager
from llms.llm_manager import LLMManager
from tca.risk_calculator import RiskCalculator
from config.tca_config import TCAConfig
from dataset.dataset_manager import DatasetManager
from dotenv import load_dotenv, find_dotenv
from tca.security_engine import SecurityDecisionEngine


class ConversationAnalyzer:
    def __init__(self, config_path, llm_type="gpt"):
        load_dotenv(find_dotenv())
        self.config = TCAConfig(config_path)
        self.llm_type = llm_type  # Store the LLM type
        self.prompt_manager = PromptManager()
        self.llm_manager = LLMManager(prompt_manager=self.prompt_manager)
        self.dataset_manager = DatasetManager(self.config)
        self.risk_calculator = RiskCalculator()
        self.decision_engine = SecurityDecisionEngine()
        self.historical_risk = 0  # Initialize historical risk

    def clean_and_parse_content(self, content):
        """
        Cleans Markdown formatting and parses the content field as JSON.
        """
        try:
            cleaned_content = (
                content.strip("`").replace("```json", "").replace("```", "").strip()
            )
            return json.loads(cleaned_content)
        except Exception as e:
            raise ValueError(f"Could not parse content as JSON. Error: {e}")

    async def analyze_row(self, idx, row):
        conversation_pairs = self.dataset_manager.extract_conversation_pairs(row)
        print(
            f"******** Total conversation pairs in row {idx + 1}: {len(conversation_pairs)} *********"
        )

        if not conversation_pairs or len(conversation_pairs) < 2:
            print(f"Not enough pairs to analyze for row {idx + 1}. Skipping.")
            return

        self.historical_risk = 0  # Reset historical risk for each row

        for i in range(1, len(conversation_pairs)):
            prev_pair = conversation_pairs[i - 1]
            current_pair = conversation_pairs[i]

            if not self.validate_pairs(prev_pair, current_pair):
                continue

            try:
                response = await self.llm_manager.analyze_conversation(
                    self.llm_type, prev_pair, current_pair
                )
                self.process_response(response, idx, i, prev_pair, current_pair)
            except Exception as e:
                print(
                    f"Error analyzing conversation pair {i}: prev_pair={prev_pair}, current_pair={current_pair}"
                )
                print("Error:", e)

    def validate_pairs(self, prev_pair, current_pair):
        """
        Validates that both previous and current pairs are complete and non-empty.
        """
        if not prev_pair or len(prev_pair) != 2 or not all(prev_pair):
            print(f"Invalid previous pair: {prev_pair}")
            return False
        if not current_pair or len(current_pair) != 2 or not all(current_pair):
            print(f"Invalid current pair: {current_pair}")
            return False
        return True

    def process_response(self, response, row_idx, pair_idx, prev_pair, current_pair):
        """
        Processes the LLM response, performs risk analysis, and makes decisions.
        """
        print("Current historical risk:", self.historical_risk)
        print(f"Row {row_idx + 1}, Conversation {pair_idx}:")
        print("Previous Pair:", prev_pair)
        print("Current Pair:", current_pair)

        try:
            content_data = self.clean_and_parse_content(response.get("content", "{}"))
        except ValueError as e:
            print("Error parsing 'content':", e)
            content_data = {}

        # Extract details from the LLM response
        interaction_risk = content_data.get("overall_progression_summary", {}).get(
            "final_risk_level", 0
        )
        reasoning = content_data.get("overall_progression_summary", {}).get(
            "risk_progression", "N/A"
        )
        recommendations = content_data.get("recommendations", [])

        # Display extracted details
        print("\nInteraction Risk and Recommendations:")
        print(f"  Interaction Risk: {interaction_risk}")
        print(f"  Risk Progression Reasoning: {reasoning}")
        print(f"  Recommendations:")
        for rec in recommendations:
            print(f"    - {rec}")

        # Risk analysis
        pattern_risk = self.risk_calculator.calculate_pattern_risk(
            content_data.get("patterns", {})
        )
        
        progressive_risk = self.risk_calculator.calculate_progressive_risk(
            self.historical_risk, interaction_risk, pattern_risk
        )
        self.historical_risk = progressive_risk  # Update historical risk

        # Security decision
        decision = self.decision_engine.evaluate_risk(
            progressive_risk, self.historical_risk
        )
        print("\n"+"-"*80)
        print("\nRisk Analysis Results:")
        print("Decision:", decision["decision"].upper())
        print("Message:", decision["message"])
        print("Historical Risk:", decision["historical_risk"])
        print("Current Pattern risk:", pattern_risk)
        print("Progressive Risk:", decision["progressive_risk"], "Threasold: ", "Block", self.config.risk.block_threshold, "Warn", self.config.risk.warn_threshold)
        print("Reasoning:", decision["reasoning"])
        print("\n" + "-" * 80)

    async def analyze_conversations(self):
        df = self.dataset_manager.load_data()
        unique_tactics = df["tactic"].unique()
        tactic_choices = {
            chr(97 + i): tactic for i, tactic in enumerate(unique_tactics)
        }

        print("\nAvailable tactics:")
        for choice, tactic in tactic_choices.items():
            print(f"  {choice}. {tactic}")

        # Prompt user to select a tactic
        while True:
            user_choice = (
                input("\nSelect a tactic to test (e.g., 'a', 'b', 'c'): ")
                .strip()
                .lower()
            )
            if user_choice in tactic_choices:
                tactic_name = tactic_choices[user_choice]
                break
            else:
                print("Invalid choice. Please select a valid option.")

        print(f"\nTesting for tactic: {tactic_name}")
        tactic_df = df[df["tactic"] == tactic_name]

        total_rows = len(tactic_df)
        print(f"\nTotal rows available for tactic '{tactic_name}': {total_rows}")

        while True:
            try:
                max_rows = int(
                    input(f"Enter the number of rows to analyze (1 to {total_rows}): ")
                )
                if 1 <= max_rows <= total_rows:
                    break
                else:
                    print(f"Please enter a number between 1 and {total_rows}.")
            except ValueError:
                print("Invalid input. Please enter a valid integer.")

        analyzed_rows = 0
        for idx, (_, row) in enumerate(tactic_df.iterrows()):
            if analyzed_rows >= max_rows:
                break
            await self.analyze_row(idx, row)
            analyzed_rows += 1

        print(f"\nAnalysis completed. Total rows analyzed: {analyzed_rows}/{max_rows}")


if __name__ == "__main__":
    # Prompt user for LLM type
    llm_options = ["gpt", "claude", "gemini"]
    print("\nAvailable LLM types:")
    for i, llm in enumerate(llm_options, 1):
        print(f"  {i}. {llm}")

    while True:
        try:
            llm_choice = int(input("Select the LLM type (e.g., '1' for GPT): ").strip())
            if 1 <= llm_choice <= len(llm_options):
                llm_type = llm_options[llm_choice - 1]
                break
            else:
                print(f"Please enter a number between 1 and {len(llm_options)}.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")

    analyzer = ConversationAnalyzer("config/config.yaml", llm_type)
    asyncio.run(analyzer.analyze_conversations())
