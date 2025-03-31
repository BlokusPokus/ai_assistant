"""
Central configuration for the agent core framework.

🛠 config.py
Sets up constants like vector DB settings, loop limits, tool metadata, debug flags, etc.

Constants:
    VECTOR_DB_URL: URL for vector database connection
    MAX_MEMORY_RESULTS: Maximum number of memory items to retrieve
    LOOP_LIMIT: Maximum number of iterations in agent loop
    GOOGLE_API_KEY/GEMINI_API_KEY: API keys for LLM access

Description:
    Central configuration file that loads environment variables and defines
    constants used throughout the agent framework. Validates required API keys
    and provides default values for various settings.
"""
import os
from dotenv import load_dotenv
load_dotenv()

# Vector DB settings
VECTOR_DB_URL = "http://localhost:6333"
MAX_MEMORY_RESULTS = 5
LOOP_LIMIT = 5

# LLM settings
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable must be set")

GEMINI_API_KEY = GOOGLE_API_KEY
if not GEMINI_API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable must be set")
