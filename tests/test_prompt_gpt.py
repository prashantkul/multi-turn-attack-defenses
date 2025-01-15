import asyncio
import os
import json

from prompts.prompt_templates import PromptManager
from llms.llm_manager import LLMManager
from tca.risk_calculator import RiskCalculator
from config.tca_config import TCAConfig
from dataset.dataset_manager import DatasetManager
from dotenv import load_dotenv, find_dotenv


def clean_and_parse_content(content):
    """
    Cleans Markdown formatting and parses the content field as JSON.
    Args:
        content (str): The raw 'content' field.
    Returns:
        dict: Parsed JSON object.
    Raises:
        ValueError: If parsing fails.
    """
    try:
        # Remove Markdown formatting if present
        cleaned_content = (
            content.strip("`")  # Remove backticks
            .replace("```json", "")  # Remove opening Markdown tag
            .replace("```", "")  # Remove closing Markdown tag
            .strip()  # Remove leading/trailing whitespace
        )
        # Attempt to parse as JSON
        return json.loads(cleaned_content)
    except Exception as e:
        raise ValueError(f"Could not parse content as JSON. Error: {e}")


def pretty_print_analysis_response(response):
    """
    Pretty-prints the analysis response with properly formatted JSON fields.
    Args:
        response (dict): The raw response dictionary containing the 'content' field.
    """
    if "content" in response and isinstance(response["content"], str):
        try:
            # Parse the content field after cleaning
            parsed_content = clean_and_parse_content(response["content"])
            print("Analysis Response (Formatted JSON Content):")
            print(
                json.dumps(parsed_content, indent=4)
            )  # Pretty-print the parsed content
        except ValueError as e:
            print("Could not parse the 'content' field as JSON.")
            print("Error:", e)
            print("Raw 'content':", response["content"])
    else:
        print("No valid 'content' field in response.")

    # Pretty-print additional fields
    additional_fields = {k: v for k, v in response.items() if k != "content"}
    if additional_fields:
        print("\nAdditional Fields in Response:")
        print(json.dumps(additional_fields, indent=4))


async def main():
    # Load dotenv
    load_dotenv(find_dotenv())
    if os.getenv("OPENAI_API_KEY"):
        print("DotEnv loaded correctly")

    # Initialize PromptManager, LLMManager, and DatasetManager
    prompt_manager = PromptManager()
    llm_manager = LLMManager(prompt_manager=prompt_manager)
    dataset_manager = DatasetManager(TCAConfig("config/config.yaml"))

    # Load the dataset
    df = dataset_manager.load_data()

    # Get unique tactics
    unique_tactics = df["tactic"].unique()
    print("\nAvailable tactics:")
    tactic_choices = {chr(97 + i): tactic for i, tactic in enumerate(unique_tactics)}
    for choice, tactic in tactic_choices.items():
        print(f"  {choice}. {tactic}")

    # Prompt user to select a tactic
    while True:
        user_choice = (
            input("\nSelect a tactic to test (e.g., 'a', 'b', 'c'): ").strip().lower()
        )
        if user_choice in tactic_choices:
            tactic_name = tactic_choices[user_choice]
            break
        else:
            print("Invalid choice. Please select a valid option.")

    print(f"\nTesting for tactic: {tactic_name}")

    # Filter dataset for the selected tactic
    tactic_df = df[df["tactic"] == tactic_name]

    # Ask user how many rows to analyze
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

    # Analyze rows and their conversation pairs
    analyzed_rows = 0
    for idx, (_, row) in enumerate(tactic_df.iterrows()):
        if analyzed_rows >= max_rows:
            break

        # Extract conversation pairs from the row
        conversation_pairs = dataset_manager.extract_conversation_pairs(row)
        print(
            f"******** Total conversation pairs in row {idx + 1}: {len(conversation_pairs)} *********"
        )

        if not conversation_pairs or len(conversation_pairs) < 2:
            print(f"Not enough pairs to analyze for row {idx + 1}. Skipping.")
            continue

        # Process overlapping pairs (current + next)
        for i in range(1, len(conversation_pairs)):
            prev_pair = conversation_pairs[i - 1]
            current_pair = conversation_pairs[i]

            # Validate the pairs
            if not prev_pair or len(prev_pair) != 2 or not all(prev_pair):
                print(f"Invalid previous pair at index {i - 1}: {prev_pair}")
                continue
            if not current_pair or len(current_pair) != 2 or not all(current_pair):
                print(f"Invalid current pair at index {i}: {current_pair}")
                continue

            try:
                # Analyze the conversation using GPT
                # print(
                #     f"Debug: Passing to analyze_conversation - prev_pair: {prev_pair}, current_pair: {current_pair}"
                # )
                response = await llm_manager.analyze_conversation(
                    "gpt", prev_pair, current_pair
                )

                # Extract and parse the "content" field
                raw_content = response.get("content", "{}")
                try:
                    content_data = json.loads(raw_content)  # Parse the JSON string
                except json.JSONDecodeError as e:
                    print(f"Error parsing 'content' field as JSON: {e}")
                    content_data = {}  # Default to an empty dictionary

                # Log results
                print(f"Tactic: {tactic_name}")
                print(f"Row {idx + 1}, Conversation {i}/{len(conversation_pairs)}:")
                print("Previous Pair:", prev_pair)
                print("Current Pair:", current_pair)
                # Format the analysis response as JSON
                pretty_print_analysis_response(response)
                print("\n" + "-" * 80 + "\n")

                # Initialize RiskCalculator with custom weights
                if "overall_progression_summary" not in response:
                    print("Warning: 'overall_progression_summary' missing in response, skipping risk analysis.")

                else: 
                    risk_calculator = RiskCalculator()
                    print("\n" + "Risk Analysis".center(80, "=") + "\n")
                    print(f"Step {i}:")
                    # Calculate pattern risk
                    pattern_risk = risk_calculator.calculate_pattern_risk(content_data.get("patterns", {}))
                    print(f"Pattern Risk: {pattern_risk}")
                    # Calculate interaction risk
                    interaction_risk = content_data.get("overall_progression_summary", {}).get("final_risk_level", 0)
                    print(f"Interaction Risk: {interaction_risk}")
                    # Calculate progressive risk
                    progressive_risk = risk_calculator.calculate_progressive_risk(
                        interaction_risk, pattern_risk
                    )
                    print(f"Progressive Risk: {progressive_risk}")
                    print("\n" + "=" * 80 + "\n")

            except Exception as e:
                print(
                    f"Error analyzing conversation pair {i}: prev_pair={prev_pair}, current_pair={current_pair}"
                )
                print("Error:", e)
                continue

        analyzed_rows += 1

    print(f"\nAnalysis completed. Total rows analyzed: {analyzed_rows}/{max_rows}")


# Run the async main function
if __name__ == "__main__":
    asyncio.run(main())
