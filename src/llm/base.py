"""Abstract base class for LLM providers.

Every provider must implement two extraction methods (text mode and vision
mode) plus a metadata accessor.  The return dict shape is identical for both
extraction methods so downstream code can handle them uniformly.
"""

from __future__ import annotations

import base64
import io
from abc import ABC, abstractmethod

from PIL import Image


class LLMProvider(ABC):
    """Contract that all LLM provider implementations must satisfy."""

    def __init__(
        self,
        model: str,
        temperature: float = 0.0,
        max_tokens: int = 2000,
        **kwargs,
    ) -> None:
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    # ------------------------------------------------------------------
    # Abstract interface
    # ------------------------------------------------------------------

    @abstractmethod
    def extract_from_text(self, ocr_text: str, prompt: str) -> dict:
        """Extract bill fields from OCR text (text mode).

        Args:
            ocr_text: Raw text produced by the OCR engine.
            prompt: Fully rendered prompt (schema description already filled).

        Returns:
            ``{"raw_output": str, "token_usage": {"input_tokens": int,
            "output_tokens": int}, "latency_ms": float}``
        """
        ...

    @abstractmethod
    def extract_from_image(self, images: list[Image.Image], prompt: str) -> dict:
        """Extract bill fields from page images (vision mode).

        Args:
            images: List of PIL Images (typically first 2 pages).
            prompt: Fully rendered prompt (schema description already filled).

        Returns:
            Same dict shape as :meth:`extract_from_text`.
        """
        ...

    @abstractmethod
    def get_model_id(self) -> str:
        """Return a stable identifier, e.g. ``"openai/gpt-4o"``."""
        ...

    # ------------------------------------------------------------------
    # Shared utility
    # ------------------------------------------------------------------

    @staticmethod
    def encode_image_base64(image: Image.Image, fmt: str = "PNG") -> str:
        """Encode a PIL Image to a base64 string.

        Args:
            image: The PIL Image to encode.
            fmt: Image format (default ``"PNG"``).

        Returns:
            Base64-encoded string of the image bytes.
        """
        buf = io.BytesIO()
        image.save(buf, format=fmt)
        return base64.b64encode(buf.getvalue()).decode("utf-8")
