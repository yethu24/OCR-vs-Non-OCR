"""OpenAI LLM provider (GPT-4o and compatible models).

Supports both text mode (OCR-based) and vision mode (image-based) extraction
via the Chat Completions API with JSON response format.
"""

from __future__ import annotations

import logging
import os
import time

from PIL import Image

from .base import LLMProvider

logger = logging.getLogger(__name__)


class OpenAIProvider(LLMProvider):
    """OpenAI Chat Completions provider."""

    def __init__(
        self,
        model: str = "gpt-4o",
        temperature: float = 0.0,
        max_tokens: int = 2000,
        **kwargs,
    ) -> None:
        super().__init__(model=model, temperature=temperature, max_tokens=max_tokens, **kwargs)

        import openai

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY environment variable is not set. "
                "Add it to your .env file or export it in your shell."
            )
        self._client = openai.OpenAI(api_key=api_key)

    # ------------------------------------------------------------------
    # Text mode
    # ------------------------------------------------------------------

    def extract_from_text(self, ocr_text: str, prompt: str) -> dict:
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": ocr_text},
        ]

        start = time.perf_counter()
        response = self._client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            response_format={"type": "json_object"},
        )
        latency_ms = (time.perf_counter() - start) * 1000

        raw_output = response.choices[0].message.content or ""
        token_usage = {
            "input_tokens": response.usage.prompt_tokens,
            "output_tokens": response.usage.completion_tokens,
        }

        logger.info(
            "OpenAI text mode  | model=%s | tokens_in=%d tokens_out=%d | %.0f ms",
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
        # Build content parts: one image per page, then a text instruction
        content_parts: list[dict] = []
        for img in images:
            b64 = self.encode_image_base64(img)
            content_parts.append(
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{b64}",
                        "detail": "high",
                    },
                }
            )
        content_parts.append(
            {
                "type": "text",
                "text": "Extract the fields from the utility bill shown in the image(s) above.",
            }
        )

        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": content_parts},
        ]

        start = time.perf_counter()
        response = self._client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            response_format={"type": "json_object"},
        )
        latency_ms = (time.perf_counter() - start) * 1000

        raw_output = response.choices[0].message.content or ""
        token_usage = {
            "input_tokens": response.usage.prompt_tokens,
            "output_tokens": response.usage.completion_tokens,
        }

        logger.info(
            "OpenAI vision mode | model=%s | tokens_in=%d tokens_out=%d | %.0f ms",
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
