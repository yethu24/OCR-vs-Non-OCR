"""Generate Chapter 5 table figures fig-5-4 and fig-5-7.

Reuses the render_table helper defined in generate-fig-4-tables.py so
the rendering style stays identical across Ch4 and Ch5.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).parent

_spec = importlib.util.spec_from_file_location(
    "fig4tables", HERE / "generate-fig-4-tables.py"
)
_mod = importlib.util.module_from_spec(_spec)
sys.modules["fig4tables"] = _mod
_spec.loader.exec_module(_mod)
render_table = _mod.render_table
Column = _mod.Column


DECISION_COLUMNS = [
    Column("Decision",     2.1, 18),
    Column("Chosen",       2.1, 18),
    Column("Rejected alternative", 2.4, 22),
    Column("Rejected because",     4.9, 52),
    Column("Traces to",    1.9, 18, mono=True),
]

DECISION_ROWS = [
    ["Modality-isolation boundary",
     "Shared rasterise, shared parse/normalise/persist; only OCR-or-vision step varies inside a condition",
     "Two independent pipelines per modality",
     "Drift between pipelines would confound modality with engineering differences and break ER1; one branch point is cheaper to audit.",
     "ER1; \u00a75.2"],

    ["Provider abstraction",
     "LLMProvider ABC + registry with lazy import",
     "Hard-coded if/elif dispatch in pipeline",
     "Adding a provider would require editing pipeline.py, coupling testing with provider choice and violating NFR4 and ER7.",
     "NFR4, ER7; \u00a75.5.1"],

    ["OCR engine abstraction",
     "OCREngine ABC + TesseractOCR adapter",
     "Direct pytesseract call in pipeline",
     "Would block substitution of EasyOCR or cloud OCR at evaluation time and collapse the failure-attribution boundary for ER5.",
     "ER5; \u00a75.5.2"],

    ["Prompt system",
     "Versioned file in prompts/, selected by config, schema description injected at render time",
     "Inline string constants in code",
     "Diff-only audit of prompt identity across conditions would be impossible, defeating ER2 prompt invariance.",
     "ER2; \u00a75.5.3"],

    ["Data contract",
     "One Pydantic BillExtraction shared by prompt, LLM output, normaliser, evaluator and reporter",
     "Per-layer dataclasses or raw dict",
     "A shared contract enforces schema agreement in one place; alternatives risk silent divergence between layers on a field rename.",
     "FR2, NFR4; \u00a75.6"],

    ["Normalisation boundary",
     "Same normaliser over prediction and ground truth before comparison",
     "Normalise prediction only",
     "Would push format parity onto annotators and count correct-but-different-format extractions as errors, inflating the incorrect class.",
     "ER6; \u00a75.7"],

    ["Structured output handling",
     "OpenAI Structured Outputs; prompt-instructed JSON + fence strip + brace extraction for providers without it",
     "Force prompt-instructed JSON on both providers for parity",
     "Would discard a capability that gives OpenAI guaranteed schema adherence; the asymmetry is recorded and checked empirically rather than hidden.",
     "ER2, NFR8; \u00a75.5.4"],

    ["Decoupling pipeline from evaluator",
     "Disk as the only interface: evaluator reads per-run artefacts",
     "Shared in-memory objects or a database",
     "Disk gives replay, partial re-evaluation and external inspection for free; in-memory coupling makes error isolation and resume harder.",
     "NFR1, NFR3; \u00a75.9"],

    ["Per-document persistence",
     "Write extraction, raw output and timings immediately; resume skips completed documents",
     "All-or-nothing batch persistence",
     "A crash on document 40 would discard 39 previous extractions and repeat them on restart, burning API cost and risking drift from upstream changes.",
     "FR9, NFR3; \u00a75.9"],

    ["Failure diagnosis",
     "Substring heuristic on stored OCR text; vision failures attributed to the vision model",
     "Trained classifier for failure attribution",
     "Introduces a second unvalidated ML component inside the evaluator, breaking ER4 auditability; the heuristic is explicit and inspectable.",
     "ER5; \u00a75.8.3"],
]

render_table(
    HERE / "fig-5-4-decisions-table.png",
    "Table 5.1.  Design decisions, rejected alternatives and traceability.",
    DECISION_COLUMNS, DECISION_ROWS,
)


TRACE_COLUMNS = [
    Column("ID",             0.55, 0),
    Column("Literature gap (\u00a73.x)", 2.4, 22),
    Column("Requirement (\u00a74.x)",    2.2, 22),
    Column("Design realisation (\u00a75.x)",      3.5, 36),
    Column("Test/eval hook",                     2.3, 24, mono=True),
]

TRACE_ROWS = [
    ["ER1",
     "Studies confound modality with model/prompt (\u00a73.4)",
     "Modality isolation",
     "Shared rasterise and shared post-processing; modality branch confined to a single pipeline step (\u00a75.2, \u00a75.4).",
     "test_pipeline.\nmodality_isolation;\nchap 7"],
    ["ER2",
     "Prompt drift hidden in prior cross-modality work (\u00a73.4)",
     "Multilingual and prompt-controlled coverage",
     "Versioned prompt file, schema injected at render time, identical prompt archived per run (\u00a75.5.3).",
     "run prompt.txt\ndiff per condition"],
    ["ER3",
     "Cost and latency not first-class in prior evals (\u00a73.5)",
     "Operational instrumentation",
     "Per-stage Timer, token counts, per-document dollar estimate written with the extraction (\u00a75.9).",
     "timings.json;\nmetadata.json"],
    ["ER4",
     "Non-reproducible experimental setups in comparable studies (\u00a73.4)",
     "Reproducibility",
     "Per-run snapshot of config, manifest and prompt, plus per-document artefacts; evaluator reads only from disk (\u00a75.9).",
     "per-run artefact\nset; fig 5.6"],
    ["ER5",
     "Aggregate metrics hide OCR vs LLM failure (\u00a73.3)",
     "Failure attribution",
     "Substring search against persisted ocr_text.txt for OCR conditions; vision failures attributed to the vision model (\u00a75.8.3).",
     "diagnosis.json;\ntest_evaluation"],
    ["ER6",
     "Null-blind metrics inflate accuracy on sparse bills (\u00a73.5)",
     "Null-aware evaluation",
     "Four-class taxonomy applied at evaluation time; both-null excluded from the denominator (\u00a75.8.2).",
     "evaluation.json\nnull blocks"],
    ["ER7",
     "Single-model studies cannot separate provider from modality (\u00a73.4)",
     "Cross-provider generality",
     "LLMProvider abstraction; factorial design tests one OpenAI and one Anthropic model across both modalities (\u00a75.5.1, fig 4.1).",
     "comparison.json\n2x2 matrix"],
]

render_table(
    HERE / "fig-5-7-traceability-matrix.png",
    "Table 5.2.  End-to-end traceability from literature gap to evaluation hook.",
    TRACE_COLUMNS, TRACE_ROWS,
)
