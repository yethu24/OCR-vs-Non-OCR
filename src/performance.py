"""Performance utilities: timing, cost estimation, and system snapshots."""

from __future__ import annotations

import logging
import time

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Timer context manager
# ---------------------------------------------------------------------------


class Timer:
    """Simple context manager that records wall-clock elapsed time in ms.

    Usage::

        with Timer() as t:
            do_work()
        print(t.elapsed_ms)
    """

    def __init__(self) -> None:
        self.elapsed_ms: float = 0.0
        self._start: float = 0.0

    def __enter__(self) -> "Timer":
        self._start = time.perf_counter()
        return self

    def __exit__(self, *exc) -> None:
        self.elapsed_ms = (time.perf_counter() - self._start) * 1000


# ---------------------------------------------------------------------------
# Cost estimation
# ---------------------------------------------------------------------------

# Per-token prices in USD: (input_price, output_price) per 1 million tokens.
# Used to estimate API cost per document after each LLM call.
_PRICING: dict[str, tuple[float, float]] = {
    "gpt-4o":                   (2.50,  10.00),
    "gpt-4o-mini":              (0.15,   0.60),
    "claude-sonnet-4-5-20250929":   (3.00,  15.00),
    "claude-sonnet-4-6":            (3.00,  15.00),
    "claude-3-5-sonnet":            (3.00,  15.00),
    "claude-3-5-sonnet-latest":     (3.00,  15.00),
    "claude-3-haiku-20240307":  (0.25,   1.25),
}


def estimate_cost(
    provider: str,
    model: str,
    input_tokens: int,
    output_tokens: int,
) -> float:
    """Return an estimated USD cost for the given token counts.

    Returns 0.0 (with a warning) for unknown models.
    """
    # Try exact model name first, then strip provider prefix (e.g. "openai/gpt-4o" → "gpt-4o")
    key = model
    if key not in _PRICING:
        key = model.split("/")[-1] if "/" in model else model

    if key not in _PRICING:
        logger.warning("No pricing data for model '%s'; cost set to 0.0", model)
        return 0.0

    input_price, output_price = _PRICING[key]
    # Prices are per 1M tokens, so divide by 1M to get USD
    return (input_tokens * input_price + output_tokens * output_price) / 1_000_000


# ---------------------------------------------------------------------------
# System snapshot (optional, for resource tracking)
# ---------------------------------------------------------------------------


def get_system_snapshot() -> dict:
    """Return a point-in-time snapshot of CPU and memory usage.

    Returns an empty dict if *psutil* is not available.
    """
    try:
        import psutil

        proc = psutil.Process()
        return {
            "cpu_percent": proc.cpu_percent(interval=0.1),
            "memory_rss_mb": round(proc.memory_info().rss / (1024 * 1024), 1),
        }
    except Exception:
        return {}
