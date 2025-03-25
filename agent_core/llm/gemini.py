from typing import Dict, Any, Union
import google.generativeai as genai
from .llm_client import LLMClient
from .prompt_builder import build_prompt
from ..types.messages import ToolCall, FinalAnswer


class GeminiLLM(LLMClient):
    def __init__(self, api_key: str, model: str = "gemini-1.5-flash"):
        """
        Initialize Gemini LLM.

        Args:
            api_key: Google API key
            model: Model name to use
        """
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)
        self.embedding_model = genai.GenerativeModel('embedding-001')

    def complete(self, prompt: str, functions: list) -> dict:
        """Implements LLMClient.complete"""
        response = self.model.generate_content({
            "prompt": prompt,
            "tools": functions  # Assuming Gemini supports function calling
        })
        return response.dict()  # Convert response to dict format

    def parse_response(self, response: dict) -> Union[ToolCall, FinalAnswer]:
        """Implements LLMClient.parse_response"""
        if "function_call" in response:
            return ToolCall(
                name=response["function_call"]["name"],
                args=response["function_call"]["arguments"]
            )
        return FinalAnswer(output=response.get("text", ""))

    def embed_text(self, text: str) -> list[float]:
        """
        Create embeddings using Gemini.

        Args:
            text: Text to embed

        Returns:
            list[float]: Vector embedding
        """
        result = self.embedding_model.embed_content(text)

        if result.embedding:
            return result.embedding
        else:
            raise Exception("Failed to generate embedding")
