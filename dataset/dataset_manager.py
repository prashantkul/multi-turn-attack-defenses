from dataclasses import dataclass
import json
from typing import List, Dict, Any, Tuple
import pandas as pd
from textwrap import wrap

from config.tca_config import TCAConfig


class DatasetManager:

    def __init__(self, config: TCAConfig):
        self.config = config

    def load_data(self) -> pd.DataFrame:
        filepath = self.config.file_path
        df = pd.read_csv(filepath)
        print(f"Loaded {len(df)} records from {filepath}")
        return df.dropna(axis=1, how="all")

    def extract_conversation_pairs(self, row: pd.Series) -> List[Tuple[str, str]]:
        """
            Extracts assistant and human conversation pairs from a row of a DataFrame,
            removing the "role" field from the messages.

            Args:
                row (pd.Series): A row of the DataFrame containing conversation messages.

            Returns:
                List[Tuple[str, str]]: A list of (assistant_message, human_message) tuples.
        """
        # Extract message columns dynamically
        message_cols = [col for col in row.index if col.startswith("message_")]

        # Sort columns to ensure proper order (e.g., message_0, message_1, ...)
        message_cols = sorted(message_cols, key=lambda x: int(x.split("_")[1]))

        # Collect messages into a list and remove the "role" field if present
        messages = []
        for col in message_cols:
            raw_message = row[col]
            if pd.notna(raw_message) and str(raw_message).strip():
                # Attempt to parse message as JSON and remove "role"
                try:
                    message_data = json.loads(raw_message)
                    message_body = message_data.get("body", raw_message)  # Default to raw_message if no "body"
                    messages.append(message_body)
                except json.JSONDecodeError:
                    messages.append(raw_message)

        # Create conversation pairs
        conversation_pairs = []
        for i in range(0, len(messages), 2):
            assistant_message = messages[i] if i < len(messages) else ""
            human_message = messages[i + 1] if i + 1 < len(messages) else ""
            conversation_pairs.append((assistant_message, human_message))

        return conversation_pairs


    def process_row(self, row: pd.Series) -> Dict[str, Any]:
        return {
            "source": row["Source"],
            "temperature": row["temperature"],
            "tactic": row["tactic"],
            "question_id": row["question_id"],
            "time_spent": row["time_spent"],
            "submission_message": row["submission_message"],
            "conversation": self.get_conversation_history(row),
        }

    def get_metadata(self, df: pd.DataFrame) -> Dict[str, Any]:
        return {
            "total_records": len(df),
            "unique_sources": df["Source"].unique().tolist(),
            "unique_tactics": df["tactic"].unique().tolist(),
            "avg_time_spent": df["time_spent"].mean(),
            "temperature_stats": df["temperature"].describe().to_dict(),
        }

    def display_beautified_conversation(self, row):
        # Header with conversation metadata
        print("\n" + "╔" + "═" * 80 + "╗")
        header = f"║ Tactic: {row['tactic']:<20} | Temp: {row['temperature']:<5} | Source: {row['Source']:<20} ║"
        print(header)
        print("╠" + "═" * 80 + "╣")

        # Get and display messages
        message_cols = [col for col in row.index if col.startswith("message_")]

        for col in message_cols:
            message = row[col]
            if pd.notna(message) and str(message).strip():
                # Determine speaker and color
                is_assistant = int(col.split("_")[1]) % 2 == 0
                speaker = "🤖 Assistant" if is_assistant else "👤 Human"

                # Format message with proper wrapping
                # Split message into lines of max 70 characters
                words = message.split()
                lines = []
                current_line = []
                current_length = 0

                for word in words:
                    if current_length + len(word) + 1 <= 70:
                        current_line.append(word)
                        current_length += len(word) + 1
                    else:
                        lines.append(" ".join(current_line))
                        current_line = [word]
                        current_length = len(word)

                if current_line:
                    lines.append(" ".join(current_line))

                # Print formatted message
                print(f"║ {speaker:<12} │")
                for line in lines:
                    print(f"║ {line:<79}║")
                print("║" + " " * 80 + "║")

        print("╚" + "═" * 80 + "╝")


# Example usage
# config = TCAConfig("config/config.yaml")
# print(config)
# manager = DatasetManager(config)  # Pass entire config object
# df = manager.load_data()  # load_data will use config.file_path
# # Iterate through each unique tactic
# for tactic in df["tactic"].unique():
#     # Filter rows for the current tactic
#     tactic_df = df[df["tactic"] == tactic]

#     # Iterate through each row in the filtered DataFrame
#     for _, row in tactic_df.iterrows():
#         # Extract conversation pairs
#         conversation_pairs = manager.extract_conversation_pairs(row)

#         # Print the results for each row
#         print(f"Tactic: {tactic}")
#         print(conversation_pairs)
#         print("\n" + "-" * 80 + "\n")
