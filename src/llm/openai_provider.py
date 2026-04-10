"""OpenAI LLM provider (GPT-4o and compatible models).

Uses the Responses API with Structured Outputs (Pydantic) for schema-
guaranteed JSON extraction.  Supports both text mode (OCR-based) and vision
mode (image-based) pipelines.
"""

from __future__ import annotations

import logging
import os
import time

from PIL import Image

from ..schema import BillExtraction
from .base import LLMProvider

logger = logging.getLogger(__name__)


class OpenAIProvider(LLMProvider):
    """OpenAI Responses API provider with structured output."""

    def __init__(
        self,
        model: str = "gpt-4o",
        temperature: float = 0.0,
        max_tokens: int = 2000,
        vision_detail: str = "high",
        timeout: float = 120.0,
        max_retries: int = 2,
        **kwargs,
    ) -> None:
        super().__init__(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout,
            max_retries=max_retries,
            **kwargs,
        )
        self.vision_detail = vision_detail

        import openai

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY environment variable is not set. "
                "Add it to your .env file or export it in your shell."
            )
        self._client = openai.OpenAI(
            api_key=api_key,
            timeout=timeout,
            max_retries=max_retries,
        )

    # ------------------------------------------------------------------
    # Text mode
    # ------------------------------------------------------------------

    def extract_from_text(self, ocr_text: str, prompt: str) -> dict:
        start = time.perf_counter()
        # Structured Outputs: responses.parse returns validated JSON matching
        # the BillExtraction schema — no manual JSON parsing needed
        response = self._client.responses.parse(
            model=self.model,
            instructions=prompt,            # system-level extraction prompt
            input=[{"role": "user", "content": ocr_text}],  # raw OCR text
            text_format=BillExtraction,     # Pydantic schema for structured output
            temperature=self.temperature,
            max_output_tokens=self.max_tokens,
        )
        latency_ms = (time.perf_counter() - start) * 1000

        return self._build_result(response, latency_ms, "text")

    # ------------------------------------------------------------------
    # Vision mode
    # ------------------------------------------------------------------

    def extract_from_image(self, images: list[Image.Image], prompt: str) -> dict:
        # Build a multi-part message: base64 images first, then a text instruction
        content_parts: list[dict] = []
        for img in images:
            b64 = self.encode_image_base64(img)
            content_parts.append(
                {
                    "type": "input_image",
                    "image_url": f"data:image/png;base64,{b64}",
                    "detail": self.vision_detail,
                }
            )
        content_parts.append(
            {
                "type": "input_text",
                "text": "Extract the fields from the utility bill shown in the image(s) above.",
            }
        )

        start = time.perf_counter()
        response = self._client.responses.parse(
            model=self.model,
            instructions=prompt,
            input=[{"role": "user", "content": content_parts}],
            text_format=BillExtraction,
            temperature=self.temperature,
            max_output_tokens=self.max_tokens,
        )
        latency_ms = (time.perf_counter() - start) * 1000

        return self._build_result(response, latency_ms, "vision")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _build_result(self, response, latency_ms: float, mode: str) -> dict:
        raw_output = response.output_text or ""
        token_usage = {
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
        }

        logger.info(
            "OpenAI %s mode | model=%s | tokens_in=%d tokens_out=%d | %.0f ms",
            mode,
            self.model,
            token_usage["input_tokens"],
            token_usage["output_tokens"],
            latency_ms,
        )

        return {
            "raw_output": raw_output,
            "token_usage": token_usage,
            "latency_ms": latency_ms,
        }

    # ------------------------------------------------------------------
    # Metadata
    # ------------------------------------------------------------------

    def get_model_id(self) -> str:
        return f"openai/{self.model}"
