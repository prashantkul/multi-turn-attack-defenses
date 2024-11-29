import os
from dotenv import load_dotenv

import json
from typing import Dict, Any, Tuple
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic
import google.generativeai as genai

# import replicate
from prompts.prompt_templates import PromptManager
from config.tca_config import TCAConfig


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
        load_dotenv()

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
        print("Formatting prompt now")
        prompt = template.format(prev_pair=prev_pair, current_pair=current_pair)
        print("Prompt formatted: " + prompt)

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
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
        )
        return json.loads(response.choices[0].message.content)

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
