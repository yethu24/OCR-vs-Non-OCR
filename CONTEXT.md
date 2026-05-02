# Technical Context Document: OCR-Based vs OCR-Free Template-Free Extraction

## 1. System Overview

### 1.1 What the System Does

This system is a controlled experimental framework for comparing two paradigms of structured data extraction from semi-structured documents --- specifically, multilingual utility bills. The end-to-end pipeline ingests a PDF utility bill (electricity, gas, or water), extracts 12 predefined structured fields into a canonical JSON schema, and evaluates the extraction against human-annotated ground truth.

The two paradigms under comparison are:

- **OCR-based (text-mediated)**: PDF pages are rasterised to images, processed by the Tesseract OCR engine to produce raw text, and that text is sent to a Large Language Model (LLM) in text mode for structured extraction.
- **OCR-free (vision-mediated)**: The same rasterised page images are sent directly to a Vision-Language Model (VLM) in vision mode, bypassing OCR entirely.

The critical design constraint is that the LLM reasoning layer is held constant across both pipelines. The same model, the same prompt, and the same post-processing are used; only the input modality (OCR-derived text vs raw page images) varies. This isolates input modality as the single independent variable, enabling controlled empirical comparison.

### 1.2 Core Problem

Automated extraction of structured data from semi-structured documents is a longstanding challenge in document intelligence. Utility bills exemplify this challenge: they exhibit high variability in layout, language, formatting conventions, and information density across providers and countries. Traditional template-based extraction systems fail on unseen layouts. The emergence of LLMs with both text and vision capabilities creates a new design choice for practitioners: should an explicit OCR preprocessing step be retained, or should the model extract directly from visual input? This question lacks a controlled empirical answer in the literature, particularly for multilingual, real-world documents.

### 1.3 Design Philosophy

The system is built around five core principles:

1. **Template-free generalisation**: No per-provider templates, rules, or layout-specific logic. The same prompt and pipeline processes bills from any provider in any supported language. Generalisation is tested, not assumed, via the multilingual dataset.

2. **Controlled experimentation**: The 2x2 factorial design (2 LLM backends x 2 input modalities) isolates variables systematically. The identical prompt, normalisation, and evaluation are shared across all conditions.

3. **Manifest-driven reproducibility**: A single CSV manifest is the authoritative registry of all documents, their metadata, and their readiness status. Every experimental run snapshots its configuration, manifest, and prompt, making results fully reproducible.

4. **Schema-as-contract**: A single 12-field Pydantic schema (`BillExtraction`) serves as the shared contract between LLM output, ground truth annotation, normalisation, evaluation, and reporting. This eliminates ambiguity about what constitutes a correct extraction.

5. **Per-document persistence with crash recovery**: Each document's results (extraction, raw LLM output, OCR text, timings, metadata) are written to disk immediately after processing. Resume logic allows interrupted runs to continue without reprocessing completed documents.

### 1.4 High-Level Architecture

The system follows a pipeline architecture with five logical stages, each implemented as a distinct module or module group:

```
Input (Manifest + PDFs)
    |
    v
Dataset Loading & Validation (dataset_loader.py)
    |
    v
Extraction Pipeline (pipeline.py)
    |-- PDF-to-Image Conversion (utils.py)
    |-- [OCR-text path] Tesseract OCR (ocr/tesseract.py)
    |-- [Vision path] Direct image input
    |-- LLM Invocation (llm/*.py)
    |-- JSON Parsing & Normalisation (normalisation.py)
    |-- Per-document Disk Persistence
    |
    v
Evaluation (evaluation/metrics.py, diagnosis.py)
    |
    v
Cross-Run Comparison & Reporting (evaluation/comparator.py, reporting.py)
```

The CLI (`cli.py`) acts as the user-facing facade, dispatching to the appropriate pipeline or evaluation command.

---

## 2. Architectural Design

### 2.1 Module Breakdown

The system comprises 14 Python modules organised into four packages:

| Module | Responsibility | LOC |
|--------|----------------|-----|
| `src/schema.py` | Canonical data models: `BillExtraction` (12-field Pydantic), `PipelineResult`, `DocumentEntry` | ~100 |
| `src/dataset_loader.py` | Manifest CSV validation, filtering, path resolution, file existence verification | ~183 |
| `src/pipeline.py` | Batch orchestration: document iteration, resume logic, stage wiring, error isolation | ~322 |
| `src/normalisation.py` | Shared normalisation functions for dates, strings, floats, currencies, units, provider names | ~343 |
| `src/utils.py` | Config loading (YAML + deep merge), PDF-to-image conversion, file I/O helpers, logging setup | ~122 |
| `src/performance.py` | `Timer` context manager, token-based cost estimation, optional system snapshots | ~98 |
| `src/reporting.py` | Chart generation (6 matplotlib/seaborn figures) and text summary from comparison data | ~199 |
| `src/ocr/base.py` | Abstract base class `OCREngine` defining the OCR interface | ~26 |
| `src/ocr/tesseract.py` | Tesseract adapter: language mapping, error handling, `pytesseract` wrapper | ~43 |
| `src/llm/base.py` | Abstract base class `LLMProvider`: text/vision extraction interface, base64 encoding utility | ~96 |
| `src/llm/openai_provider.py` | OpenAI Responses API with Structured Outputs (`BillExtraction` Pydantic schema) | ~147 |
| `src/llm/anthropic_provider.py` | Anthropic Messages API with prompt-instructed JSON and fence-stripping post-processing | ~161 |
| `src/llm/registry.py` | Provider registry and factory: lazy import, config-driven instantiation | ~67 |
| `src/evaluation/metrics.py` | Field comparison (null table, float tolerance, Levenshtein), document/run aggregation | ~355 |
| `src/evaluation/diagnosis.py` | Failure attribution: OCR failure vs LLM extraction failure vs vision model failure | ~104 |
| `src/evaluation/comparator.py` | Cross-run comparison: accuracy matrices, performance matrices, slice analysis | ~140 |
| `cli.py` | Click-based CLI: `run`, `evaluate`, `compare`, `report` commands | ~187 |

**Total**: approximately 2,700 lines of production code across 17 files, plus approximately 1,800 lines of tests across 12 test files (237+ test cases).

### 2.2 Inter-Module Dependencies

The dependency graph is acyclic and layered:

