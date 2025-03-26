"""
Weather information tool implementation.
"""
from .base import Tool


def get_weather(location: str) -> str:
    """Mock weather tool - replace with real API call"""
    return f"The weather in {location} is sunny and 22°C"


WeatherTool = Tool(
    name="get_weather",
    func=get_weather,
    description="Get the current weather for a location",
    parameters={
        "location": {
            "type": "string",
            "description": "The city or location to get weather for"
        }
    }
)
