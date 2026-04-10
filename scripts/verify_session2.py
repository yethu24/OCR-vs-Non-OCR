#!/usr/bin/env python
"""Session 2 verification — offline checks + online smoke tests.

Part 1 (offline): import validation, config wiring, prompt template,
    Pydantic schema compatibility, provider instantiation, registry.
    No API keys required.

Part 2 (online):  live 4-condition smoke test (1 bill × 2 providers × 2 modes)
    with structured-output validation, token-count sanity, and ground-truth
    spot-checks.  Requires OPENAI_API_KEY and ANTHROPIC_API_KEY in .env.

Usage:
    source .venv/Scripts/activate

    # run offline checks only (safe, free)
    python scripts/verify_session2.py --offline

    # run everything (costs a few cents)
    python scripts/verify_session2.py

    # override models for online tests
    OPENAI_E2E_MODEL=gpt-4o ANTHROPIC_E2E_MODEL=claude-3-5-sonnet \
        python scripts/verify_session2.py
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import textwrap
import traceback
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

# ── Counters ─────────────────────────────────────────────────────────
_passed = 0
_failed = 0
_errors: list[str] = []


def check(label: str, condition: bool, detail: str = "") -> None:
    """Record and print a single check result."""
    global _passed, _failed
    if condition:
        _passed += 1
        print(f"  [PASS] {label}")
    else:
        _failed += 1
        msg = f"  [FAIL] {label}"
        if detail:
            msg += f"  — {detail}"
        print(msg)
        _errors.append(f"{label}: {detail}")


def section(title: str) -> None:
    print(f"\n{'=' * 70}")
    print(f"  {title}")
    print(f"{'=' * 70}")


# =====================================================================
#  PART 1 — OFFLINE CHECKS (no API keys needed)
# =====================================================================

def run_offline_checks() -> None:
    section("1. Unit tests (pytest)")
    import subprocess

    r = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"],
        capture_output=True,
        text=True,
        cwd=str(project_root),
    )
    check("pytest exits 0", r.returncode == 0, r.stdout.split("\n")[-2] if r.stdout else r.stderr[-200:])

    # ── 2. Provider imports ──────────────────────────────────────────
    section("2. Provider imports")
    try:
        from src.llm.base import LLMProvider
        check("Import LLMProvider", True)
    except Exception as e:
        check("Import LLMProvider", False, str(e))

    try:
        from src.llm.openai_provider import OpenAIProvider
        check("Import OpenAIProvider", True)
    except Exception as e:
        check("Import OpenAIProvider", False, str(e))

    try:
        from src.llm.anthropic_provider import AnthropicProvider
        check("Import AnthropicProvider", True)
    except Exception as e:
        check("Import AnthropicProvider", False, str(e))

    try:
        from src.llm.registry import get_provider
        check("Import get_provider", True)
    except Exception as e:
        check("Import get_provider", False, str(e))

    # ── 3. Base class contract ───────────────────────────────────────
    section("3. LLMProvider base class contract")
    from src.llm.base import LLMProvider
    import inspect

    sig = inspect.signature(LLMProvider.__init__)
    params = list(sig.parameters.keys())
    check("__init__ has 'timeout' param", "timeout" in params)
    check("__init__ has 'max_retries' param", "max_retries" in params)
    check("__init__ has 'max_tokens' param", "max_tokens" in params)

    # Check abstract methods exist
    abstracts = {m for m in dir(LLMProvider) if getattr(getattr(LLMProvider, m, None), "__isabstractmethod__", False)}
    check("extract_from_text is abstract", "extract_from_text" in abstracts)
    check("extract_from_image is abstract", "extract_from_image" in abstracts)
    check("get_model_id is abstract", "get_model_id" in abstracts)
    check("encode_image_base64 exists", hasattr(LLMProvider, "encode_image_base64"))

    # ── 4. Provider instantiation (mock API key) ─────────────────────
    section("4. Provider instantiation with mock keys")

    os.environ["OPENAI_API_KEY"] = "sk-test-offline-check"
    os.environ["ANTHROPIC_API_KEY"] = "sk-ant-test-offline-check"

    from src.llm.openai_provider import OpenAIProvider
    from src.llm.anthropic_provider import AnthropicProvider

    oai = OpenAIProvider(model="gpt-4o", temperature=0.0, max_tokens=2000,
                         vision_detail="high", timeout=60, max_retries=1)
    check("OpenAI provider instantiated", True)
    check("  model = gpt-4o", oai.model == "gpt-4o")
    check("  vision_detail = high", oai.vision_detail == "high")
    check("  timeout = 60", oai.timeout == 60)
    check("  max_retries = 1", oai.max_retries == 1)
    check("  get_model_id() = openai/gpt-4o", oai.get_model_id() == "openai/gpt-4o")

    ant = AnthropicProvider(model="claude-sonnet-4-5-20250929", temperature=0.0,
                            max_tokens=2000, timeout=90, max_retries=3)
    check("Anthropic provider instantiated", True)
    check("  model = claude-sonnet-4-5-20250929", ant.model == "claude-sonnet-4-5-20250929")
    check("  timeout = 90", ant.timeout == 90)
    check("  max_retries = 3", ant.max_retries == 3)
    check("  get_model_id() = anthropic/claude-sonnet-4-5-20250929",
          ant.get_model_id() == "anthropic/claude-sonnet-4-5-20250929")

    # ── 5. Registry wiring ───────────────────────────────────────────
    section("5. Registry config wiring")
    from src.llm.registry import get_provider

    cfg_oai = {
        "llm": {
            "provider": "openai",
            "model": "gpt-4o",
            "temperature": 0.0,
            "max_tokens": 2000,
            "vision_detail": "auto",
            "timeout": 45,
            "max_retries": 5,
        }
    }
    p = get_provider(cfg_oai)
    check("Registry returns OpenAIProvider", type(p).__name__ == "OpenAIProvider")
    check("  vision_detail forwarded", p.vision_detail == "auto")
    check("  timeout forwarded", p.timeout == 45)
    check("  max_retries forwarded", p.max_retries == 5)

    cfg_ant = {
        "llm": {
            "provider": "anthropic",
            "model": "claude-sonnet-4-5-20250929",
            "temperature": 0.0,
            "max_tokens": 2000,
            "vision_detail": "high",
            "timeout": 120,
            "max_retries": 2,
        }
    }
    p2 = get_provider(cfg_ant)
    check("Registry returns AnthropicProvider", type(p2).__name__ == "AnthropicProvider")
    check("  timeout forwarded", p2.timeout == 120)

    # Bad provider name
    try:
        get_provider({"llm": {"provider": "gemini"}})
        check("Unknown provider raises ValueError", False, "No exception raised")
    except ValueError:
        check("Unknown provider raises ValueError", True)

    # ── 6. Prompt template ───────────────────────────────────────────
    section("6. Prompt template")
    from src.utils import load_prompt_template
    from src.schema import BillExtraction

    template = load_prompt_template(project_root / "prompts" / "extraction_v1.txt")
    check("Template loaded", len(template) > 0)
    check("Template has {schema_description}", "{schema_description}" in template)
    check("Template does NOT have {ocr_text}", "{ocr_text}" not in template)

    rendered = template.format(schema_description=BillExtraction.schema_description())
    check("Renders without error", True)
    check("No leftover placeholders", "{" not in rendered and "}" not in rendered,
          f"Found braces in rendered prompt")
    check("Contains 'provider_name'", "provider_name" in rendered)
    check("Contains 'total_amount_due'", "total_amount_due" in rendered)
    check("Contains all 12 field names",
          all(f in rendered for f in BillExtraction.SCHEMA_FIELDS))

    # ── 7. BillExtraction Pydantic schema ────────────────────────────
    section("7. BillExtraction Pydantic schema for structured output")

    schema = BillExtraction.model_json_schema()
    check("JSON schema generated", isinstance(schema, dict))
    check("  has 'properties'", "properties" in schema)
    check("  has 12 properties", len(schema["properties"]) == 12)

    # Check all 12 fields are in the schema
    for field in BillExtraction.SCHEMA_FIELDS:
        check(f"  field '{field}' in schema", field in schema["properties"])

    # Verify we can construct from a dict (simulating structured output)
    sample = {
        "provider_name": "OVO Energy",
        "utility_type": "electricity",
        "bill_number": "INV-001",
        "bill_date": "2024-01-15",
        "billing_period_start": "2023-12-01",
        "billing_period_end": "2024-01-01",
        "due_date": "2024-02-01",
        "total_amount_due": 125.50,
        "currency": "GBP",
        "account_number": "ACC-12345",
        "consumption_amount": 350.0,
        "consumption_unit": "kWh",
    }
    extraction = BillExtraction(**sample)
    check("BillExtraction from dict", extraction.provider_name == "OVO Energy")
    check("  serialises to JSON", isinstance(extraction.model_dump(mode="json"), dict))

    # All-null extraction (model returns all nulls)
    null_extraction = BillExtraction()
    check("All-null BillExtraction valid", null_extraction.provider_name is None)

    # ── 8. Config file ───────────────────────────────────────────────
    section("8. Config file (default.yaml)")
    from src.utils import load_config

    config = load_config(project_root / "config" / "default.yaml")
    llm = config["llm"]
    check("llm.vision_detail present", "vision_detail" in llm)
    check("  value = 'high'", llm["vision_detail"] == "high")
    check("llm.timeout present", "timeout" in llm)
    check("  value = 120", llm["timeout"] == 120)
    check("llm.max_retries present", "max_retries" in llm)
    check("  value = 2", llm["max_retries"] == 2)
    check("llm.structured_output present", "structured_output" in llm)

    # ── 9. Pipeline prompt rendering ─────────────────────────────────
    section("9. Pipeline prompt rendering (no OCR duplication)")

    # Simulate what pipeline.py does
    from src.schema import BillExtraction
    prompt_file = Path(config["llm"]["prompt_file"])
    tmpl = load_prompt_template(prompt_file)
    schema_desc = BillExtraction.schema_description()
    rendered_prompt = tmpl.format(schema_description=schema_desc)

    fake_ocr = "This is some OCR text from a bill TOTAL: £42.50"
    check("Rendered prompt does NOT contain OCR text",
          fake_ocr not in rendered_prompt)
    check("Rendered prompt length reasonable",
          500 < len(rendered_prompt) < 3000,
          f"length={len(rendered_prompt)}")

    # ── 10. OpenAI SDK — Responses API available ─────────────────────
    section("10. SDK capability checks")
    import openai
    check(f"OpenAI SDK version: {openai.__version__}", True)
    client = openai.OpenAI(api_key="sk-test")
    check("client.responses exists", hasattr(client, "responses"))
    check("client.responses.parse exists", hasattr(client.responses, "parse"))
    check("client.responses.create exists", hasattr(client.responses, "create"))

    import anthropic
    check(f"Anthropic SDK version: {anthropic.__version__}", True)
    aclient = anthropic.Anthropic(api_key="sk-ant-test")
    check("client.messages.parse exists", hasattr(aclient.messages, "parse"))

    # Check Responses API accepts text_format
    import inspect
    sig = inspect.signature(client.responses.parse)
    check("responses.parse has 'text_format' param", "text_format" in sig.parameters)
    check("responses.parse has 'instructions' param", "instructions" in sig.parameters)
    check("responses.parse has 'max_output_tokens' param", "max_output_tokens" in sig.parameters)

    # Check Anthropic messages.parse accepts output_format
    sig2 = inspect.signature(aclient.messages.parse)
    check("messages.parse has 'output_format' param", "output_format" in sig2.parameters)
    check("messages.parse has 'system' param", "system" in sig2.parameters)
    check("messages.parse has 'max_tokens' param", "max_tokens" in sig2.parameters)

    # Clean up mock keys
    if os.environ.get("OPENAI_API_KEY") == "sk-test-offline-check":
        del os.environ["OPENAI_API_KEY"]
    if os.environ.get("ANTHROPIC_API_KEY") == "sk-ant-test-offline-check":
        del os.environ["ANTHROPIC_API_KEY"]


# =====================================================================
#  PART 2 — ONLINE SMOKE TESTS (API keys required)
# =====================================================================

def run_online_checks() -> None:
    from src.env import load_env
    from src.utils import load_prompt_template, pdf_to_images, setup_logging
    from src.ocr.tesseract import TesseractOCR
    from src.schema import BillExtraction
    from src.llm.openai_provider import OpenAIProvider
    from src.llm.anthropic_provider import AnthropicProvider
    from src.performance import estimate_cost

    setup_logging()
    load_env()

    # Check that real API keys are set
    section("11. API key check")
    oai_key = os.environ.get("OPENAI_API_KEY", "")
    ant_key = os.environ.get("ANTHROPIC_API_KEY", "")
    check("OPENAI_API_KEY is set", len(oai_key) > 10 and oai_key != "sk-test-offline-check")
    check("ANTHROPIC_API_KEY is set", len(ant_key) > 10 and ant_key != "sk-ant-test-offline-check")

    if not oai_key or oai_key == "sk-test-offline-check":
        print("  !! Skipping online tests — no real OPENAI_API_KEY")
        return
    if not ant_key or ant_key == "sk-ant-test-offline-check":
        print("  !! Skipping online tests — no real ANTHROPIC_API_KEY")
        return

    # Config
    BILL_PDF = project_root / "data" / "bills" / "GB_electricity_ovo_001.pdf"
    GT_FILE = project_root / "data" / "ground_truth" / "GB_electricity_ovo_001.json"
    PROMPT_FILE = project_root / "prompts" / "extraction_v1.txt"
    OPENAI_MODEL = os.getenv("OPENAI_E2E_MODEL", "gpt-4o-mini")
    ANTHROPIC_MODEL = os.getenv("ANTHROPIC_E2E_MODEL", "claude-sonnet-4-6")

    print(f"\n  Models: OpenAI={OPENAI_MODEL}, Anthropic={ANTHROPIC_MODEL}")
    print(f"  Bill:   {BILL_PDF.name}")

    # Shared prep
    template = load_prompt_template(PROMPT_FILE)
    prompt = template.format(schema_description=BillExtraction.schema_description())
    gt = json.loads(GT_FILE.read_text(encoding="utf-8"))["fields"]
    all_images = pdf_to_images(BILL_PDF, dpi=200)
    vision_images = all_images[:2]

    ocr_engine = TesseractOCR()
    ocr_texts = [ocr_engine.extract_text(img, language="en") for img in all_images]
    ocr_text = "\n\n".join(ocr_texts)

    # Helper to validate a single result
    def validate(label: str, result: dict, provider_name: str, model: str) -> None:
        section(label)
        raw = result["raw_output"]
        tokens = result["token_usage"]
        latency = result["latency_ms"]

        # Return contract checks
        check("raw_output is non-empty str", isinstance(raw, str) and len(raw) > 0)
        check("token_usage has input_tokens", "input_tokens" in tokens)
        check("token_usage has output_tokens", "output_tokens" in tokens)
        check("input_tokens > 0", tokens["input_tokens"] > 0,
              f"got {tokens.get('input_tokens')}")
        check("output_tokens > 0", tokens["output_tokens"] > 0,
              f"got {tokens.get('output_tokens')}")
        check("latency_ms > 0", latency > 0, f"got {latency}")

        print(f"  Tokens: in={tokens['input_tokens']:,}  out={tokens['output_tokens']:,}")
        print(f"  Latency: {latency:,.0f} ms")

        # Cost estimation still works
        cost = estimate_cost(provider_name, model,
                             tokens["input_tokens"], tokens["output_tokens"])
        check("estimate_cost returns float >= 0", isinstance(cost, float) and cost >= 0,
              f"got {cost}")
        print(f"  Est. cost: ${cost:.6f}")

        # JSON validity — structured output should produce clean JSON
        try:
            parsed = json.loads(raw)
            check("raw_output is valid JSON", True)
        except json.JSONDecodeError as exc:
            check("raw_output is valid JSON", False, str(exc))
            print(f"  Raw (first 300 chars): {raw[:300]}")
            return

        # Schema completeness
        missing = [f for f in BillExtraction.SCHEMA_FIELDS if f not in parsed]
        check("All 12 fields present", len(missing) == 0,
              f"missing: {missing}" if missing else "")

        # Can construct BillExtraction from parsed output
        try:
            extraction = BillExtraction(**parsed)
            check("BillExtraction(**parsed) succeeds", True)
        except Exception as exc:
            check("BillExtraction(**parsed) succeeds", False, str(exc))

        # Ground-truth spot checks
        for field in ["total_amount_due", "currency", "provider_name"]:
            expected = gt.get(field)
            actual = parsed.get(field)
            match = str(actual) == str(expected)
            check(f"Spot-check {field}: {actual}",
                  match or expected is None,
                  f"expected {expected}" if not match else "")

        # Print full extraction
        print(f"\n  Full extraction:")
        for k, v in parsed.items():
            print(f"    {k}: {v}")

    # ── Condition 1: OpenAI text ─────────────────────────────────────
    print(f"\n\n{'#' * 70}")
    print(f"  ONLINE TEST: OpenAI text mode ({OPENAI_MODEL})")
    print(f"{'#' * 70}")
    try:
        oai_provider = OpenAIProvider(model=OPENAI_MODEL, temperature=0.0, max_tokens=2000)
        result_1 = oai_provider.extract_from_text(ocr_text, prompt)
        validate("12. OpenAI text mode — return contract", result_1, "openai", OPENAI_MODEL)
    except Exception as exc:
        section("12. OpenAI text mode")
        check("OpenAI text mode call succeeded", False, f"{type(exc).__name__}: {exc}")
        traceback.print_exc()
        result_1 = None

    # ── Condition 2: OpenAI vision ───────────────────────────────────
    print(f"\n\n{'#' * 70}")
    print(f"  ONLINE TEST: OpenAI vision mode ({OPENAI_MODEL})")
    print(f"{'#' * 70}")
    try:
        if result_1 is None:
            oai_provider = OpenAIProvider(model=OPENAI_MODEL, temperature=0.0, max_tokens=2000)
        result_2 = oai_provider.extract_from_image(vision_images, prompt)
        validate("13. OpenAI vision mode — return contract", result_2, "openai", OPENAI_MODEL)
    except Exception as exc:
        section("13. OpenAI vision mode")
        check("OpenAI vision mode call succeeded", False, f"{type(exc).__name__}: {exc}")
        traceback.print_exc()
        result_2 = None

    # ── Condition 3: Anthropic text ──────────────────────────────────
    print(f"\n\n{'#' * 70}")
    print(f"  ONLINE TEST: Anthropic text mode ({ANTHROPIC_MODEL})")
    print(f"{'#' * 70}")
    try:
        ant_provider = AnthropicProvider(model=ANTHROPIC_MODEL, temperature=0.0, max_tokens=2000)
        result_3 = ant_provider.extract_from_text(ocr_text, prompt)
        validate("14. Anthropic text mode — return contract", result_3, "anthropic", ANTHROPIC_MODEL)
    except Exception as exc:
        section("14. Anthropic text mode")
        check("Anthropic text mode call succeeded", False, f"{type(exc).__name__}: {exc}")
        traceback.print_exc()
        result_3 = None

    # ── Condition 4: Anthropic vision ────────────────────────────────
    print(f"\n\n{'#' * 70}")
    print(f"  ONLINE TEST: Anthropic vision mode ({ANTHROPIC_MODEL})")
    print(f"{'#' * 70}")
    try:
        if result_3 is None:
            ant_provider = AnthropicProvider(model=ANTHROPIC_MODEL, temperature=0.0, max_tokens=2000)
        result_4 = ant_provider.extract_from_image(vision_images, prompt)
        validate("15. Anthropic vision mode — return contract", result_4, "anthropic", ANTHROPIC_MODEL)
    except Exception as exc:
        section("15. Anthropic vision mode")
        check("Anthropic vision mode call succeeded", False, f"{type(exc).__name__}: {exc}")
        traceback.print_exc()
        result_4 = None

    # ── Cross-provider comparison ────────────────────────────────────
    section("16. Cross-provider comparison")
    results = {
        "OpenAI text": result_1,
        "OpenAI vision": result_2,
        "Anthropic text": result_3,
        "Anthropic vision": result_4,
    }

    succeeded = {k: v for k, v in results.items() if v is not None}
    check(f"{len(succeeded)}/4 conditions succeeded", len(succeeded) == 4,
          f"failed: {[k for k, v in results.items() if v is None]}")

    if succeeded:
        print(f"\n  {'Condition':<22s} {'Tokens In':>10s} {'Tokens Out':>10s} {'Latency':>10s}")
        print(f"  {'-' * 54}")
        for label, r in results.items():
            if r:
                t = r["token_usage"]
                print(
                    f"  {label:<22s} {t['input_tokens']:>10,} {t['output_tokens']:>10,}"
                    f" {r['latency_ms']:>9,.0f}ms"
                )
            else:
                print(f"  {label:<22s}  {'FAILED':>30s}")

    # Token sanity: text mode should NOT have doubled tokens
    if result_1 and result_2:
        text_in = result_1["token_usage"]["input_tokens"]
        vision_in = result_2["token_usage"]["input_tokens"]
        # Text mode should be reasonably sized, not 2x the prompt
        check("OpenAI text tokens not abnormally high",
              text_in < vision_in * 3,
              f"text={text_in}, vision={vision_in}")


# =====================================================================
#  MAIN
# =====================================================================

def main() -> None:
    parser = argparse.ArgumentParser(description="Session 2 verification suite")
    parser.add_argument("--offline", action="store_true",
                        help="Run only offline checks (no API calls)")
    args = parser.parse_args()

    print("=" * 70)
    print("  SESSION 2 VERIFICATION SUITE")
    print("=" * 70)

    run_offline_checks()

    if not args.offline:
        run_online_checks()
    else:
        print("\n  (Skipping online tests — use without --offline to run them)")

    # ── Final report ─────────────────────────────────────────────────
    section("FINAL REPORT")
    total = _passed + _failed
    print(f"\n  Total checks: {total}")
    print(f"  Passed:       {_passed}")
    print(f"  Failed:       {_failed}")

    if _errors:
        print(f"\n  Failures:")
        for e in _errors:
            print(f"    - {e}")

    print()
    if _failed == 0:
        print("  *** ALL CHECKS PASSED ***")
    else:
        print(f"  *** {_failed} CHECK(S) FAILED ***")

    sys.exit(0 if _failed == 0 else 1)


if __name__ == "__main__":
    main()
