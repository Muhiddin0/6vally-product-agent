"""OpenAI client singleton."""
from typing import Optional

from openai import OpenAI

from core.config import settings

_client: Optional[OpenAI] = None


def get_openai_client() -> OpenAI:
    """Get or create OpenAI client instance."""
    global _client
    if _client is None:
        _client = OpenAI(api_key=settings.openai_api_key)
    return _client

