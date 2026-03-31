#!/usr/bin/env python
"""Manual dev end-to-end test: 1 bill x 4 conditions.

Runs GB_electricity_ovo_001 through all 4 conditions:
  1. OpenAI   text mode  (OCR -> OpenAI model)
  2. OpenAI   vision mode (images -> OpenAI model)
  3. Anthropic text mode  (OCR -> Claude)
  4. Anthropic vision mode (images -> Claude)

Usage:
    source .venv/Scripts/activate
    python scripts/test_llm_e2e.py

Model selection:
  Defaults are cost-control (dev) models:
    - OPENAI_E2E_MODEL defaults to gpt-4o-mini
    - ANTHROPIC_E2E_MODEL defaults to claude-3-5-haiku
  Override via environment variables if needed:
    OPENAI_E2E_MODEL=gpt-4o
    ANTHROPIC_E2E_MODEL=claude-3-5-sonnet
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

# Ensure project root is on the path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from src.env import load_env
from src.ocr.tesseract import TesseractOCR
from src.schema import BillExtraction
from src.utils import load_prompt_template, pdf_to_images, setup_logging

setup_logging()
load_env()

# ── Config ────────────────────────────────────────────────────────────
BILL_PDF = project_root / "data" / "bills" / "GB_electricity_ovo_001.pdf"
PROMPT_FILE = project_root / "prompts" / "extraction_v1.txt"
GROUND_TRUTH = project_root / "data" / "ground_truth" / "GB_electricity_ovo_001.json"
MAX_VISION_PAGES = 2
OPENAI_MODEL = os.getenv("OPENAI_E2E_MODEL", "gpt-4o-mini")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_E2E_MODEL", "claude-3-haiku-20240307")

# ── Shared preparation ───────────────────────────────────────────────
print("=" * 70)
print("Session 2 — Manual E2E Test")
print("=" * 70)
print(f"OpenAI model:    {OPENAI_MODEL}")
print(f"Anthropic model: {ANTHROPIC_MODEL}")

# Load prompt template and render with schema description
template = load_prompt_template(PROMPT_FILE)
schema_desc = BillExtraction.schema_description()

# Convert PDF to images
print(f"\nConverting {BILL_PDF.name} to images …")
all_images = pdf_to_images(BILL_PDF, dpi=200)
vision_images = all_images[:MAX_VISION_PAGES]
print(f"  Total pages: {len(all_images)}, using first {len(vision_images)} for vision mode")

# Run OCR on all pages
print("Running Tesseract OCR (lang=en) …")
ocr_engine = TesseractOCR()
ocr_texts = [ocr_engine.extract_text(img, language="en") for img in all_images]
ocr_text = "\n\n".join(ocr_texts)
print(f"  OCR text length: {len(ocr_text)} chars")

# Render prompts
prompt_text_mode = template.format(schema_description=schema_desc, ocr_text=ocr_text)
prompt_vision_mode = template.format(schema_description=schema_desc, ocr_text="")

# Load ground truth for spot-check
gt = json.loads(GROUND_TRUTH.read_text(encoding="utf-8"))["fields"]


def validate_result(label: str, result: dict) -> None:
    """Print validation checks for a single condition."""
    print(f"\n{'─' * 60}")
    print(f"  {label}")
    print(f"{'─' * 60}")

    raw = result["raw_output"]
    tokens = result["token_usage"]
    latency = result["latency_ms"]

    # Basic checks
    assert isinstance(raw, str) and len(raw) > 0, "raw_output is empty"
    assert tokens["input_tokens"] > 0, "input_tokens is 0"
    assert tokens["output_tokens"] > 0, "output_tokens is 0"
    assert latency > 0, "latency_ms is 0"

    print(f"  Tokens in: {tokens['input_tokens']:,}  out: {tokens['output_tokens']:,}")
    print(f"  Latency:   {latency:,.0f} ms")

    # Parse JSON
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        print(f"  !! JSON parse FAILED: {exc}")
        print(f"  Raw output (first 300 chars): {raw[:300]}")
        return

    # Check all 12 fields present
    missing = [f for f in BillExtraction.SCHEMA_FIELDS if f not in parsed]
    if missing:
        print(f"  !! Missing fields: {missing}")
    else:
        print(f"  All 12 fields present: OK")

    # Spot checks
    checks = {
        "total_amount_due": (gt["total_amount_due"], parsed.get("total_amount_due")),
        "currency": (gt["currency"], parsed.get("currency")),
        "provider_name": (gt["provider_name"], parsed.get("provider_name")),
    }
    for field, (expected, actual) in checks.items():
        match = "OK" if str(actual) == str(expected) else f"MISMATCH (expected={expected})"
        print(f"  {field}: {actual} — {match}")

    # Print full extraction for inspection
    print(f"\n  Full extraction:")
    for k, v in parsed.items():
        print(f"    {k}: {v}")


# ── Condition 1: OpenAI text mode ─────────────────────────────────────
print("\n\n[1/4] OpenAI text mode …")
try:
    from src.llm.openai_provider import OpenAIProvider

    openai_provider = OpenAIProvider(model=OPENAI_MODEL, temperature=0.0, max_tokens=2000)
    result_1 = openai_provider.extract_from_text(ocr_text, prompt_text_mode)
    validate_result("OpenAI / text mode (OCR-based)", result_1)
except Exception as exc:
    print(f"  FAILED: {exc}")
    result_1 = None

# ── Condition 2: OpenAI vision mode ───────────────────────────────────
print("\n\n[2/4] OpenAI vision mode …")
try:
    if openai_provider is None:
        openai_provider = OpenAIProvider(model=OPENAI_MODEL, temperature=0.0, max_tokens=2000)
    result_2 = openai_provider.extract_from_image(vision_images, prompt_vision_mode)
    validate_result("OpenAI / vision mode (OCR-free)", result_2)
except Exception as exc:
    print(f"  FAILED: {exc}")
    result_2 = None

# ── Condition 3: Anthropic text mode ──────────────────────────────────
print("\n\n[3/4] Anthropic text mode …")
try:
    from src.llm.anthropic_provider import AnthropicProvider

    anthropic_provider = AnthropicProvider(model=ANTHROPIC_MODEL, temperature=0.0, max_tokens=2000)
    result_3 = anthropic_provider.extract_from_text(ocr_text, prompt_text_mode)
    validate_result("Anthropic / text mode (OCR-based)", result_3)
except Exception as exc:
    print(f"  FAILED: {exc}")
    result_3 = None

# ── Condition 4: Anthropic vision mode ────────────────────────────────
print("\n\n[4/4] Anthropic vision mode …")
try:
    if anthropic_provider is None:
        anthropic_provider = AnthropicProvider(model=ANTHROPIC_MODEL, temperature=0.0, max_tokens=2000)
    result_4 = anthropic_provider.extract_from_image(vision_images, prompt_vision_mode)
    validate_result("Anthropic / vision mode (OCR-free)", result_4)
except Exception as exc:
    print(f"  FAILED: {exc}")
    result_4 = None

# ── Summary ───────────────────────────────────────────────────────────
print("\n\n" + "=" * 70)
print("Summary")
print("=" * 70)
conditions = [
    ("OpenAI text", result_1),
    ("OpenAI vision", result_2),
    ("Anthropic text", result_3),
    ("Anthropic vision", result_4),
]
for label, r in conditions:
    if r is None:
        print(f"  {label:20s}  FAILED")
    else:
        t = r["token_usage"]
        print(
            f"  {label:20s}  tokens_in={t['input_tokens']:>6,}  "
            f"tokens_out={t['output_tokens']:>5,}  "
            f"latency={r['latency_ms']:>7,.0f} ms"
        )

print("\nDone.")
