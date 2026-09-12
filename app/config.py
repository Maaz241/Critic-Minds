"""
config.py
Configuration and Secrets Management for Critic Minds.
Supports loading from environment variables, .env file, and Streamlit Secrets.
Never logs, displays, or exposes secret values.
"""
import os
from typing import Optional, Dict
from dotenv import load_dotenv

# Load local .env if present
load_dotenv()


def _get_secret(key: str, default: str = "") -> str:
    """Safely retrieves a key from Streamlit secrets (if running under Streamlit) or os.environ."""
    # First check Streamlit secrets if streamlit is imported and secrets exists
    try:
        import streamlit as st
        if hasattr(st, "secrets") and key in st.secrets:
            val = st.secrets[key]
            if val:
                return str(val).strip()
    except Exception:
        pass

    return os.environ.get(key, default).strip()


class AppConfig:
    """Application configuration holder."""

    @staticmethod
    def default_provider() -> str:
        return _get_secret("DEFAULT_LLM_PROVIDER", "gemini").lower()

    @staticmethod
    def get_default_key(provider: str) -> Optional[str]:
        """Returns the application default API key for a given provider, if configured."""
        provider = provider.lower()
        if provider == "gemini":
            key = _get_secret("GEMINI_API_KEY")
            return key if key else None
        elif provider == "groq":
            key = _get_secret("GROQ_API_KEY")
            return key if key else None
        return None

    @staticmethod
    def is_default_available(provider: str) -> bool:
        """Checks if a default key is configured for the given provider."""
        key = AppConfig.get_default_key(provider)
        return bool(key and len(key) > 5)

    @staticmethod
    def embedding_model_name() -> str:
        return _get_secret("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
