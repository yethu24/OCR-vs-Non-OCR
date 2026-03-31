from __future__ import annotations

from pathlib import Path


def load_env() -> None:
    """Load environment variables from a project-root .env file if present.

    This ensures API keys (e.g., OPENAI_API_KEY, ANTHROPIC_API_KEY) are
    consistently available via os.environ without relying on shell-specific
    export steps.
    """

    try:
        from dotenv import load_dotenv
    except ImportError:
        # Optional at runtime; required for local development convenience.
        return

    project_root = Path(__file__).resolve().parents[1]
    dotenv_path = project_root / ".env"
    if dotenv_path.exists():
        load_dotenv(dotenv_path=dotenv_path)

