# OCR vs Non-OCR — Utility Bill Extraction Pipeline

Comparative study of OCR-based vs OCR-free template-free extraction applied to utility bills (electricity, gas, water). BSc Computer Science dissertation project.

See [SPEC.md](SPEC.md) for full architecture, evaluation methodology, and implementation roadmap.

## Prerequisites

- Python 3.10+
- [Poppler](https://poppler.freedesktop.org/) (system binary, required by `pdf2image`)
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) (system binary, required by `pytesseract`) with language packs: `eng`, `deu`, `fra`, `ita`

## Setup

### 1. Clone / open the project

```bash
cd "c:\Users\winye\OCR vs Non-OCR"
```

### 2. Create a virtual environment

```bash
python -m venv .venv
source .venv/Scripts/activate   # Windows bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Verify system dependencies

```bash
# Poppler
pdfinfo -v

# Tesseract
tesseract --version
tesseract --list-langs   # should include eng, deu, fra, ita
```

### 4. Verify Python dependencies

```bash
python -c "import yaml, pydantic, pdf2image, PIL, pytesseract; print('ok')"
```

## Running Tests

```bash
python -m pytest tests/ -v
```

## Dev E2E Smoke Test (LLM calls; costs money)

This project includes a manual end-to-end dev test script: `scripts/test_llm_e2e.py`.

- **Defaults (cost-control / dev)**:
  - OpenAI: `gpt-4o-mini`
  - Anthropic: `claude-3-5-haiku`
- **Override to baseline models** (locked for experiments in `SPEC.md`):

```bash
OPENAI_E2E_MODEL=gpt-4o ANTHROPIC_E2E_MODEL=claude-3-5-sonnet python scripts/test_llm_e2e.py
```

Run with defaults:

```bash
python scripts/test_llm_e2e.py
```

## Project Layout

```
config/              YAML pipeline configs
prompts/             Versioned prompt templates
src/                 Source modules (schema, loader, OCR, LLM, normalisation, evaluation)
data/
  dataset_manifest.csv   Document metadata (single source of truth)
  bills/                 PDFs ({document_id}.pdf)
  ground_truth/          Annotations ({document_id}.json)
results/
  runs/                  Per-run output directories
  reports/               Comparative analysis outputs
tests/               Unit and integration tests
cli.py               Main CLI entry point
SPEC.md              Full specification and architecture
```

## Adding Documents

1. Place the PDF in `data/bills/` named `{document_id}.pdf`.
2. Add a row to `data/dataset_manifest.csv` with the document metadata.
3. Create a ground truth file at `data/ground_truth/{document_id}.json`:

```json
{
  "document_id": "GB_electricity_ovo_001",
  "annotated_by": "student",
  "annotation_date": "2026-03-30",
  "fields": {
    "provider_name": "OVO Energy Ltd",
    "utility_type": "electricity",
    "bill_number": null,
    "bill_date": "2026-03-10",
    "billing_period_start": "2025-12-18",
    "billing_period_end": "2026-01-17",
    "due_date": null,
    "total_amount_due": 177.53,
    "currency": "GBP",
    "account_number": "26447122",
    "consumption_amount": 572.502,
    "consumption_unit": "kWh"
  }
}
```

4. Set `annotated=true` and `verified=true` in the manifest row once the ground truth is complete and checked.

## Usage (CLI)

```bash
# Run extraction pipeline (manifest path from config)
python cli.py run --config config/experiments/gpt4o_text.yaml

# Override pipeline mode or model via CLI
python cli.py run --config config/default.yaml --mode vision --provider openai --model gpt-4o

# Force re-run (ignore cached results)
python cli.py run --config config/default.yaml --force

# Evaluate a completed run
python cli.py evaluate --run-dir results/runs/20260401_120000_openai_gpt4o_text/

# Compare multiple runs
python cli.py compare --runs results/runs/...text/ results/runs/...vision/

# Generate report
python cli.py report --runs-dir results/runs/ --output results/reports/
```

## Configuration

Default config: `config/default.yaml`. Experiment overrides go in `config/experiments/`.

Key settings:
- `pipeline.mode`: `"ocr_text"` or `"vision"`
- `llm.provider` / `llm.model`: which LLM backend to use
- `llm.prompt_file`: path to the prompt template
- `data.manifest`: path to the dataset manifest CSV

## Notes

- **Provider name suffixes**: Bills often include legal suffixes (e.g., "Acque Veronesi s.c. a r.l."). Ground truth uses the canonical name as determined by the annotator. Evaluation reports both exact match and Levenshtein similarity to account for this.
- **OCR language**: Tesseract language is set per document from the manifest `language` column, not globally. A single run can process bills in multiple languages.
