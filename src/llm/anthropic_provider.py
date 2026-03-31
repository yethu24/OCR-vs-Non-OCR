"""Anthropic LLM provider (Claude 3.5 Sonnet and compatible models).

Supports both text mode (OCR-based) and vision mode (image-based) extraction
via the Messages API.  Since Anthropic does not offer a ``response_format``
parameter, JSON fencing (```json ... ```) is stripped from the raw output if
present.
"""

from __future__ import annotations

import logging
import os
import re
import time

from PIL import Image

from .base import LLMProvider

logger = logging.getLogger(__name__)


def _strip_json_fencing(text: str) -> str:
    """Remove markdown code fences that wrap a JSON block.

    Claude sometimes wraps its JSON output in ```json ... ``` even when
    instructed not to.  This helper strips that layer so downstream JSON
    parsing succeeds.
    """
    stripped = text.strip()
    # Match ```json ... ``` or ``` ... ```
    m = re.match(r"^```(?:json)?\s*\n?(.*?)\n?\s*```$", stripped, re.DOTALL)
    if m:
        return m.group(1).strip()
    return stripped


class AnthropicProvider(LLMProvider):
    """Anthropic Messages API provider."""

    def __init__(
        self,
        model: str = "claude-3-5-sonnet",
        temperature: float = 0.0,
        max_tokens: int = 2000,
        **kwargs,
    ) -> None:
        super().__init__(model=model, temperature=temperature, max_tokens=max_tokens, **kwargs)

        import anthropic

        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY environment variable is not set. "
                "Add it to your .env file or export it in your shell."
            )
        self._client = anthropic.Anthropic(api_key=api_key)

    # ------------------------------------------------------------------
    # Text mode
    # ------------------------------------------------------------------

    def extract_from_text(self, ocr_text: str, prompt: str) -> dict:
        start = time.perf_counter()
        response = self._client.messages.create(
            model=self.model,
            system=prompt,
            messages=[{"role": "user", "content": ocr_text}],
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )
        latency_ms = (time.perf_counter() - start) * 1000

        raw_output = _strip_json_fencing(response.content[0].text)
        token_usage = {
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
        }

        logger.info(
            "Anthropic text mode  | model=%s | tokens_in=%d tokens_out=%d | %.0f ms",
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
    # Vision mode
    # ------------------------------------------------------------------

    def extract_from_image(self, images: list[Image.Image], prompt: str) -> dict:
        # Build content blocks: one image per page, then a text instruction
        content_blocks: list[dict] = []
        for img in images:
            b64 = self.encode_image_base64(img)
            content_blocks.append(
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/png",
                        "data": b64,
                    },
                }
            )
        content_blocks.append(
            {
                "type": "text",
                "text": "Extract the fields from the utility bill shown in the image(s) above.",
            }
        )

        start = time.perf_counter()
        response = self._client.messages.create(
            model=self.model,
            system=prompt,
            messages=[{"role": "user", "content": content_blocks}],
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )
        latency_ms = (time.perf_counter() - start) * 1000

        raw_output = _strip_json_fencing(response.content[0].text)
        token_usage = {
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
        }

        logger.info(
            "Anthropic vision mode | model=%s | tokens_in=%d tokens_out=%d | %.0f ms",
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
        return f"anthropic/{self.model}"
