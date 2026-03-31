# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A BSc Computer Science dissertation project comparing OCR-based vs OCR-free (vision-based) extraction pipelines for utility bills (electricity, gas, water). The core research question: does explicit OCR preprocessing (Tesseract) help or hurt LLM extraction accuracy compared to direct visual input?

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

### Run Tests
```bash
python -m pytest tests/ -v          # All 51 tests
python -m pytest tests/test_schema.py -v    # Single file
python -m pytest tests/ -k "test_normalise_date" -v  # Single test
```

### Verify System Dependencies
```bash
tesseract --version && tesseract --list-langs  # Must include eng, deu, fra, ita
pdfinfo -v  # Poppler
```

## Architecture

### Pipeline Flow
```
PDF → pdf_to_images() → [OCR path: TesseractOCR → text] OR [Vision path: skip]
                      → LLM Provider → JSON → normalise_extraction() → PipelineResult
                      → per-document disk write → evaluation metrics
```

### Key Design Patterns

**Strategy pattern for providers:** `OCREngine` (ABC in `src/ocr/base.py`) → `TesseractOCR`. Planned: `LLMProvider` ABC → `OpenAIProvider`, `GoogleProvider`, `AnthropicProvider`.

**Manifest-driven dataset:** `data/dataset_manifest.csv` is the single source of truth. `DatasetLoader.load_and_validate()` filters to `status=active AND annotated=true AND verified=true`, resolves file paths, and verifies existence.

**Config-as-code:** `config/default.yaml` controls all pipeline behaviour. CLI overrides deep-merge into the base config via `load_config()`. No hardcoded model names, paths, or API keys.

**Prompt-as-config:** `prompts/extraction_v1.txt` is a template with `{schema_description}` and `{ocr_text}` placeholders. Prompt is injected at runtime, not hardcoded.

**Per-document persistence:** After each document, results are written to `results/runs/{run_id}/documents/{document_id}/`. Files: `extraction.json`, `raw_llm_output.txt`, `ocr_text.txt` (OCR mode only), `timings.json`, `metadata.json`. This enables crash recovery; skip if `extraction.json` exists unless `--force`.

### Module Map

| Module | Purpose |
|---|---|
| `src/schema.py` | Pydantic models: `BillExtraction` (12 canonical fields, all optional), `PipelineResult`, `DocumentEntry` |
| `src/dataset_loader.py` | Manifest validation, filtering, file path resolution |
| `src/normalisation.py` | Per-field normalisation applied identically to predictions and ground truth before comparison |
| `src/utils.py` | `load_config`, `pdf_to_images` (via pdf2image+Poppler), file I/O, logging |
| `src/env.py` | Loads `.env` for `OPENAI_API_KEY`, `ANTHROPIC_API_KEY` |
| `src/ocr/` | `OCREngine` ABC + `TesseractOCR` (language mapping: `en→eng`, `de→deu`, `fr→fra`, `it→ita`) |
| `src/llm/base.py` | `LLMProvider` ABC: `extract_from_text`, `extract_from_image`, `get_model_id`, `encode_image_base64` |
| `src/llm/openai_provider.py` | `OpenAIProvider` — GPT-4o text + vision modes, JSON response format, token tracking |
| `src/llm/anthropic_provider.py` | `AnthropicProvider` — Claude text + vision modes, JSON fence stripping, token tracking |
| `src/llm/registry.py` | `get_provider(config)` factory — maps config string to provider class |
| `src/evaluation/` | Stubs only — Session 4 |

### Canonical Schema (`BillExtraction`)
12 optional fields: `provider_name`, `utility_type`, `bill_number`, `bill_date`, `billing_period_start`, `billing_period_end`, `due_date`, `total_amount_due`, `currency`, `account_number`, `consumption_amount`, `consumption_unit`.

### Normalisation Rules
- Dates → ISO 8601 (`YYYY-MM-DD`), 10 input formats supported
- Currency → uppercase ISO 4217 (e.g., `EUR`, `GBP`)
- Floats → rounded to 2 decimal places
- Strings → lowercase, stripped, whitespace collapsed
- Null/missing → preserved as `None`

## Dataset

5 documents (2 English, 3 Italian), all active/annotated/verified:

| document_id | language | utility_type | provider |
|---|---|---|---|
| GB_electricity_ovo_001 | en | electricity | OVO Energy |
| GB_water_thameswater_001 | en | water | Thames Water |
| IT_electricity_lupatotina_001 | it | electricity | Lupatotina Gas e Luce SRL |
| IT_gas_lupatotina_001 | it | gas | Lupatotina Gas e Luce SRL |
| IT_water_acqueveronesi_001 | it | water | Acque Veronesi |

Ground truth JSON files in `data/ground_truth/{document_id}.json` — 12-field extractions verified manually.

## Experimental Design (2×2 Factorial)

- Model A: GPT-4o (OpenAI)
- Model B: Claude 3.5 Sonnet (Anthropic)
- Mode 1: OCR-based (Tesseract → text → LLM)
- Mode 2: Vision-based (images → LLM directly)

**Fixed across all runs:** Vision input uses first 2 pages only. Same prompt template. Per-document language from manifest.

### Dev vs baseline models

- **Baseline (dissertation runs)**: use the locked baseline models from `SPEC.md` (OpenAI `gpt-4o`, Anthropic `claude-3-5-sonnet`).\n+- **Development / smoke testing**: prefer cheaper models to control costs. `scripts/test_llm_e2e.py` defaults to:\n+  - OpenAI: `gpt-4o-mini`\n+  - Anthropic: `claude-3-5-haiku`\n+\n+Override models for the script via env vars:\n+```\n+OPENAI_E2E_MODEL=gpt-4o\n+ANTHROPIC_E2E_MODEL=claude-3-5-sonnet\n+```\n+
## Implementation Roadmap

- **Session 1** (done): Schema, dataset loader, normalisation, OCR engine, utils — 51 tests passing
- **Session 2** (done): LLM providers (OpenAI, Anthropic) + registry + e2e test script — blocked on API credits for live validation
- **Session 3**: Pipeline orchestrator + `cli.py` (`run` command)
- **Session 4**: Evaluation metrics (field/document accuracy, Levenshtein, cost tracking)
- **Session 5**: Run the 4 experimental conditions
- **Session 6**: Analysis, visualisation, report generation
- **Session 7**: Polish + buffer

## Configuration Reference

Key fields in `config/default.yaml`:
- `pipeline.mode`: `"ocr_text"` or `"vision"`
- `llm.provider`: `"openai"`, `"google"`, or `"anthropic"`
- `llm.model`: provider-specific model ID
- `llm.structured_output`: use JSON schema enforcement where available
- `output.save_intermediate`: write per-stage outputs to disk

## API Keys

Store in `.env` (gitignored):
```
OPENAI_API_KEY=...
ANTHROPIC_API_KEY=...
```

Loaded via `src/env.load_env()`.