```
cli.py
  |-- src/pipeline.py
  |     |-- src/dataset_loader.py --> src/schema.py
  |     |-- src/llm/registry.py --> src/llm/base.py
  |     |     |-- src/llm/openai_provider.py --> src/schema.py
  |     |     |-- src/llm/anthropic_provider.py
  |     |-- src/ocr/tesseract.py --> src/ocr/base.py
  |     |-- src/normalisation.py
  |     |-- src/performance.py
  |     |-- src/utils.py
  |-- src/evaluation/metrics.py --> src/normalisation.py, src/schema.py
  |-- src/evaluation/diagnosis.py
  |-- src/evaluation/comparator.py --> src/evaluation/metrics.py
  |-- src/reporting.py --> src/schema.py, src/utils.py
```

Key observations:
- `schema.py` is the foundational module with zero internal dependencies; everything else depends on it.
- `normalisation.py` is shared between the pipeline (post-extraction) and evaluation (pre-comparison), ensuring identical treatment of predictions and ground truth.
- LLM providers depend only on `base.py` and `schema.py`; they are loaded lazily via the registry to avoid importing unused SDKs.
- The evaluation package is entirely decoupled from the pipeline; it reads disk artefacts (JSON files) rather than receiving in-memory objects.

### 2.3 Architectural Style

The system uses a **pipeline architecture** at the macro level (data flows linearly through stages) with a **strategy pattern** at the component level (swappable OCR engines and LLM providers behind abstract interfaces).

This hybrid was chosen for three reasons:

1. **Pipeline linearity** matches the natural processing flow of document extraction: ingest, preprocess, extract, normalise, evaluate. Each stage has well-defined inputs and outputs.

2. **Strategy abstraction** at the OCR and LLM layers enables the 2x2 factorial design without code duplication. Adding a new LLM provider (e.g., Google Gemini) requires only a new module implementing `LLMProvider` and one registry entry --- no changes to the pipeline, evaluation, or reporting modules.

3. **Disk-mediated decoupling** between the pipeline and evaluation modules means they can be run independently. A pipeline run produces a self-contained directory of artefacts; evaluation reads those artefacts without any runtime dependency on the pipeline code. This supports iterative evaluation refinement without re-running expensive LLM calls.

---

## 3. Design Decisions

### 3.1 Controlled Single-Variable Comparison vs Multi-System Benchmark

**Decision**: Hold the LLM reasoning engine constant and vary only the input modality (OCR-derived text vs direct vision).

**Why**: The research question asks whether OCR preprocessing helps or hurts extraction accuracy. If different models were used for each pipeline (e.g., Tesseract + GPT-4o vs Donut), the comparison would confound input modality with model architecture, training data, and reasoning capability. Controlling the reasoning engine isolates input modality as the sole independent variable.

**Alternative considered**: Multi-system benchmark comparing specialised OCR-free models (Donut, Pix2Struct, Florence-2) against OCR + LLM pipelines. This approach answers a different question ("which system performs best?") rather than the targeted question ("does OCR help or hurt when using the same reasoning engine?"). Rejected because it does not permit causal attribution of accuracy differences to input modality.

**Trade-off**: The controlled design limits ecological validity --- practitioners may use different models for each pipeline. However, it maximises internal validity, which is the priority for a research contribution. The 2x2 factorial partially addresses this by testing with two different LLM backends.

### 3.2 Template-Free Extraction via LLM Prompting vs Template-Based or ML Approaches

**Decision**: Use a single prompt template with a fixed 12-field schema, relying on the LLM's zero-shot reasoning for extraction, rather than per-provider templates, rule-based extraction, or trained ML models.

**Why**: Template-based approaches require layout-specific configuration for each utility provider and break on unseen layouts. Trained ML models (e.g., LayoutLM) require labelled training data per document type. The LLM-based approach generalises across providers and languages without per-provider configuration, which is essential for a system processing bills from diverse utility companies across four countries.

**Alternatives considered**:
- **Template-based (e.g., regex + coordinate mapping)**: Precise for known layouts but zero generalisation; would require a template per provider, defeating the template-free objective.
- **Trained document understanding models (LayoutLM, Donut)**: Require substantial labelled training data per document class; infeasible within the project's dataset size (5--50 documents) and timeline.
- **Few-shot prompting with examples**: Would improve accuracy on similar layouts but could introduce bias toward example layouts. Rejected in favour of zero-shot to test the model's inherent extraction capability.

**Trade-off**: Zero-shot LLM extraction sacrifices potential accuracy gains from fine-tuning or few-shot examples in exchange for generalisability and experimental cleanliness.

### 3.3 Schema-Driven Extraction with Fixed 12 Fields

**Decision**: Define a fixed canonical schema of 12 fields (`provider_name`, `utility_type`, `bill_number`, `bill_date`, `billing_period_start`, `billing_period_end`, `due_date`, `total_amount_due`, `currency`, `account_number`, `consumption_amount`, `consumption_unit`) enforced via Pydantic.

**Why**: A fixed schema enables exact-match evaluation with well-defined metrics. The 12 fields were selected to cover the core structured data present across utility bill types (electricity, gas, water) and countries, balancing coverage against annotation feasibility. All fields are nullable (`Optional`), accommodating bills that legitimately omit certain information.

**Alternative considered**: Open-ended key-value extraction where the model identifies whatever fields it can find. This approach would be more flexible but makes evaluation subjective --- there is no objective ground truth for "all fields present" when the schema is unbounded. It also prevents standardised comparison across runs.

**Trade-off**: The fixed schema may miss document-specific fields (e.g., feed-in tariff credits on solar bills, meter readings with different naming conventions). However, it ensures that evaluation is objective, reproducible, and comparable across experimental conditions.

### 3.4 OCR Engine Selection: Tesseract

**Decision**: Use Tesseract OCR (v4+, LSTM-based) as the sole OCR engine, configured with per-document language packs derived from the dataset manifest.

**Why**: Tesseract is open-source, runs locally (no API cost confound), supports multiple languages via downloadable language packs, and is the most widely-used open-source OCR engine. Local execution ensures that OCR processing time is measured independently of network latency, and that no additional API costs confound the cost comparison between pipelines.

**Alternatives considered**:
- **Google Cloud Vision API**: Higher accuracy on complex layouts but introduces a second cloud API dependency, adds cost that confounds the OCR-vs-vision cost comparison, and requires network access.
- **EasyOCR**: Deep-learning-based, potentially more accurate on certain scripts, but heavier computational footprint and less mature language pack ecosystem.
- **AWS Textract**: Commercial, layout-aware, but same confounding cost and cloud dependency issues as Google Vision.

