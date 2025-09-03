"""
Logger implementation for interaction tracing.

📁 logs/logger.py
Writes logs to PostgreSQL or file. Logs every step: inputs, tools, 
memory hits, final output.
"""


def log_interaction(entry):
    """
    Logs the entire agent step for traceability.

    Args:
        entry (dict): Dict with user input, tool calls, memory, etc.
    """
