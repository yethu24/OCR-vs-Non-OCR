# OCR vs Non-OCR — Utility Bill Extraction Pipeline

Controlled experimental comparison of OCR-based (text-mediated) and OCR-free (vision-mediated) structured data extraction from multilingual utility bills (electricity, gas, water). BSc Computer Science dissertation project.

See [SPEC.md](SPEC.md) for the full architecture, evaluation methodology, and module reference.

---

## Prerequisites

- Python 3.10+
- [Poppler](https://poppler.freedesktop.org/) — system binary required by `pdf2image` for PDF rasterisation
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) — system binary required by `pytesseract`, with language packs: `eng`, `deu`, `fra`, `ita`

---

## Setup

### 1. Open the project directory

```bash
cd "OCR vs Non-OCR"
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/Scripts/activate   # Windows (Git Bash / bash)
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Configure API keys

Create a `.env` file in the project root:

```
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

### 4. Verify system dependencies

```bash
# Poppler
pdfinfo -v

# Tesseract + language packs
tesseract --version
tesseract --list-langs   # must include eng, deu, fra, ita
```

### 5. Verify Python dependencies

```bash
python -c "import yaml, pydantic, pdf2image, PIL, pytesseract; print('ok')"
```

---

## Running Tests

```bash
python -m pytest tests/ -v
```

---

## Usage

The pipeline is controlled entirely through `cli.py`. There are four commands: `run`, `evaluate`, `compare`, and `report`.

### Run the extraction pipeline

```bash
# Use defaults from config/default.yaml (vision mode, Anthropic Claude)
python cli.py run --config config/default.yaml

# Override mode and model via CLI flags
python cli.py run --config config/default.yaml --mode ocr_text --provider openai --model gpt-4o

# Force re-processing of all documents (ignore cached extraction.json files)
python cli.py run --config config/default.yaml --force
```

Each run produces a uniquely named output directory under `results/runs/` in the format `{timestamp}_{provider}_{model}_{mode}` (e.g. `20260429_204310_anthropic_claudesonnet4520250929_vision`). The exact name depends on when and how the run is executed.

### Evaluate a completed run

```bash
# Basic evaluation (overall accuracy, field-level accuracies)
python cli.py evaluate --run-dir results/runs/<your-run-directory>/

# With failure diagnosis (attributes incorrect fields to OCR failure vs LLM failure)
python cli.py evaluate --run-dir results/runs/<your-run-directory>/ --diagnose
```

### Compare multiple runs

Pass `--runs` once per run directory. Designed for the 2x2 factorial matrix (four runs):

```bash
python cli.py compare \
  --runs results/runs/<run-1-directory>/ \
  --runs results/runs/<run-2-directory>/ \
  --runs results/runs/<run-3-directory>/ \
  --runs results/runs/<run-4-directory>/ \
  --output results/reports/
```

Writes `results/reports/comparison.json`.

### Generate charts and text summary

```bash
python cli.py report \
  --comparison results/reports/comparison.json \
  --output results/reports/
```

Writes six PNG charts to `results/reports/figures/` and a text summary to `results/reports/summary.txt`.

---

## Project Layout

```
config/
  default.yaml              Default pipeline configuration
prompts/
  extraction_v1.txt         LLM prompt template
src/
  schema.py                 BillExtraction, PipelineResult, DocumentEntry
  pipeline.py               Batch pipeline orchestrator
  dataset_loader.py         Manifest validation and document resolution
  normalisation.py          Field normalisers shared by pipeline and evaluation
  performance.py            Timer context manager and cost estimation
  reporting.py              Chart generation and text summary
  utils.py                  Config loading, PDF conversion, file I/O
  env.py                    .env file loading
  llm/                      LLM provider implementations (OpenAI, Anthropic)
  ocr/                      OCR engine implementations (Tesseract)
  evaluation/               Metrics, failure diagnosis, cross-run comparison
data/
  dataset_manifest.csv      Document registry (single source of truth)
  bills/                    PDF files — {document_id}.pdf
  ground_truth/             Annotation files — {document_id}.json
results/
  runs/                     Per-run output directories
  reports/                  Comparative analysis outputs
tests/                      Automated tests (237+ across 12 files)
cli.py                      CLI entry point
SPEC.md                     Full specification and architecture reference
README.md                   This file
```

---

## Configuration

The default configuration lives in `config/default.yaml`. All settings can be overridden via CLI flags on the `run` command without editing the file.

Key settings:

| Key | Default | Description |
|-----|---------|-------------|
| `pipeline.mode` | `"vision"` | `"ocr_text"` or `"vision"` |
| `llm.provider` | `"anthropic"` | `"openai"` or `"anthropic"` |
| `llm.model` | `"claude-sonnet-4-5-20250929"` | Provider-specific model name |
| `llm.temperature` | `0.0` | LLM sampling temperature |
| `llm.max_tokens` | `2000` | Maximum output tokens |
| `llm.prompt_file` | `"prompts/extraction_v1.txt"` | Path to prompt template |
| `llm.vision_detail` | `"high"` | OpenAI image detail level (`"low"`, `"high"`, `"auto"`) |
| `data.manifest` | `"data/dataset_manifest.csv"` | Path to manifest CSV |

---

## Adding Documents

1. Place the PDF in `data/bills/` named `{document_id}.pdf`.
2. Add a row to `data/dataset_manifest.csv` with the document metadata.
3. Create the ground truth file at `data/ground_truth/{document_id}.json`:

```json
{
  "document_id": "gb_electricity_ovo_001",
  "annotated_by": "student",
  "annotation_date": "2026-03-30",
  "fields": {
    "provider_name": "OVO Energy",
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

4. Set `annotated=true` and `verified=true` in the manifest row once the ground truth has been created and checked.

The document will be included in subsequent runs automatically (the `DatasetLoader` filters to `status=active AND annotated=true AND verified=true`).

---

## Notes

- **OCR language**: Tesseract language is set per document from the manifest `language` column. A single run can process bills in multiple languages simultaneously.
- **Resume mode**: If a run is interrupted, re-running the same command skips documents that already have `extraction.json` output. Use `--force` to override this.
- **Provider name normalisation**: Legal suffixes (e.g. "s.c. a r.l.", "GmbH", "Ltd") are stripped from `provider_name` during normalisation. Ground truth files use the canonical name without suffixes.
