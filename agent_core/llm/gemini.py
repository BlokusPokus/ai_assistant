from typing import Union
import google.generativeai as genai
from .llm_client import LLMClient
from ..types.messages import ToolCall, FinalAnswer
from dotenv import load_dotenv
load_dotenv()


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
        print(f"Initialized GeminiLLM with model: {model}")

    def complete(self, prompt: str, functions: dict) -> dict:
        """Implements LLMClient.complete"""
        try:
            print(
                f"GeminiLLM.complete called with prompt length: {len(prompt)}")
            print(
                f"Functions provided: {list(functions.keys()) if functions else 'None'}")

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
                            "properties": func_def.get("parameters", {}).get("properties", {}),
                            "required": func_def.get("parameters", {}).get("required", [])
                        }
                    }
                    tools.append(tool)
                print(
                    f"Converted {len(tools)} functions to Gemini tool format")

            # Make the API call with tools as a direct parameter
            print("Calling Gemini API...")
            response = self.model.generate_content(
                prompt,
                tools=[{"function_declarations": tools}] if tools else None
            )
            print(f"Received response from Gemini API: {response}")

            # Get the first candidate's content
            candidate = response.candidates[0]
            content = candidate.content
            print(f"Extracted candidate content: {content}")

            # Check if the response has a function call
            if hasattr(content.parts[0], 'function_call') and content.parts[0].function_call is not None:
                print("Function call detected in response")
                function_call = content.parts[0].function_call
                # Extract the name correctly - it might be in function_call.name
                name = getattr(function_call, 'name', None)
                if not name and hasattr(function_call, 'function_name'):
                    name = function_call.function_name
                if not name:  # Add this check to ensure name is valid
                    print("No valid function name found in response")
                    # Treat as text response
                    return {"content": content.parts[0].text}
                print(f"Function name: {name}")

                # Ensure we have valid arguments
                args = {}
                if hasattr(function_call, 'args') and function_call.args is not None:
                    print(f"Function args type: {type(function_call.args)}")
                    if isinstance(function_call.args, dict):
                        args = function_call.args
                    elif hasattr(function_call.args, 'to_dict'):
                        args = function_call.args.to_dict()
                    else:
                        try:
                            args = dict(function_call.args)
                        except TypeError:
                            print(
                                f"Could not convert args to dict: {function_call.args}")
                            args = {}
                print(f"Processed function args: {args}")

                return {
                    "function_call": {
                        "name": name,
                        "arguments": args
                    }
                }
            else:
                print("No function call detected, processing as text response")
                # Fix: Access text content correctly from the response structure
                if content.parts and len(content.parts) > 0:
                    text_content = content.parts[0].text
                    print(f"Extracted text content: {text_content}")
                    return {"content": text_content}
                else:
                    print("No text content found in response")
                    return {"content": ""}

        except Exception as e:
            print(f"Error in Gemini completion: {str(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            if 'response' in locals() and response is not None:
                print(f"Response structure: {response}")  # Debug print
            else:
                print("Response is None or not available.")
            raise

    def parse_response(self, response: dict) -> Union[ToolCall, FinalAnswer]:
        """Implements LLMClient.parse_response"""
        print(f"Parsing response: {response}")
        if "error" in response:
            return FinalAnswer(output=f"Error: {response['error']}")

        if "function_call" in response:
            return ToolCall(
                name=response["function_call"]["name"],
                args=response["function_call"]["arguments"]
            )
        return FinalAnswer(output=response.get("content", ""))

    def embed_text(self, text: str) -> list[float]:
        """
        Create embeddings using Gemini.

        Args:
            text: Text to embed

        Returns:
            list[float]: Vector embedding
        """
        try:
            print(f"Creating embedding for text of length: {len(text)}")
            result = self.embedding_model.embed_content(text)
            if result.embedding:
                print(
                    f"Embedding created with length: {len(result.embedding)}")
                return result.embedding
            else:
                print("No embedding returned from API")
                return []
        except Exception as e:
            print(f"Error creating embedding: {str(e)}")
            return []
