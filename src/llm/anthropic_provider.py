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
import io

from PIL import Image

from .base import LLMProvider

logger = logging.getLogger(__name__)

# Anthropic hard limit (error seen at runtime): 5 MB per base64 image payload.
_ANTHROPIC_IMAGE_MAX_BYTES = 5 * 1024 * 1024

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


def _encode_image_under_limit(img: Image.Image, max_bytes: int = _ANTHROPIC_IMAGE_MAX_BYTES) -> tuple[str, str]:
    """Encode an image to base64 under Anthropic's per-image size limit.

    Strategy:
    - Try PNG first (lossless; best for text) but it can exceed 5MB on large pages.
    - Fall back to JPEG with decreasing quality.
    - If still too large, progressively downscale and retry JPEG.
    """
    # 1) PNG attempt
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    png_bytes = buf.getvalue()
    if len(png_bytes) <= max_bytes:
        return (LLMProvider.encode_image_base64(img, fmt="PNG"), "image/png")

    # 2) JPEG attempts (quality sweep)
    def _jpeg_bytes(im: Image.Image, quality: int) -> bytes:
        b = io.BytesIO()
        # Convert to RGB for JPEG
        im_rgb = im.convert("RGB")
        im_rgb.save(b, format="JPEG", quality=quality, optimize=True, progressive=True)
        return b.getvalue()

    for q in (85, 75, 65, 55, 45, 35):
        jb = _jpeg_bytes(img, q)
        if len(jb) <= max_bytes:
            return (LLMProvider.encode_image_base64(img.convert("RGB"), fmt="JPEG"), "image/jpeg")

    # 3) Downscale + JPEG (keep aspect ratio)
    w, h = img.size
    # Start from 1600px max dimension and go down.
    for max_dim in (1600, 1400, 1200, 1000, 800):
        scale = max_dim / max(w, h)
        if scale >= 1.0:
            continue
        new_size = (max(1, int(w * scale)), max(1, int(h * scale)))
        resized = img.resize(new_size, resample=Image.LANCZOS)
        for q in (75, 60, 45):
            jb = _jpeg_bytes(resized, q)
            if len(jb) <= max_bytes:
                return (LLMProvider.encode_image_base64(resized.convert("RGB"), fmt="JPEG"), "image/jpeg")

    raise ValueError(
        f"Could not compress image under {max_bytes} bytes for Anthropic vision input "
        f"(original size={img.size}, png_bytes={len(png_bytes)})."
    )


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
            b64, media_type = _encode_image_under_limit(img)
            content_blocks.append(
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": media_type,
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
