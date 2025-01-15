import os
from dotenv import load_dotenv, find_dotenv

import json
from typing import Dict, Any, Tuple
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic
import google.generativeai as genai

# import replicate
from prompts.prompt_templates import PromptManager
from config.tca_config import TCAConfig
from prompts.prompt_response import Response

class LLMManager:
    def __init__(self, prompt_manager: PromptManager):
        """
        Initializes the LLMManager with the necessary API clients and keys.

        Args:
            prompt_manager (PromptManager): The PromptManager instance for managing prompts.
        """
        self.prompt_manager = prompt_manager
        self.config = TCAConfig("config/config.yaml")
        # Load environment variables from .env file
        load_dotenv(find_dotenv())

        print("Did dotenv loaded correctly: ", os.getenv("OPENAI_API_KEY"))

        # Access environment variables
        openai_api_key = os.getenv("OPENAI_API_KEY")
        anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        google_genai_api_key = os.getenv("GOOGLE_GENAI_API_KEY")
        replicate_api_key = os.getenv("LLAMA_API_KEY")

        gcp_project_id = self.config.gcp_project_id
        print(f"Loaded GCP project ID: {gcp_project_id}")
        # Initialize OpenAI client

        if not openai_api_key:
            raise ValueError("Missing OPENAI_API_KEY environment variable")
        self.openai_client = AsyncOpenAI(api_key=openai_api_key)

        # Initialize Anthropic client
        anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        if not anthropic_api_key:
            raise ValueError("Missing ANTHROPIC_API_KEY environment variable")
        self.anthropic_client = AsyncAnthropic(api_key=anthropic_api_key)

        # Google Generative AI API key
        self.google_api_key = os.getenv("GOOGLE_GENAI_API_KEY")
        if not self.google_api_key:
            raise ValueError("Missing GOOGLE_GENAI_API_KEY environment variable")

        # Initialize Replicate client
        # replicate_api_key = os.getenv("LLAMA_API_KEY")
        # if not replicate_api_key:
        #     raise ValueError("Missing REPLICATE_API_KEY environment variable")
        # self.replicate_client = replicate.Client(api_token=replicate_api_key)

    async def analyze_conversation(
        self, llm_type: str, prev_pair: Tuple[str, str], current_pair: Tuple[str, str]
    ) -> Dict[str, Any]:
        """
        Analyzes a conversation using the specified LLM type.

        Args:
            llm_type (str): The type of LLM (e.g., "gpt", "claude").
            prev_pair (Tuple[str, str]): The previous assistant-human conversation pair.
            current_pair (Tuple[str, str]): The current assistant-human conversation pair.

        Returns:
            Dict[str, Any]: The analysis result from the LLM.
        """
        template = self.prompt_manager.get_template(llm_type)
        print("*" * 50)
        print("Formatting prompt now")
        prompt = template.format(prev_pair=prev_pair, current_pair=current_pair)
        # print("Prompt formatted: " + prompt)

        handlers = {
            "gpt": self._call_gpt,
            "claude": self._call_claude,
            "gemini": self._call_gemini,
           # "llama": self._call_llama,
        }

        handler = handlers.get(llm_type)
        if not handler:
            raise ValueError(f"Unsupported LLM type: {llm_type}")

        return await handler(prompt)

    async def _call_gpt(self, prompt: str) -> Dict[str, Any]:
        """
        Calls OpenAI GPT model with the provided prompt.

        Args:
            prompt (str): The input prompt for GPT.

        Returns:
            Dict[str, Any]: The response as a JSON dictionary.
        """
        response = await self.openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
        )

        # Extract content from OpenAI response
        response_content = response.choices[0].message.content

        # Parse the content to extract structured information
        # You'll need to implement this based on your content structure
        parsed_data = self.parse_content(
            response_content
        )  # This function needs to be implemented

        # Create Response instance with all fields
        response_out = Response(
            content=response_content,
            risk_level=parsed_data.get("risk_level"),
            recommendations=parsed_data.get("recommendations"),
            intent_shift=parsed_data.get("intent_shift"),
            prompt_attack=parsed_data.get("prompt_attack"),
            patterns=parsed_data.get("patterns"),
            overall_progression_summary=parsed_data.get("overall_progression_summary"),
        )

        # Access and print the attributes
        # print("Risk Level:", response_out.risk_level)
        # print("Recommendations:", response_out.recommendations)
        # print("Intent Shift Details:", response_out.intent_shift)
        # print("Prompt Attack Details:", response_out.prompt_attack)
        # print("Patterns:", response_out.patterns)
        # print("Overall Progression Summary:", response_out.overall_progression_summary)

        return response_out.dict()

    def parse_content(self, content: str) -> dict:
        """
        Parse the OpenAI response content to extract structured information.
        This is a placeholder - implement based on your content structure.
        """
        # Example implementation - you'll need to modify this based on your actual content structure
        return {
            'risk_level': None,
            'recommendations': [],
            'intent_shift': {},
            'prompt_attack': {},
            'patterns': {},
            'overall_progression_summary': {}
        }

    async def _call_claude(self, prompt: str) -> Dict[str, Any]:
        """
        Calls Anthropic Claude model with the provided prompt.

        Args:
            prompt (str): The input prompt for Claude.

        Returns:
            Dict[str, Any]: The response as a JSON dictionary.
        """
        response = await self.anthropic_client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=2000,
            temperature=0.1,
            messages=[{"role": "user", "content": prompt}],
        )
        return json.loads(response.content[0].text)

    async def _call_gemini(self, prompt: str) -> Dict[str, Any]:
        """
        Calls Google Generative AI Gemini model with the provided prompt.

        Args:
            prompt (str): The input prompt for Gemini.

        Returns:
            Dict[str, Any]: The response as a JSON dictionary.
        """
        genai.configure(api_key=self.google_api_key)
        model = genai.GenerativeModel("gemini-pro")
        response = await model.generate_content_async(prompt)
        return json.loads(response.text)

    # async def _call_llama(self, prompt: str) -> Dict[str, Any]:
    #     """
    #     Calls LLaMA model hosted on Replicate with the provided prompt.

    #     Args:
    #         prompt (str): The input prompt for LLaMA.

    #     Returns:
    #         Dict[str, Any]: The response as a JSON dictionary.
    #     """
    #     output = await self.replicate_client.async_run(
    #         "meta/llama-2-70b-chat:02e509c789964a7ea8736978a43525956ef40397be9033abf9fd2badfe68c9e3",
    #         input={"prompt": prompt},
    #     )
    #     return json.loads(output)
