"""
Message type definitions and tool call formats.

📁 types/messages.py
Defines UserMessage, ToolCall, AgentResponse, etc.
"""


class ToolCall:
    def __init__(self, name: str, args: dict):
        self.name = name
        self.args = args

    def is_final(self):
        return False


class FinalAnswer:
    def __init__(self, output: str):
        self.output = output

    def is_final(self):
        return True
