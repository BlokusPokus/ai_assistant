from typing import Union

import google.generativeai as genai
from dotenv import load_dotenv

from ..config.logging_config import get_logger
from ..types.messages import FinalAnswer, ToolCall
from ..utils.text_cleaner import clean_text_for_logging
from .llm_client import LLMClient

# Configure module logger
logger = get_logger("llm")

load_dotenv()


class GeminiLLM(LLMClient):
    """
    A client for interacting with Google's Gemini LLM models.
    Provides completion, function calling, and embedding capabilities.
    """

    # ------------------------
    # Initialization
    # ------------------------
    def __init__(self, api_key: str, model: str = "gemini-1.5-flash"):
        """
        Initialize Gemini LLM.

        Args:
            api_key: Google API key
            model: Model name to use
        """
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)
        # Note: Embeddings are now handled by creating a client in embed_text()
        print(f"Initialized GeminiLLM with model: {model}")

    # ------------------------
    # Core LLM Operations
    # ------------------------
    def complete(self, prompt: str, functions: dict) -> dict:
        """
        Generate a completion response from Gemini model with optional function calling.

        Args:
            prompt (str): The input text prompt to send to the model
            functions (dict): Dictionary of function definitions that can be called by the model.
                            Each function should have 'name', 'description', and 'parameters'

        Returns:
            dict: Either {'content': str} for text responses or
                 {'function_call': {'name': str, 'arguments': dict}} for function calls

        Raises:
            Exception: If there's an error during the API call or response processing
        """
        try:
            # Clean text before logging
            clean_prompt = clean_text_for_logging(prompt)
            logger.debug(f"GeminiLLM.complete called with prompt length: {len(prompt)}")
            logger.debug(
                f"Functions provided: {list(functions.keys()) if functions else 'None'}"
            )

            # Convert functions to Gemini's function calling format
            tools = None
            if functions:
                # Convert dictionary of functions to list of tool objects
                tools = []
                for func_def in functions.values():
                    tool = {
                        "name": func_def["name"],
                        "description": func_def.get("description", ""),
                        "parameters": {
                            "type": "OBJECT",
                            "properties": func_def.get("parameters", {}).get(
                                "properties", {}
                            ),
                            "required": func_def.get("parameters", {}).get(
                                "required", []
                            ),
                        },
                    }
                    tools.append(tool)
                print(f"Converted {len(tools)} functions to Gemini tool format")

            # Make the API call with tools as a direct parameter
            logger.debug("Calling Gemini API...")
            response = self.model.generate_content(
                prompt, tools=[{"function_declarations": tools}] if tools else None
            )

            # Clean response before logging
            clean_response = clean_text_for_logging(str(response))
            logger.debug(f"Received response from Gemini API: {clean_response}")

            # Get the first candidate's content
            candidate = response.candidates[0]
            content = candidate.content
            clean_content = clean_text_for_logging(str(content))
            print(f"Extracted candidate content: {clean_content}")

            # Check all parts for function calls
            function_call_found = False
            for part in content.parts:
                if hasattr(part, "function_call") and part.function_call is not None:
                    if not function_call_found:
                        logger.debug("Function call detected in response")
                        function_call_found = True

                    function_call = part.function_call
                    name = getattr(function_call, "name", None)

                    if not name and hasattr(function_call, "function_name"):
                        name = function_call.function_name

                    if name:  # If we found a valid name
                        logger.debug(f"Function name: {name}")

                        # Extract arguments
                        args = {}
                        if hasattr(function_call, "args"):
                            if isinstance(function_call.args, dict):
                                args = function_call.args
                            elif hasattr(function_call.args, "to_dict"):
                                args = function_call.args.to_dict()
                            else:
                                try:
                                    args = dict(function_call.args)
                                except TypeError:
                                    logger.error(
                                        f"Could not convert args to dict: {function_call.args}"
                                    )
                                    args = {}

                        return {"function_call": {"name": name, "arguments": args}}

            # If no function call found in any part, return text content
            return {"content": content.parts[0].text if content.parts else ""}

        except Exception as e:
            logger.error(f"Error in Gemini completion: {str(e)}")
            import traceback

            logger.error(f"Traceback: {traceback.format_exc()}")
            if "response" in locals() and response is not None:
                clean_response = clean_text_for_logging(str(response))
                # Debug print
                logger.debug(f"Response structure: {clean_response}")
            else:
                logger.debug("Response is None or not available.")
            raise

    # ------------------------
    # Response Processing
    # ------------------------
    def parse_response(self, response: dict) -> Union[ToolCall, FinalAnswer]:
        """
        Parse the completion response into either a ToolCall or FinalAnswer.

        Args:
            response (dict): The response from complete() method, containing either
                           text content or function call details

        Returns:
            Union[ToolCall, FinalAnswer]:
                - ToolCall if the response contains a function call
                - FinalAnswer if the response contains text content
        """
        # Clean response before logging
        clean_response = clean_text_for_logging(str(response))
        print(f"Parsing response: {clean_response}")
        if "error" in response:
            return FinalAnswer(output=f"Error: {response['error']}")

        if "function_call" in response:
            return ToolCall(
                name=response["function_call"]["name"],
                args=response["function_call"]["arguments"],
            )
        return FinalAnswer(output=response.get("content", ""))

    # ------------------------
    # Embedding Operations
    # ------------------------
    def embed_text(self, text: str) -> list[float]:
        """
        Create vector embeddings for the given text using Gemini's embedding model.

        Args:
            text (str): The input text to create embeddings for

        Returns:
            list[float]: A vector of floating point numbers representing the text embedding.
                        Returns empty list if embedding fails.
        """
        try:
            print(f"Creating embedding for text of length: {len(text)}")
            # Use the correct Gemini embeddings API for version 0.8.4
            # In this version, embed_content is a module-level function
            import google.generativeai as genai

            # Use the module-level embed_content function
            result = genai.embed_content(
                model="models/gemini-embedding-001", content=text
            )

            # Debug: print the result structure
            print(f"API Response type: {type(result)}")
            print(f"API Response dir: {dir(result)}")

            # The API returns a dictionary with 'embedding' key
            if isinstance(result, dict) and "embedding" in result:
                embedding = result["embedding"]
                print(f"Embedding created with length: {len(embedding)}")
                return embedding
            else:
                print("No embedding returned from API")
                return []

        except Exception as e:
            print(f"Error creating embedding: {str(e)}")
            return []
