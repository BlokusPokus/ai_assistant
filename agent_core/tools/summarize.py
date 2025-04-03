import os

from dotenv import load_dotenv
from agent_core.llm.gemini import GeminiLLM
from .base import Tool
from typing import Dict, Any
from agent_core.llm.llm_client import LLMClient
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY environment variable not set")


class SummarizeTool:
    def __init__(self, llm_client: GeminiLLM):
        # Initialize the LLM client
        self.llm_client = GeminiLLM(api_key=api_key, model="gemini-1.5-pro")

        # Create the summarize tool
        self.summarize_tool = Tool(
            name="summarize_text",
            func=self.summarize_text,
            description="Summarize a given text using a language model",
            parameters={
                "text": {
                    "type": "string",
                    "description": "Text to be summarized"
                }
            }
        )

    def __iter__(self):
        """Makes the class iterable to return all tools"""
        return iter([self.summarize_tool])

    def summarize_text(self, text: str) -> Dict[str, Any]:
        """Summarize the given text using a language model"""
        prompt = f"Summarize the following text:\n\n{text}"
        try:
            response = self.llm_client.complete(prompt, [])
            summary = response.get("content", "No summary available")
            return {"summary": summary}
        except Exception as e:
            return {"error": f"Failed to summarize text: {str(e)}"}


def test_summarize_tool():
    # Initialize the LLM client with your API key or configuration
    # Replace with actual API key
    llm_client = GeminiLLM(api_key=api_key, model="gemini-1.5-pro")

    # Instantiate the SummarizeTool
    summarize_tool = SummarizeTool(llm_client)

    # Test the summarize_text method
    text_to_summarize = (
        "The Bilderberg Meeting is an annual conference established in 1954 to foster dialogue "
        "between Europe and North America. The meeting has been held annually since its inception, "
        "with the exception of 1976, when it was canceled due to the Lockheed scandal involving "
        "Prince Bernhard of the Netherlands."
    )
    summary_result = summarize_tool.summarize_text(text_to_summarize)
    print("Summary Result:")
    print(summary_result)


if __name__ == "__main__":
    test_summarize_tool()
