"""
config.py – LoreBuilder Configuration
=======================================
Centralised configuration loader.
Reads from environment variables (or a .env file) and exposes
clean constants used throughout the backend.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# ------------------------------------------------------------------
# Load .env from project root (two levels up from this file)
# ------------------------------------------------------------------
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_ENV_FILE = _PROJECT_ROOT / ".env"
load_dotenv(dotenv_path=_ENV_FILE)

# ------------------------------------------------------------------
# Cognee Cloud credentials
# ------------------------------------------------------------------
COGNEE_SERVICE_URL: str = os.environ.get("COGNEE_SERVICE_URL", "")
COGNEE_API_KEY: str = os.environ.get("COGNEE_API_KEY", "")

# ------------------------------------------------------------------
# OpenRouter – LLM provider
# ------------------------------------------------------------------
OPENROUTER_API_KEY: str = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
# google/gemma-4-31b-it:free — Google Gemma 4 31B on OpenRouter free tier
OPENROUTER_MODEL: str = "google/gemma-4-31b-it:free"

# ------------------------------------------------------------------
# Google AI Studio (used for embeddings configuration in Cognee)
# ------------------------------------------------------------------
GOOGLE_API_KEY: str = os.environ.get("GOOGLE_API_KEY", "")

# ------------------------------------------------------------------
# Paths
# ------------------------------------------------------------------
WORLD_LORE_DIR: Path = _PROJECT_ROOT / "WorldLoreFiles"
GRAPH_OUTPUT_DIR: Path = _PROJECT_ROOT / "Backend" / "graph_output"
GRAPH_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
GRAPH_HTML_PATH: Path = GRAPH_OUTPUT_DIR / "knowledge_graph.html"

# ------------------------------------------------------------------
# Validation helper
# ------------------------------------------------------------------
def validate_config() -> list[str]:
    """
    Returns a list of missing/empty required config keys.
    The frontend can call this to warn the user before proceeding.
    """
    missing = []
    if not COGNEE_SERVICE_URL:
        missing.append("COGNEE_SERVICE_URL")
    if not COGNEE_API_KEY:
        missing.append("COGNEE_API_KEY")
    if not OPENROUTER_API_KEY:
        missing.append("OPENROUTER_API_KEY")
    return missing
