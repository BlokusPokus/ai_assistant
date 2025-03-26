# agent_core/llm/llm_client.py

from ..types.messages import ToolCall, FinalAnswer


class LLMClient:
    def __init__(self, model):
        """
        Initialize the client with an LLM model (e.g., Google Gemini).

        Args:
            model (Any): The LLM model client or API wrapper
        """
        self.model = model

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

            # Extract the actual response content
            # Different models might structure this differently
            if isinstance(response, dict):
                return response
            elif hasattr(response, "model_dump"):  # Pydantic model
                return response.model_dump()
            elif hasattr(response, "dict"):  # Other object with dict method
                return response.dict()
            else:
                return {"content": str(response)}  # Fallback

        except Exception as e:
            # Log error and return a safe fallback response
            print(f"Error in LLM completion: {str(e)}")
            return {"error": str(e), "content": "I encountered an error processing your request."}

    def parse_response(self, response: dict):
        """
        Parses the LLM's raw output and returns a ToolCall or FinalAnswer.

        Args:
            response (dict): Raw response from the LLM

        Returns:
            ToolCall or FinalAnswer: Parsed result from model output
        """
        # Check if response contains a function call
        if "function_call" in response:
            # Extract function name and arguments
            function_call = response["function_call"]
            return ToolCall(
                name=function_call["name"],
                args=function_call["arguments"]
            )

        # If no function call, treat as final answer
        # Look for content in common response formats
        content = (
            response.get("text") or  # Standard text field
            response.get("content") or  # Alternative content field
            response.get("output") or  # Another possible field
            # Nested message format
            response.get("message", {}).get("content") or
            "No valid response content found"  # Fallback
        )

        return FinalAnswer(output=content)
