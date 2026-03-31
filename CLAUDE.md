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

### Verify system dependencies
```bash
tesseract --version && tesseract --list-langs  # Must include eng, deu, fra, ita
pdfinfo -v  # Poppler
```

## Architecture

### Pipeline flow
```
PDF → pdf_to_images() → [OCR path: TesseractOCR → text] OR [Vision path: skip]
                      → LLM Provider → JSON → normalise_extraction() → PipelineResult
                      → per-document disk write → evaluation metrics
```

### Key design patterns

- **Manifest-driven dataset:** `data/dataset_manifest.csv` is the single source of truth.
- **Config-as-code:** `config/default.yaml` controls pipeline behaviour; CLI overrides deep-merge into it.
- **Prompt-as-config:** `prompts/extraction_v1.txt` is injected at runtime; providers do not build prompts.
- **Provider registry:** `src/llm/registry.py` selects the provider from config.

### Module map

| Module | Purpose |
|---|---|
| `src/schema.py` | Canonical 12-field schema (`BillExtraction`) and result containers |
| `src/dataset_loader.py` | Manifest validation, filtering, path resolution |
| `src/normalisation.py` | Field normalisation for predictions + ground truth |
| `src/utils.py` | Config load/merge, `pdf_to_images`, file I/O, logging |
| `src/env.py` | Loads `.env` for API keys |
| `src/ocr/` | `OCREngine` ABC + `TesseractOCR` |
| `src/llm/base.py` | `LLMProvider` ABC + base64 image helper |
| `src/llm/openai_provider.py` | OpenAI provider (text + vision), token/latency tracking |
| `src/llm/anthropic_provider.py` | Anthropic provider (text + vision), token/latency tracking |
| `src/llm/registry.py` | `get_provider(config)` factory |

## Experimental design (2×2)

- **Model A (baseline):** OpenAI `gpt-4o`
- **Model B (baseline):** Anthropic `claude-3-5-sonnet`
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
- **Session 2 (done):** OpenAI + Anthropic providers, registry, dev e2e smoke test script
- **Session 3:** pipeline orchestrator + CLI run command; JSON parsing hardening (handle prose before JSON)
- **Session 4:** evaluation + reporting