**Trade-off**: Tesseract may underperform commercial OCR on complex layouts (rotated text, multi-column tables), which could bias the comparison against the OCR-based pipeline. This is acknowledged as a limitation and discussed in the evaluation.

### 3.5 LLM Provider Selection: OpenAI + Anthropic in 2x2 Factorial

**Decision**: Use two LLM providers --- OpenAI (GPT-4o) and Anthropic (Claude Sonnet) --- each tested in both text and vision mode, yielding a 2x2 factorial design.

**Why**: The 2x2 factorial directly addresses RQ3 (effect of model choice). Using two providers from different organisations with different architectures tests whether the OCR-vs-vision accuracy gap is model-specific or a general phenomenon. A single-provider design would leave open the question of whether findings generalise.

**Alternative considered**: Single provider with two model sizes (e.g., GPT-4o vs GPT-4o-mini). Rejected because size variation confounds model architecture with capacity, and same-family models likely share similar vision/text processing characteristics.

**Trade-off**: Two providers introduce an asymmetry in structured output support: OpenAI provides constrained decoding (Structured Outputs guarantee schema-valid JSON), while Anthropic requires prompt-instructed JSON with post-processing fence-stripping. This asymmetry is itself a finding worth discussing.

### 3.6 Structured Output: Constrained Decoding vs Prompt-Instructed JSON

**Decision**: Use provider-appropriate structured output mechanisms --- OpenAI Structured Outputs (constrained decoding via `text_format=BillExtraction`) for OpenAI, and prompt-instructed JSON with `_strip_json_fencing()` post-processing for Anthropic.

**Why**: OpenAI's Structured Outputs guarantee that the model output conforms to the Pydantic schema at the token level, eliminating JSON parsing failures. Anthropic lacks an equivalent constrained decoding mechanism, so the prompt instructs JSON output and a multi-stage parsing pipeline (`_parse_llm_json`) handles common failure modes (markdown fences, extraneous text, brace-balanced extraction).

