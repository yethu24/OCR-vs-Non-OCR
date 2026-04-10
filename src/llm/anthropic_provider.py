"""Anthropic LLM provider (Claude models).

Uses the Messages API with JSON-fenced output.  The prompt instructs the
model to return JSON; ``_strip_json_fencing`` removes any markdown code
fences Claude may wrap around the response.
"""

from __future__ import annotations

import logging
import os
import re
import time

from PIL import Image

from .base import LLMProvider

logger = logging.getLogger(__name__)

# Strips ```json or ``` fences
_FENCE_RE = re.compile(r"^```(?:json)?\s*\n?(.*?)\n?\s*```$", re.DOTALL)


def _strip_json_fencing(text: str) -> str:
    """Remove markdown code fences that wrap a JSON block.
    Claude often wraps JSON in ```json ... ``` fences, which must be
    stripped before parsing."""
    stripped = text.strip()
    m = _FENCE_RE.match(stripped)
    if m:
        return m.group(1).strip()
    return stripped


class AnthropicProvider(LLMProvider):
    """Anthropic Messages API provider."""

    def __init__(
        self,
        model: str = "claude-sonnet-4-5-20250929",
        temperature: float = 0.0,
        max_tokens: int = 2000,
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

        import anthropic

        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY environment variable is not set. "
                "Add it to your .env file or export it in your shell."
            )
        self._client = anthropic.Anthropic(
            api_key=api_key,
            timeout=timeout,
            max_retries=max_retries,
        )

    # ------------------------------------------------------------------
    # Text mode
    # ------------------------------------------------------------------

    def extract_from_text(self, ocr_text: str, prompt: str) -> dict:
        start = time.perf_counter()
        # Prompt-instructed JSON: the system prompt tells Claude to return JSON;
        # unlike OpenAI, Anthropic doesn't support structured output for this schema
        response = self._client.messages.create(
            model=self.model,
            system=prompt,                                     # extraction instructions
            messages=[{"role": "user", "content": ocr_text}],  # raw OCR text
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )
        latency_ms = (time.perf_counter() - start) * 1000

        return self._build_result(response, latency_ms, "text")

    # ------------------------------------------------------------------
    # Vision mode
    # ------------------------------------------------------------------

    def extract_from_image(self, images: list[Image.Image], prompt: str) -> dict:
        # Build multi-part content: base64 image blocks + a text instruction
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

        return self._build_result(response, latency_ms, "vision")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _build_result(self, response, latency_ms: float, mode: str) -> dict:
        # Strip any ```json fences Claude may have added around the JSON
        raw_output = _strip_json_fencing(response.content[0].text if response.content else "")
        token_usage = {
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
        }

        logger.info(
            "Anthropic %s mode | model=%s | tokens_in=%d tokens_out=%d | %.0f ms",
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
        return f"anthropic/{self.model}"
