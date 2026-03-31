"""LLM provider package — strategy pattern for swappable model backends."""

from .base import LLMProvider
from .registry import get_provider

__all__ = ["LLMProvider", "get_provider"]