**Alternative considered**: Use prompt-instructed JSON for both providers (disabling OpenAI's structured outputs) to ensure identical output processing. Rejected because it would deliberately degrade OpenAI's output reliability, and the asymmetry itself is a meaningful practical consideration.

**Trade-off**: The asymmetry means that JSON parsing failures may differ between providers, potentially confounding extraction accuracy with output format reliability. The raw LLM output is archived per document, enabling post-hoc analysis of whether parsing failures (not extraction failures) drove accuracy differences.

### 3.7 Normalisation Strategy: Shared Pre-Comparison Normalisation

**Decision**: Apply identical normalisation functions to both predictions and ground truth before comparison. Normalisation covers dates (10 format patterns to ISO 8601), strings (NFC Unicode, lowercase, whitespace collapse), floats (EU/US decimal parsing, 2dp rounding), currencies (symbol/name to ISO 4217), consumption units (synonym mapping), utility types (multilingual synonym mapping), and provider names (legal suffix stripping).

**Why**: Without normalisation, correct extractions formatted differently from ground truth would be penalised. For example, a model outputting `"01/03/2024"` against a ground truth of `"2024-03-01"` has extracted the correct date but in a different format. Provider names with legal suffixes (e.g., `"Acque Veronesi s.c. a r.l."` vs `"Acque Veronesi"`) are semantically equivalent. Normalisation ensures that evaluation measures extraction accuracy, not formatting compliance.

**Alternative considered**: Raw string comparison without normalisation. This would inflate false negatives for correct-but-differently-formatted extractions, particularly across languages (European date formats, decimal separators).

**Trade-off**: Normalisation may mask genuine extraction errors if the normalisation rules are too aggressive. The `FIELD_NORMALISERS` dispatch table makes the normalisation rules explicit and auditable per field.

### 3.8 Evaluation Null Handling: 4-Class Taxonomy

**Decision**: Classify each field comparison into one of four categories: `correct` (both non-null and match), `incorrect` (both non-null but mismatch), `hallucination` (ground truth is null but model returned a value), `omission` (ground truth has a value but model returned null), and `both_null` (neither has a value --- excluded from accuracy denominators).

**Why**: A binary correct/incorrect classification obscures the distinction between hallucination (model fabricated data) and omission (model missed existing data), which are fundamentally different failure modes with different implications. Hallucinations are more dangerous in production (false information) than omissions (missing information). The `both_null` exclusion prevents fields legitimately absent from the bill from inflating accuracy.

**Alternative considered**: Binary correct/incorrect. Rejected because it conflates qualitatively different failure modes critical to answering RQ1 (where do the pipelines fail, and how?).

**Trade-off**: The 4-class taxonomy adds complexity to metric aggregation. The `_aggregate_slice` function must handle each category correctly when computing accuracy across slices (language, utility type).

### 3.9 Failure Diagnosis: Heuristic Error Attribution

**Decision**: For the OCR-based pipeline, attribute each incorrect field to either `ocr_failure` (the ground truth value is absent from the OCR text) or `llm_extraction_failure` (the ground truth value is present in the OCR text but the LLM failed to extract it). For the vision pipeline, all failures are attributed to `vision_model_failure`.

**Why**: This diagnosis answers the most important sub-question of RQ1: when the OCR-based pipeline fails, is the failure caused by Tesseract not capturing the text, or by the LLM not extracting from captured text? This distinction has direct practical implications for pipeline improvement.

**Alternative considered**: Manual error analysis. This would be more precise but does not scale and is not reproducible. The heuristic approach (substring search of ground truth in OCR text) provides an automated, reproducible first approximation.

**Trade-off**: The substring heuristic has false positives (a value might appear in OCR text in a different context) and false negatives (OCR might capture the value with minor character-level errors that prevent exact substring matching). These limitations are documented.

### 3.10 Vision Input Scope: First 2 Pages Only

**Decision**: In vision mode, only the first 2 pages of each bill are sent to the LLM, regardless of total page count.

**Why**: Empirically, the majority of target fields (provider name, bill date, amounts, account number) appear within the first two pages of most utility bills. Processing all pages increases token count (and therefore cost and latency) with diminishing accuracy returns. This constraint also standardises the information budget across documents of varying length.

**Alternative considered**: All pages. This would maximise information availability but at significantly higher cost, particularly for documents with 6--8 pages where later pages contain detailed tariff breakdowns and regulatory information irrelevant to the target fields.

**Trade-off**: Some fields (particularly billing period dates and consumption figures) may appear only on later pages for certain providers. This is a known limitation and a candidate for future work (adaptive page selection based on content detection).

### 3.11 Prompt Separation: Instructions vs Data

**Decision**: The prompt template contains only extraction instructions and the schema description. The actual data (OCR text or images) is passed separately in the user message, not embedded in the instruction prompt.

**Why**: This separation avoids duplicating input tokens. If OCR text were embedded in the instruction prompt and also sent as user content, the model would process the same text twice. Separation keeps the system/instruction message clean and token-efficient.

**Alternative considered**: Single combined prompt with instructions and data interleaved. Rejected for token efficiency and because it conflates instruction-following context with data processing context.

### 3.12 Per-Document Persistence and Resume Logic

**Decision**: Write all artefacts (extraction.json, raw_llm_output.txt, ocr_text.txt, timings.json, metadata.json) to disk immediately after each document is processed. If a document's `extraction.json` already exists, skip it unless `--force` is set.

**Why**: LLM API calls are expensive and slow. If a run is interrupted (network failure, timeout, API rate limit), resume logic allows continuation from the point of failure without reprocessing completed documents. Per-document persistence also enables incremental evaluation --- a partially-completed run can still be evaluated on its completed subset.

**Alternative considered**: In-memory accumulation with a single batch write at the end. This is simpler but loses all progress on interruption and requires the entire run to complete before any evaluation is possible.

---

## 4. Data Model and Schema Design

### 4.1 Schema Structure

The data model centres on three types defined in `schema.py`:

**`BillExtraction`** (Pydantic `BaseModel`): The canonical 12-field extraction schema. Every field is `Optional` (nullable), reflecting the reality that utility bills vary in what information they present. The field list:

| Field | Type | Rationale |
|-------|------|-----------|
| `provider_name` | `str` | Identifies the utility company; legal suffix stripping in normalisation |
| `utility_type` | `str` | `electricity` / `gas` / `water`; multilingual synonym mapping |
| `bill_number` | `str` | Invoice reference; free-form string |
| `bill_date` | `date` | Issue date; Pydantic handles `date` serialisation to ISO 8601 |
| `billing_period_start` | `date` | Period start; enables period-based analysis |
| `billing_period_end` | `date` | Period end |
| `due_date` | `date` | Payment deadline; often absent |
| `total_amount_due` | `float` | Amount; EU/US decimal parsing in normalisation |
| `currency` | `str` | ISO 4217; symbol-to-code mapping in normalisation |
| `account_number` | `str` | Customer reference; free-form string |
| `consumption_amount` | `float` | Usage quantity; unit-specific |
| `consumption_unit` | `str` | Unit of measurement; synonym mapping (kWh, m3, SMC, etc.) |

The class-level `SCHEMA_FIELDS` list provides a canonical iteration order used by evaluation, reporting, and normalisation modules, ensuring consistent field ordering across the entire system.

The `schema_description()` classmethod generates a human-readable field description injected into the LLM prompt via the `{schema_description}` template placeholder. This ensures the prompt always reflects the current schema definition.

**`PipelineResult`** (Pydantic `BaseModel`): An envelope wrapping the extraction with provenance metadata --- raw LLM output (for debugging), OCR text (for diagnosis), timing breakdown, token usage, model ID, and pipeline mode. This type is internal to the pipeline and not persisted directly; its fields are written to separate files per document.

**`DocumentEntry`** (`dataclass`): A resolved manifest row containing the document's metadata and file paths. Used by the pipeline to iterate documents.

### 4.2 Schema Justification

The 12-field schema was designed by intersecting the common structured fields across utility bills from four countries (UK, Italy, Germany, France) and three utility types (electricity, gas, water). Fields were included only if they are:
1. Present on a majority of bills in the dataset.
2. Unambiguously extractable (not requiring domain-specific calculation).
3. Evaluable with exact-match or near-match metrics.

Fields omitted by design: line-item tariff breakdowns (variable structure), meter readings (inconsistent naming), address fields (privacy concerns), multi-rate consumption splits (complex nested structure incompatible with flat schema).

### 4.3 Ground Truth Annotation Strategy

Ground truth files follow a standardised JSON envelope:

```json
{
  "document_id": "gb_electricity_ovo_001",
  "annotated_by": "student",
  "annotation_date": "2026-03-30",
  "fields": { ... 12 fields ... }
}
```

Design choices:
- Fields not present on the bill are set to `null` explicitly, distinguishing "field absent" from "field unannotated".
- Legal-form suffixes are stripped from `provider_name` in ground truth and predictions alike, so that `"Acque Veronesi s.c. a r.l."` and `"Acque Veronesi"` are treated as equivalent.
- The `annotated` and `verified` flags in the manifest gate which documents enter the evaluation set, preventing unannotated or unverified documents from corrupting results.

### 4.4 Dataset Manifest Design

The manifest (`data/dataset_manifest.csv`) is the single source of truth for the dataset:

| Column | Purpose |
|--------|---------|
| `document_id` | Unique key; doubles as filename stem for PDF and ground truth |
| `language` | ISO 639-1; drives Tesseract language pack selection and evaluation slicing |
| `utility_type` | `electricity` / `gas` / `water`; drives evaluation slicing |
| `provider` | Billing company name; metadata for analysis |
| `digital_native` | Born-digital vs scanned; potential confounding variable |
| `page_count` | Document length; metadata for cost/complexity analysis |
| `annotated` | Ground truth JSON exists |
| `verified` | Ground truth manually checked |
| `status` | `active` / `excluded`; allows soft-deletion without file removal |

The **runnable set** is defined as `status=active AND annotated=true AND verified=true`, enforced by `DatasetLoader.load_and_validate()`. This three-flag gating ensures that only quality-controlled documents enter experimental runs.

---

## 5. Experimental Framework Design

### 5.1 Experiment Structure: 2x2 Factorial

The experimental design is a 2x2 factorial with two factors:

| | Text Mode (OCR-based) | Vision Mode (OCR-free) |
|---|---|---|
| **Model A (OpenAI GPT-4o)** | Condition 1 | Condition 2 |
| **Model B (Anthropic Claude Sonnet)** | Condition 3 | Condition 4 |

Each condition is a complete pipeline run across the full dataset. The four runs share:
- The same document set (manifest-controlled)
- The same prompt template
- The same normalisation rules
- The same evaluation metrics

This design supports three research questions:
- **RQ1** (OCR vs vision): Compare Condition 1 vs 2 and Condition 3 vs 4 (within-model modality comparison).
- **RQ2** (cost and latency): Compare timing and cost data across all four conditions.
- **RQ3** (model choice effect): Compare Condition 1 vs 3 and Condition 2 vs 4 (within-modality model comparison), and examine whether the modality gap (RQ1) is consistent across models.

### 5.2 Run Execution and Orchestration

The `run_pipeline()` function in `pipeline.py` orchestrates a complete experimental run:

1. **Dataset loading**: `DatasetLoader.load_and_validate()` reads the manifest, validates all columns and values, filters to runnable documents, resolves file paths, and verifies file existence.

2. **Provider instantiation**: `get_provider(config)` lazily imports the selected LLM SDK and constructs the provider with config-specified parameters.

3. **Run directory creation**: A unique run ID (`{timestamp}_{provider}_{model}_{mode}`) is generated. The run directory is populated with frozen snapshots of the config, manifest, and prompt.

4. **Document iteration**: For each document, `_process_document()` executes the full pipeline: PDF-to-image conversion, OCR (if text mode), LLM invocation, JSON parsing, normalisation, and artefact persistence.

5. **Resume logic**: Documents with existing `extraction.json` are skipped (unless `--force`), enabling interrupted runs to continue.

6. **Error isolation**: If a document fails, the error is captured in `error.json` and the run continues with the next document. This prevents a single problematic document from aborting the entire experiment.

### 5.3 Reproducibility Design

Every experimental run is self-documenting through four mechanisms:

1. **Config snapshot**: The exact YAML configuration (including CLI overrides) is written to `config.yaml` in the run directory.
2. **Manifest snapshot**: A copy of the CSV manifest at run time is preserved as `manifest_snapshot.csv`.
3. **Prompt snapshot**: The exact prompt template is copied as `prompt.txt`.
4. **Per-document metadata**: Each document's `metadata.json` records the LLM provider, model, pipeline mode, cost estimate, and timestamp.

These snapshots ensure that any run can be audited and, in principle, reproduced (modulo LLM API non-determinism at temperature > 0).

### 5.4 Evaluation Pipeline

The evaluation pipeline is a three-stage process:

**Stage 1 --- Per-Run Evaluation** (`evaluate_run`):
- Walks the run directory, loading each document's `extraction.json` and matching ground truth.
- For each document, normalises both prediction and ground truth identically via `normalise_extraction()`.
- Compares all 12 fields using `compare_field()`, which applies the null table (4-class taxonomy), float tolerance (+-0.01), date exact-match, and string exact-match with Levenshtein similarity.
- Aggregates to field-level accuracy (per-field across documents, with `both_null` excluded from denominators), document-level accuracy (fraction of fully-correct documents), and overall accuracy.
- Slices results by language and utility type using metadata from `metadata.json`.
- Writes `evaluation.json` to the run directory.

**Stage 2 --- Failure Diagnosis** (`diagnose_document`):
- For each incorrect field in the OCR-text pipeline: searches `ocr_text.txt` for the ground truth value. Present = LLM extraction failure; absent = OCR failure.
- For the vision pipeline: all failures attributed to vision model failure.
- Writes `diagnosis.json` per document.

**Stage 3 --- Cross-Run Comparison** (`compare_runs`):
- Loads or computes `evaluation.json` for each run.
- Builds accuracy matrices (12 per-field accuracies across runs), performance matrices (mean timings, total cost), null analysis (hallucination/omission counts), and slice comparisons.
- Writes `comparison.json`, which feeds the reporting module.

### 5.5 Reporting

The `generate_report()` function produces six charts and a text summary from `comparison.json`:

1. Overall accuracy bar chart (one bar per condition)
2. Field accuracy heatmap (12 fields x 4 conditions)
3. Timing breakdown stacked bar (OCR time + LLM time)
4. Cost comparison bar chart
5. Accuracy by language (grouped bar)
6. Accuracy by utility type (grouped bar)

These visualisations directly support the three research questions with publication-ready figures.

---

## 6. Model Integration Strategy

### 6.1 Abstraction Layer

The `LLMProvider` abstract base class defines a provider-agnostic interface:

```python
class LLMProvider(ABC):
    def extract_from_text(self, ocr_text: str, prompt: str) -> dict: ...
    def extract_from_image(self, images: list[Image.Image], prompt: str) -> dict: ...
    def get_model_id(self) -> str: ...
```

Both extraction methods return a standardised dict: `{"raw_output": str, "token_usage": {"input_tokens": int, "output_tokens": int}, "latency_ms": float}`. This uniform return type allows the pipeline to handle all providers identically.

### 6.2 Provider-Specific Implementations

**OpenAI (`OpenAIProvider`)**: Uses the Responses API with Structured Outputs. The `text_format=BillExtraction` parameter enables constrained decoding, guaranteeing schema-valid JSON output at the token level. System instructions go in the `instructions` parameter; user data goes in the `input` list. Vision images use `type: "input_image"` with a configurable `detail` parameter (`"high"` by default for maximum visual fidelity).

**Anthropic (`AnthropicProvider`)**: Uses the Messages API with prompt-instructed JSON. System instructions go in the `system` parameter; user data goes in the `messages` list. Claude frequently wraps JSON output in markdown code fences; the `_strip_json_fencing()` function removes these before downstream parsing. Vision images use base64-encoded PNG blocks per the Anthropic Messages API specification.

### 6.3 Registry and Factory

The `registry.py` module maps provider names to dotted class paths and performs lazy import at runtime:

```python
_PROVIDERS = {
    "openai": "src.llm.openai_provider.OpenAIProvider",
    "anthropic": "src.llm.anthropic_provider.AnthropicProvider",
}
```

The `get_provider(config)` factory reads the provider name from config, lazily imports the class, and instantiates it with config-specified parameters (model, temperature, max_tokens, timeout, max_retries, vision_detail). Lazy import ensures that the OpenAI SDK is not loaded when running the Anthropic provider, and vice versa.

### 6.4 Input/Output Standardisation

Both pipelines produce identical output: a `dict` of raw LLM text that is parsed by `_parse_llm_json()` and normalised by `normalise_extraction()` before being validated into a `BillExtraction` Pydantic model. This standardisation ensures that downstream evaluation treats all four experimental conditions identically.

The JSON parsing pipeline is hardened against three common LLM output failure modes:
1. **Direct JSON**: `json.loads(text)` succeeds.
2. **Markdown-fenced JSON**: Regex-strips ` ```json ... ``` ` fences before parsing.
3. **Embedded JSON with extraneous text**: Finds the first `{` and its matching `}` via brace-depth counting, then parses the extracted substring.

If all three strategies fail, a diagnostic `ValueError` is raised with the first 500 characters of the output for debugging.

---

## 7. Performance and Scalability Considerations

### 7.1 Computational Efficiency

**PDF-to-image conversion**: The `pdf2image` library (backed by Poppler) runs locally. The default DPI of 300 balances OCR accuracy against memory consumption. Each page at 300 DPI produces approximately a 2500x3500 pixel image (~26 MB uncompressed in memory). For an 8-page document, this is approximately 208 MB of image data.

**OCR processing**: Tesseract runs locally on CPU. Per-page OCR time depends on page complexity and language; typical times range from 1--5 seconds per page. All pages are OCR'd sequentially; parallelisation is a potential optimisation.

**LLM API calls**: The dominant latency component. Vision mode calls are significantly slower than text mode because image tokens are more expensive to process. The first-2-pages constraint limits vision input size.

**Normalisation and evaluation**: Negligible computation (string operations, float comparisons, Levenshtein similarity on short strings). The entire evaluation of a 50-document run completes in under 1 second.

### 7.2 Cost Management

Cost is managed through three mechanisms:
1. **First-2-pages baseline**: Limits vision token consumption per document.
2. **Resume logic**: Prevents reprocessing of completed documents.
3. **Per-document cost estimation**: `estimate_cost()` uses a pricing table for known models, logging warnings for unrecognised models. Cost is tracked per document and aggregated per run, enabling precise cost comparison between conditions.

### 7.3 Bottlenecks

The primary bottleneck is LLM API latency. Each document requires one API call (or two, for OCR-text mode where OCR is local). With 50 documents and 4 conditions, the experiment involves approximately 200 API calls. At 5--15 seconds per call, total experiment time is 15--50 minutes.

Potential mitigations (deferred as future work): asynchronous API calls, batching where supported, document-level parallelism with rate limiting.

---

## 8. Error Handling and Robustness

### 8.1 Noisy Documents

The system handles noisy input at multiple levels:
- **OCR failures**: Tesseract errors (e.g., `TesseractError` from corrupted images) are caught and result in an empty OCR text string. The LLM receives minimal text and is likely to return mostly null fields.
- **LLM JSON parsing failures**: The three-stage `_parse_llm_json()` function handles common output noise (fences, extraneous text). If parsing fails entirely, the document is marked as failed with a detailed error trace.
- **Normalisation edge cases**: Unparseable dates are passed through as-is (likely causing an evaluation mismatch, which is the correct behaviour). Unknown currencies return `None` with a warning. Booleans are explicitly rejected by `normalise_float()` to prevent `True/False` being interpreted as `1.0/0.0`.

### 8.2 Missing Fields

All 12 schema fields are `Optional`. The LLM is instructed to return `null` for fields not present on the bill. The evaluation null table handles this gracefully: legitimate absence (`both_null`) is excluded from accuracy denominators, while hallucination and omission are tracked as distinct failure modes.

### 8.3 Pipeline-Level Error Isolation

The `_process_document()` function is wrapped in a `try/except` within the batch loop. If any document fails (network timeout, API error, parsing failure), the error is captured in `error.json` with a full traceback, and the run continues with the remaining documents. The evaluation module skips documents with `error.json` and reports them in `errors_skipped`.

### 8.4 Manifest Validation

The `DatasetLoader` implements a six-step validation pipeline:
1. File existence check (manifest CSV must exist)
2. CSV parsing (must have at least one row)
3. Column validation (all 9 required columns must be present)
4. Duplicate ID detection (reports exact row numbers)
5. Value validation (language, utility_type, status against allowed sets; page_count must be integer) --- errors are aggregated and reported together
6. File existence verification (both PDF and ground truth must exist for runnable documents)

This validates early, preventing runtime failures deep in the pipeline.

---

## 9. Extensibility and Maintainability

### 9.1 Adding New LLM Providers

Adding a new provider (e.g., Google Gemini) requires:
1. Create `src/llm/gemini_provider.py` implementing `LLMProvider`.
2. Add one entry to `_PROVIDERS` in `registry.py`: `"gemini": "src.llm.gemini_provider.GeminiProvider"`.

No changes to the pipeline, evaluation, CLI, or any other module. The strategy pattern and lazy import registry ensure that the new provider is available immediately via config: `llm.provider: "gemini"`.

### 9.2 Adding New OCR Engines

The `OCREngine` ABC defines a single method: `extract_text(image, language)`. A new OCR engine (e.g., EasyOCR, PaddleOCR) needs only to implement this interface. The pipeline currently hardcodes `TesseractOCR`; extending to a registry pattern (analogous to the LLM registry) would require minimal refactoring.

### 9.3 Modifying the Schema

Adding a new extraction field requires:
1. Add the field to `BillExtraction` in `schema.py`.
2. Add the field to `SCHEMA_FIELDS`.
3. Add a normaliser to `FIELD_NORMALISERS` in `normalisation.py`.
4. Update ground truth annotations to include the new field.
5. Update the prompt template.

The evaluation, comparison, and reporting modules automatically iterate `SCHEMA_FIELDS`, so they require no changes. This is the benefit of the schema-as-contract pattern.

### 9.4 Adding New Document Types

Adding a new utility type (e.g., telecommunications) or language requires:
1. Add the language/type to the validation sets in `dataset_loader.py`.
2. Add any new normalisation synonyms (e.g., `"telecom": "telecommunications"` in `_UTILITY_TYPE_MAP`).
3. Install the Tesseract language pack if new language.
4. Add documents to the dataset with manifest rows.

### 9.5 Design Patterns

| Pattern | Where Used | Purpose |
|---------|------------|---------|
| Strategy | `LLMProvider`, `OCREngine` | Swappable algorithm implementations |
| Factory + Registry | `registry.py` | Config-driven instantiation with lazy import |
| Template Method | `pipeline._process_document()` | Fixed stage sequence with pluggable components |
| Context Manager | `Timer` | RAII-style timing with guaranteed cleanup |
| Schema-as-Contract | `BillExtraction.SCHEMA_FIELDS` | Single iteration order across all modules |
| Strategy Table | `FIELD_NORMALISERS` | Per-field normaliser dispatch |
| Null Object | `Timer()` as 0ms placeholder | Uniform timing dict structure for both modes |

---

## 10. Limitations and Trade-offs

### 10.1 Architectural Limitations

1. **Sequential document processing**: Documents are processed one-at-a-time. Asynchronous or parallel processing would significantly reduce total experiment time but adds complexity in rate limiting and error handling.

2. **Hardcoded Tesseract instantiation**: The pipeline directly imports `TesseractOCR` rather than using the OCR ABC + registry pattern. This limits OCR engine swapping to code changes rather than config changes.

3. **Vision diagnosis granularity**: All vision mode failures are attributed to `vision_model_failure` without further differentiation. Unlike OCR mode, there is no intermediate artefact (analogous to OCR text) to enable finer-grained attribution.

### 10.2 Model Integration Limitations

1. **Structured output asymmetry**: OpenAI's constrained decoding guarantees schema-valid JSON; Anthropic's prompt-instructed JSON does not. This means Anthropic may exhibit parsing failures that are absent from OpenAI runs, conflating output format reliability with extraction accuracy.

2. **Temperature fixed at 0.0**: While deterministic output aids reproducibility, it prevents exploration of output diversity and confidence calibration.

3. **Single prompt version**: All experiments use `extraction_v1.txt`. Prompt sensitivity analysis (varying instructions, adding examples, modifying field descriptions) is deferred.

### 10.3 Dataset Limitations

1. **Small sample size**: The current dataset contains 5 verified documents. Statistical claims require careful qualification. Results should be interpreted as case studies rather than population-level generalisations.

2. **Limited language coverage**: Only English and Italian are represented in the current verified set. German and French documents are listed in the manifest but require annotation.

3. **All documents are digital-native**: The dataset lacks scanned documents, which would stress-test OCR accuracy more severely.

4. **Single annotator**: Ground truth was created by a single annotator without inter-annotator agreement measurement, introducing potential annotation bias.

### 10.4 Evaluation Limitations

1. **Substring-based diagnosis heuristic**: The OCR failure attribution relies on exact substring matching. OCR may capture a value with character-level errors (e.g., `"l77.53"` instead of `"177.53"`) that the substring check misses, leading to false OCR failure attributions.

2. **No confidence scoring**: The evaluation is binary per field (match/no-match). Partial credit is computed via Levenshtein similarity but not used in accuracy calculations.

3. **No statistical significance testing**: With 5 documents, classical statistical tests (t-test, ANOVA) lack power. The evaluation reports descriptive statistics only.

### 10.5 Realistic Constraints

1. **Compute**: All computation is local (OCR) or cloud API (LLM). No GPU is required. Total API cost for the 2x2 factorial is estimated at $20--40.

2. **Time**: Each experimental condition takes approximately 5--15 minutes for 5 documents. The full 2x2 matrix completes in under an hour.

3. **Data availability**: Real utility bills contain personal data; the dataset uses sample/specimen bills from utility companies' public websites to avoid privacy concerns.

---

## 11. Comparison to Alternative Approaches

### 11.1 Template-Based Extraction Systems

**Examples**: Apache Tika + regex rules, UiPath Document Understanding with templates.

**Comparison**: Template-based systems achieve high accuracy on known layouts but require a new template for each provider. With hundreds of utility providers across Europe, template creation is a prohibitive maintenance burden. The LLM-based approach processes all providers with a single prompt at the cost of lower per-document accuracy on complex layouts.

**Why the LLM approach is justified for this project**: The research question is about modality comparison (OCR vs vision), not maximum accuracy. Template-based systems are not applicable to the vision pipeline at all, making them incomparable.

### 11.2 Rule-Based Extraction

**Examples**: Regex + coordinate-based extraction from PDF text layers.

**Comparison**: Rule-based systems work well on born-digital PDFs with accessible text layers but fail on scanned documents and provide no generalisation across layouts. They also skip the image modality entirely, making them irrelevant to the OCR-vs-vision comparison.

### 11.3 End-to-End Deep Learning Pipelines

**Examples**: Donut (OCR-free document understanding), LayoutLM (layout-aware language model), Pix2Struct.

**Comparison**: These models are trained end-to-end on document datasets and achieve strong results on benchmarks. However:
- They require task-specific fine-tuning with hundreds to thousands of labelled examples.
- They cannot be fairly compared against LLM-based extraction in a controlled modality study because they have fundamentally different architectures.
- Including them would answer "which system is best?" rather than "does OCR help or hurt with the same reasoning engine?"

**Why excluded**: Specialised models are discussed in the literature review but excluded from the experimental design because including them would confound the modality comparison. They are acknowledged as strong baselines for absolute performance comparison.

### 11.4 Hybrid Approaches

**Examples**: OCR + layout features + LLM, multi-stage extraction with confidence routing.

**Comparison**: Hybrid approaches could combine OCR and vision evidence, potentially outperforming either modality alone. This is identified as a promising direction for future work but exceeds the scope of the current controlled comparison.

---

## 12. Alignment with Research Questions

### 12.1 RQ1: Does explicit OCR preprocessing improve or degrade extraction accuracy compared to direct visual extraction by the same LLM?

**System support**: The controlled single-variable design (same model, same prompt, different input modality) directly isolates this question. Field-level accuracy, document-level accuracy, and the 4-class null taxonomy (hallucination vs omission) provide multi-dimensional accuracy comparison. Failure diagnosis attributes errors to OCR or LLM, answering the follow-up question of *where* the OCR pipeline fails.

### 12.2 RQ2: How do the two pipelines compare in cost, latency, and operational complexity?

**System support**: The `Timer` context manager measures wall-clock time per stage (PDF conversion, OCR, LLM call, parsing/normalisation). Token usage is recorded from API response metadata. `estimate_cost()` computes USD cost per document. The `performance_matrix` in `comparison.json` aggregates these across runs. Operational complexity is assessed qualitatively: the OCR pipeline requires Tesseract installation, language pack management, and per-document language configuration; the vision pipeline requires none of these.

### 12.3 RQ3: Does the accuracy gap between OCR-based and OCR-free extraction vary across different LLM backends?

**System support**: The 2x2 factorial (OpenAI GPT-4o x Anthropic Claude Sonnet) tests two models from different providers with different architectures. The `comparison.json` accuracy matrix enables direct comparison: if the OCR-vs-vision gap is similar for both models, the effect is general; if it differs, the effect is model-specific. Slice analysis by language and utility type provides further granularity.

---

## 13. Visualisation Suggestions

### 13.1 Architecture Diagrams

1. **System architecture diagram**: A top-level flowchart showing the two pipeline paths (OCR-text and vision) diverging after PDF-to-image conversion and converging at JSON parsing. Include module names and their responsibilities. The existing mermaid diagram in SPEC.md provides a foundation; a publication-quality version should use consistent styling and highlight the controlled variable (input modality).

2. **Module dependency diagram**: A directed acyclic graph showing inter-module dependencies, with `schema.py` at the root and `cli.py` at the top. Useful for the design chapter to demonstrate layered architecture.

### 13.2 Data Flow Diagrams

3. **Per-document processing flow**: A sequence diagram showing the stages for a single document in each mode: PDF -> images -> (OCR text | images) -> LLM -> raw JSON -> parse -> normalise -> BillExtraction -> disk. Annotate with timing measurement points.

4. **Evaluation data flow**: A diagram showing how run artefacts (extraction.json, metadata.json, ocr_text.txt) are consumed by the three evaluation stages (metrics, diagnosis, comparison) to produce evaluation.json, diagnosis.json, and comparison.json.

### 13.3 Experimental Design Diagrams

5. **2x2 factorial matrix**: A simple table diagram showing the four experimental conditions with labels.

6. **Null handling decision tree**: A flowchart showing the 4-class null taxonomy: GT null + Pred null -> both_null; GT null + Pred value -> hallucination; GT value + Pred null -> omission; both values -> compare by field type.

7. **Failure diagnosis flowchart**: A decision tree for OCR-mode diagnosis: field incorrect -> search OCR text for GT value -> found: LLM failure; not found: OCR failure.

### 13.4 Results Visualisations

The six charts already generated by `reporting.py` (overall accuracy, field heatmap, timing breakdown, cost comparison, accuracy by language, accuracy by utility type) provide the core results visualisations. Additional suggestions:

8. **Confusion matrix per condition**: For each of the 4 conditions, a 4-class confusion matrix (correct, incorrect, hallucination, omission) across all fields.

9. **Error attribution pie chart**: For the OCR-text conditions, a pie chart showing the proportion of errors attributed to OCR failure vs LLM extraction failure.

---

## 14. Critical Evaluation

### 14.1 Strengths

1. **Rigorous experimental control**: The decision to hold the reasoning engine constant while varying only the input modality is methodologically sound and uncommon in the literature. Most comparisons use different systems, confounding multiple variables.

2. **Comprehensive evaluation framework**: The combination of field-level accuracy, document-level accuracy, 4-class null taxonomy, Levenshtein similarity for partial credit, failure diagnosis, cost tracking, and multi-dimensional slicing (language, utility type) provides a thorough evaluation that supports nuanced analysis.

3. **Schema-as-contract coherence**: The single `BillExtraction` schema with `SCHEMA_FIELDS` ensures that the prompt, ground truth, normalisation, evaluation, and reporting all operate on exactly the same 12 fields in the same order. This eliminates a common source of bugs in evaluation pipelines.

4. **Reproducibility infrastructure**: Config/manifest/prompt snapshots per run, per-document artefact persistence, and resume logic demonstrate engineering maturity. Any run can be audited and its results independently verified.

5. **Clean separation of concerns**: The disk-mediated decoupling between pipeline and evaluation means evaluation can be refined iteratively without re-running expensive LLM calls. This is both a practical advantage and a design strength.

6. **Normalisation depth**: The shared normalisation layer handles multilingual date formats, EU/US number conventions, currency symbols, consumption unit synonyms, and provider name legal suffixes. This prevents superficial formatting differences from being counted as extraction errors.

7. **Test coverage**: 237+ tests covering schema validation, normalisation edge cases, dataset loader validation, evaluation metrics (including null table boundary cases), and diagnosis attribution. Test-driven development is evident in the parametrised test structure.

### 14.2 Areas for Improvement

1. **Statistical rigour**: With 5 documents, the results are case studies, not population-level findings. For publication, the dataset would need to be expanded to at least 30--50 documents per language to support meaningful statistical analysis (confidence intervals, effect size estimation, non-parametric tests for non-normal distributions).

2. **Inter-annotator agreement**: Ground truth from a single annotator lacks reliability validation. Standard practice requires at least two annotators with Cohen's kappa or similar agreement metrics.

3. **Prompt sensitivity analysis**: A single prompt version is used. The results may be prompt-dependent --- a different instruction phrasing could change the accuracy rankings. A rigorous study would test 3--5 prompt variants.

4. **OCR preprocessing**: No image preprocessing (grayscale conversion, binarisation, deskewing) is applied before Tesseract. These standard techniques can significantly improve OCR accuracy on noisy or skewed documents.

5. **Vision page selection**: The first-2-pages constraint is fixed rather than adaptive. A more sophisticated approach might use a lightweight classifier to identify which pages contain target fields.

6. **Async processing**: Sequential API calls are a practical bottleneck. Asynchronous processing with rate limiting would reduce experiment time proportionally.

7. **Cross-language normalisation validation**: The normalisation rules for EU/US decimal conventions rely on heuristic position analysis. Edge cases (e.g., a number like `1.234` that could be 1234 in EU or 1.234 in US) are not disambiguated.

### 14.3 Publication-Level Requirements

To elevate this work to publication quality, the following would be needed:
- Dataset expansion to 50+ documents across 4+ languages
- Inter-annotator agreement metrics
- Statistical significance testing (or explicit power analysis showing why it is not applicable)
- Prompt sensitivity analysis with ablation
- Comparison against at least one specialised baseline (e.g., Donut fine-tuned on utility bills)
- Error analysis case studies with visual examples of OCR failures and vision misinterpretations
- Discussion of LLM non-determinism even at temperature 0 (documented in OpenAI/Anthropic literature)
