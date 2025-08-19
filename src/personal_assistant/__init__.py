"""
Personal Assistant Package

A comprehensive AI-powered personal assistant with SMS integration,
calendar management, and intelligent task processing.
"""

__version__ = "0.1.0"
__author__ = "Personal Assistant Team"

from .core.agent import AgentCore
from .core.runner import AgentRunner

__all__ = ["AgentCore", "AgentRunner"]
