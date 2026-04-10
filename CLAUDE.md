# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A BSc Computer Science dissertation project comparing OCR-based vs OCR-free (vision-based) extraction pipelines for utility bills (electricity, gas, water).

**Two pipeline modes:**
- **OCR-based:** PDF → images → Tesseract → text → LLM (text mode)
- **Vision-based:** PDF → images → LLM (vision mode) directly

## Commands

### Setup (Windows bash)
```bash
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
```

### Run tests
```bash
python -m pytest tests/ -v
```

### Run the pipeline
```bash
python cli.py run --config config/default.yaml
python cli.py run --config config/default.yaml --mode vision --provider openai --model gpt-4o
python cli.py run --config config/default.yaml --force  # re-process all docs
```

### Evaluate a run
```bash
python cli.py evaluate --run-dir results/runs/20260402_162321_openai_gpt4o_ocr_text/
python cli.py evaluate --run-dir results/runs/... --diagnose  # with failure attribution
```

### Compare runs
```bash
python cli.py compare \
  --runs results/runs/...gpt4o_ocr_text \
  --runs results/runs/...gpt4o_vision \
  --runs results/runs/...claude_ocr_text \
  --runs results/runs/...claude_vision
```

### Generate report (charts + summary)
```bash
python cli.py report                          # uses results/reports/comparison.json
python cli.py report --comparison results/reports/comparison.json --output results/reports
```

### Verify system dependencies
```bash
tesseract --version && tesseract --list-langs  # Must include eng, deu, fra, ita
pdfinfo -v  # Poppler
```

## Architecture

### Pipeline flow
```
PDF → pdf_to_images() → [OCR path: TesseractOCR → text] OR [Vision path: skip]
                      → LLM Provider (.parse + Pydantic) → BillExtraction
                      → normalise_extraction() → PipelineResult
                      → per-document disk write → evaluation metrics
```

### Key design patterns

- **Manifest-driven dataset:** `data/dataset_manifest.csv` is the single source of truth.
- **Config-as-code:** `config/default.yaml` controls pipeline behaviour; CLI overrides deep-merge into it.
- **Prompt-as-config:** `prompts/extraction_v1.txt` contains only instructions and `{schema_description}` — raw data (OCR text or images) is passed separately in the user message to avoid duplicating input tokens.
- **Structured Outputs (OpenAI):** OpenAI uses `responses.parse` with `text_format=BillExtraction` for schema-guaranteed JSON.  Anthropic uses prompt-instructed JSON with `_strip_json_fencing()` post-processing (Anthropic's structured output rejects the `BillExtraction` schema as too complex across model tiers).
- **Provider registry:** `src/llm/registry.py` selects the provider from config.

### Module map

| Module | Purpose |
|---|---|
| `src/schema.py` | Canonical 12-field schema (`BillExtraction`) and result containers |
| `src/dataset_loader.py` | Manifest validation, filtering, path resolution |
| `src/normalisation.py` | Field normalisation for predictions + ground truth: NFC strings; date/`strptime`; currency map + 3-letter ISO; utility_type and consumption_unit synonym maps; EU/US numeric strings; `normalise_extraction()` + `FIELD_NORMALISERS` |
| `src/utils.py` | Config load/merge, `pdf_to_images`, file I/O, logging |
| `src/env.py` | Loads `.env` for API keys |
| `src/ocr/` | `OCREngine` ABC + `TesseractOCR` |
| `src/llm/base.py` | `LLMProvider` ABC (`timeout`, `max_retries`) + base64 image helper |
| `src/llm/openai_provider.py` | OpenAI Responses API provider (`responses.parse`, Structured Outputs, `instructions` param, `input_image` vision, configurable `detail`) |
| `src/llm/anthropic_provider.py` | Anthropic Messages API provider (`messages.create`, prompt-instructed JSON, `_strip_json_fencing`, `system` param) |
| `src/llm/registry.py` | `get_provider(config)` factory — passes `vision_detail`, `timeout`, `max_retries` |
| `src/performance.py` | `Timer` context manager, `estimate_cost`, system snapshots |
| `src/pipeline.py` | Pipeline orchestrator: JSON parsing, per-doc processing, batch run |
| `src/evaluation/metrics.py` | `compare_field`, `evaluate_document`, `evaluate_run` with null table + Levenshtein |
| `src/evaluation/diagnosis.py` | Failure attribution: OCR failure vs LLM extraction vs normalisation vs inference |
| `src/evaluation/comparator.py` | Cross-run comparison: accuracy/performance matrices, slice tables |
| `src/reporting.py` | `generate_report`: reads `comparison.json`, outputs 6 charts (PNG) + `summary.txt` |
| `cli.py` | Click CLI with `run`, `evaluate`, `compare`, `report` commands |

## Experimental design (2×2)

- **Model A (baseline):** OpenAI `gpt-4o`
- **Model B (baseline):** Anthropic `claude-sonnet-4-5-20250929`
- **Mode 1:** OCR-based (Tesseract → text → LLM)
- **Mode 2:** Vision-based (images → LLM directly)

**Fixed across baseline runs:** vision input uses first 2 pages only; same prompt template; per-document language from manifest.

### Dev vs baseline models

- **Baseline (dissertation runs):** OpenAI `gpt-4o`, Anthropic `claude-3-5-sonnet` (locked in `SPEC.md`).
- **Development / smoke testing:** use cheaper models. `scripts/test_llm_e2e.py` defaults to:
  - OpenAI: `gpt-4o-mini`
  - Anthropic: `claude-3-haiku-20240307` (example; use whatever Haiku model ID works for your account)

Override models for the dev script via env vars:

```bash
OPENAI_E2E_MODEL=gpt-4o ANTHROPIC_E2E_MODEL=claude-3-5-sonnet python scripts/test_llm_e2e.py
```

## Implementation roadmap

- **Session 1 (done):** schema, dataset loader, normalisation, OCR, utils
- **Session 2 (done):** OpenAI (Responses API + Structured Outputs) + Anthropic (Messages API + JSON fence stripping) providers, registry, dev e2e smoke test script
- **Session 3 (done):** pipeline orchestrator (`src/pipeline.py`), CLI `run` command (`cli.py`), performance tracking (`src/performance.py`), JSON parsing hardening
- **Session 4 (done):** evaluation module (`src/evaluation/metrics.py`, `diagnosis.py`, `comparator.py`), CLI `evaluate` + `compare` commands, 30 evaluation tests
- **Session 5 (done):** ran 4 experimental conditions (GPT-4o × OCR/Vision, Sonnet 4.5 × OCR/Vision) on 5 documents, evaluated + diagnosed + compared
- **Session 6 (done):** `src/reporting.py` — 6 charts (accuracy bar, field heatmap, timing stacked bar, cost bar, language grouped bar, utility type grouped bar) + text summary; CLI `report` command
