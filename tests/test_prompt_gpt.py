import asyncio

from prompts.prompt_templates import PromptManager
from llms.llm_manager import LLMManager
from config.tca_config import TCAConfig
from dataset.dataset_manager import DatasetManager


async def main():
    # Initialize PromptManager
    prompt_manager = PromptManager()

    # Initialize LLMManager
    llm_manager = LLMManager(prompt_manager=prompt_manager)

    # Initialize DatasetManager with configuration
    dataset_manager = DatasetManager(TCAConfig("config/config.yaml"))

    # Load the dataset
    df = dataset_manager.load_data()  # load_data will use config.file_path

    # Iterate through each unique tactic
    for tactic in df["tactic"].unique():
        # Filter rows for the current tactic
        tactic_df = df[df["tactic"] == tactic]

        # Iterate through each row in the filtered DataFrame
        for _, row in tactic_df.iterrows():
            # Extract conversation pairs
            conversation_pairs = dataset_manager.extract_conversation_pairs(row)

            # Iterate through each conversation pair
            for pair in conversation_pairs:
                # Analyze the conversation using GPT
                response = await llm_manager.analyze_conversation(
                    "gpt", pair[0], pair[1]
                )
                print(f"Tactic: {tactic}")
                print("Response:", response)

# Run the async main function
if __name__ == "__main__":
    asyncio.run(main())
