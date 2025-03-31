# agent_core/llm/llm_client.py

from ..types.messages import ToolCall, FinalAnswer
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)


class LLMClient:
    """
    Base class for LLM clients providing a standard interface for model interactions.
    Handles prompt completion and response parsing with support for function calling.
    """

    # ------------------------
    # Initialization
    # ------------------------
    def __init__(self, model):
        """
        Initialize the client with an LLM model (e.g., Google Gemini).

        Args:
            model (Any): The LLM model client or API wrapper
        """
        self.model = model

    # ------------------------
    # Core LLM Operations
    # ------------------------
    def complete(self, prompt: str, functions: list) -> dict:
        """
        Sends prompt to the LLM with function metadata.

        Args:
            prompt (str): The constructed prompt including user message and context
            functions (list): List of available tools with their function schemas

        Returns:
            dict: Raw response from the LLM (could be function call or final response)
        """
        try:
            logging.debug(f"Sending prompt to LLM: {prompt}")
            logging.debug(f"Functions available: {functions}")

            # Convert functions list to the format expected by the model
            tools = [
                {
                    "type": "function",
                    "function": func
                } for func in functions
            ]

            # Make the API call to the LLM
            response = self.model.chat(
                messages=[{"role": "user", "content": prompt}],
                tools=tools if tools else None,  # Only include tools if we have functions
                tool_choice="auto"  # Let the model decide whether to use tools
            )

            logging.debug(f"Received response from LLM: {response}")

            return self._extract_response_content(response)

        except Exception as e:
            logging.error(f"Error in LLM completion: {str(e)}")
            return {"error": str(e), "content": "I encountered an error processing your request."}

    # ------------------------
    # Response Processing
    # ------------------------
    def _extract_response_content(self, response) -> dict:
        """
        Extracts content from various response formats into a standardized dictionary.

        Args:
            response: Raw response from the LLM model

        Returns:
            dict: Standardized response format
        """
        if isinstance(response, dict):
            return response
        elif hasattr(response, "model_dump"):  # Pydantic model
            return response.model_dump()
        elif hasattr(response, "dict"):  # Other object with dict method
            return response.dict()
        else:
            return {"content": str(response)}  # Fallback

    def parse_response(self, response: dict):
        """
        Parses the LLM's raw output and returns a ToolCall or FinalAnswer.

        Args:
            response (dict): Raw response from the LLM

        Returns:
            ToolCall or FinalAnswer: Parsed result from model output
        """
        logging.debug(f"Parsing response: {response}")

        # Check if response contains a function call
        if "function_call" in response:
            function_call = response["function_call"]
            logging.debug(f"Function call detected: {function_call}")
            return ToolCall(
                name=function_call["name"],
                args=function_call["arguments"]
            )

        # If no function call, treat as final answer
        content = (
            response.get("text") or  # Standard text field
            response.get("content") or  # Alternative content field
            response.get("output") or  # Another possible field
            # Nested message format
            response.get("message", {}).get("content") or
            "No valid response content found"  # Fallback
        )

        logging.debug(f"Final answer content: {content}")
        return FinalAnswer(output=content)
