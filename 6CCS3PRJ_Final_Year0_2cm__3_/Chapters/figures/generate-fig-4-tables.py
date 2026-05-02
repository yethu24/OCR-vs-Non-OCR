"""Generate Chapter 4 table screenshot figures fig-4-2 .. fig-4-6.

Renders each table as a cleanly-typeset matplotlib figure with fixed
column widths, explicit row wrapping, banded rows, and booktabs-style
horizontal rules. Produces one PNG per table.
"""
from __future__ import annotations

import textwrap
from pathlib import Path
from dataclasses import dataclass
from typing import Iterable

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

OUT_DIR = Path(__file__).parent


@dataclass
class Column:
    header: str
    width_in: float
    wrap: int
    mono: bool = False
    align: str = "left"


def render_table(
    out_path: Path,
    title: str,
    columns: list[Column],
    rows: list[list[str]],
    *,
    header_fs: int = 10,
    body_fs: int = 9,
    line_height_in: float = 0.22,
    row_pad_in: float = 0.10,
    title_fs: int = 11,
):
    wrapped_rows: list[list[list[str]]] = []
    for row in rows:
        wrapped_row = []
        for col, cell in zip(columns, row):
            if col.wrap <= 0:
                wrapped_row.append([cell])
            else:
                wrapped_row.append(textwrap.wrap(cell, width=col.wrap)
                                   or [""])
        wrapped_rows.append(wrapped_row)

    header_lines = [textwrap.wrap(c.header, width=max(c.wrap, 12)) or [""]
                    for c in columns]

    def row_height(wrapped_row):
        return max(len(cell) for cell in wrapped_row) * line_height_in + \
               2 * row_pad_in

    header_h = max(len(h) for h in header_lines) * line_height_in + \
               2 * row_pad_in

    body_h_each = [row_height(r) for r in wrapped_rows]
    total_body_h = sum(body_h_each)

    title_h = 0.45 if title else 0.0
    fig_w = sum(c.width_in for c in columns) + 0.4
    fig_h = title_h + header_h + total_body_h + 0.6

    fig, ax = plt.subplots(figsize=(fig_w, fig_h))

    x0 = 0.2
    total_table_w = sum(c.width_in for c in columns)
    y_top = fig_h - 0.25

    if title:
        ax.text(x0 + total_table_w / 2, y_top - 0.05, title,
                ha="center", va="top", fontsize=title_fs, fontweight="bold")
        y_top -= title_h

    col_xs = [x0]
    for col in columns:
        col_xs.append(col_xs[-1] + col.width_in)

    ax.plot([x0, x0 + total_table_w], [y_top, y_top],
            color="black", linewidth=1.6)

    for i, col in enumerate(columns):
        cell_x = col_xs[i]
        text = "\n".join(header_lines[i])
        ax.text(cell_x + 0.08, y_top - row_pad_in, text,
                ha="left", va="top", fontsize=header_fs,
                fontweight="bold")

    y_mid = y_top - header_h
    ax.plot([x0, x0 + total_table_w], [y_mid, y_mid],
            color="black", linewidth=0.8)

    cur_y = y_mid
    for ri, wrapped_row in enumerate(wrapped_rows):
        h = body_h_each[ri]
        if ri % 2 == 0:
            ax.add_patch(Rectangle((x0, cur_y - h), total_table_w, h,
                                   facecolor="#f7f7f7", edgecolor="none"))
        for ci, (col, cell_lines) in enumerate(zip(columns, wrapped_row)):
            cell_x = col_xs[ci]
            text = "\n".join(cell_lines)
            kwargs = dict(fontsize=body_fs, va="top")
            if col.mono:
                kwargs["fontfamily"] = "monospace"
            if col.align == "right":
                ax.text(cell_x + col.width_in - 0.08,
                        cur_y - row_pad_in, text, ha="right", **kwargs)
            elif col.align == "center":
                ax.text(cell_x + col.width_in / 2,
                        cur_y - row_pad_in, text, ha="center", **kwargs)
            else:
                ax.text(cell_x + 0.08, cur_y - row_pad_in, text,
                        ha="left", **kwargs)
        cur_y -= h

    ax.plot([x0, x0 + total_table_w], [cur_y, cur_y],
            color="black", linewidth=1.6)

    ax.set_xlim(0, fig_w)
    ax.set_ylim(cur_y - 0.25, fig_h)
    ax.axis("off")
    fig.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"Wrote {out_path}")


FR_COLUMNS = [
    Column("ID", 0.6, 0),
    Column("Requirement", 6.5, 72),
    Column("Priority", 0.9, 0),
    Column("Verification", 2.5, 24, mono=True),
]

FR_ROWS = [
    ["FR1",
     "Ingest documents via a manifest-driven dataset loader that validates the existence of both the source PDF and the ground-truth annotation for every runnable row.",
     "Must",
     "test_dataset_loader; persisted manifest snapshot"],
    ["FR2",
     "Extract the 12-field canonical BillExtraction schema (\u00a74.7) from each input document.",
     "Must",
     "test_schema; extraction.json per document"],
    ["FR3",
     "Expose an OCR-mediated pipeline and a vision-mediated pipeline that share identical LLM reasoning engine, prompt, and post-processing within a condition.",
     "Must",
     "ER1; test_pipeline"],
    ["FR4",
     "Persist per document: extracted schema, raw LLM response, OCR text (OCR-mediated only), per-stage timings, token and cost metadata.",
     "Must",
     "run directory; test_pipeline artefacts"],
    ["FR5",
     "Evaluate extractions under a four-class null-aware taxonomy (correct, incorrect, hallucination, omission) with the both-null class excluded from the denominator.",
     "Must",
     "test_evaluation; evaluation.json"],
    ["FR6",
     "Diagnose each incorrect or missing field and attribute it to OCR, LLM reasoning, or vision-model failure.",
     "Must",
     "test_evaluation; diagnosis.json"],
    ["FR7",
     "Compare an arbitrary number of runs and produce accuracy, performance, null-taxonomy, and slice matrices for every condition under comparison.",
     "Must",
     "test_evaluation; comparison.json"],
    ["FR8",
     "Emit the six canonical chart figures of \u00a74.8 for any comparison, suitable for direct inclusion in the evaluation chapter.",
     "Must",
     "test_reporting; results/reports/"],
    ["FR9",
     "Resume an interrupted run, skipping documents with a complete persisted extraction unless forced.",
     "Should",
     "test_pipeline resume path"],
    ["FR10",
     "Expose a single CLI with run, evaluate, compare, and report commands.",
     "Should",
     "test_cli"],
]

render_table(
    OUT_DIR / "fig-4-2-fr-table.png",
    "Table 4.1.  Functional requirements.",
    FR_COLUMNS, FR_ROWS,
)

NFR_COLUMNS = [
    Column("ID", 0.7, 0),
    Column("Property", 2.0, 16),
    Column("Requirement", 5.3, 58),
    Column("Verification", 2.4, 24, mono=True),
]

NFR_ROWS = [
    ["NFR1", "Reproducibility",
     "Every run persists a snapshot of the effective configuration, the manifest used, and the exact prompt template applied.",
     "per-run artefact set"],
    ["NFR2", "Determinism",
     "LLM sampling temperature fixed at 0.0 across all conditions; any deviation logged to run metadata.",
     "config.yaml; run metadata"],
    ["NFR3", "Error isolation",
     "A failure on one document produces an error.json for that document and does not abort the run over remaining documents.",
     "test_pipeline negative path"],
    ["NFR4", "Extensibility",
     "Adding a new LLM provider requires one provider module and one registry entry, with no changes to pipeline, evaluator, or CLI.",
     "LLMProvider contract review"],
    ["NFR5", "Multilingual coverage",
     "The OCR-mediated pipeline supports the Tesseract language packs eng, deu, fra, ita at minimum, selected per document from the manifest.",
     "test_ocr language mapping"],
    ["NFR6", "Cost observability",
     "Token usage and a derived per-document dollar estimate are recorded for every LLM call.",
     "metadata.json; test_performance"],
    ["NFR7", "Timing observability",
     "Each pipeline stage (rasterise, OCR, LLM, parse and normalise) is timed per document.",
     "timings.json; test_performance"],
    ["NFR8", "Auditability",
     "The raw verbatim LLM response is retained for every document, independently of whether it parsed.",
     "raw_llm_output.txt"],
]

render_table(
    OUT_DIR / "fig-4-3-nfr-table.png",
    "Table 4.2.  Non-functional requirements.",
    NFR_COLUMNS, NFR_ROWS,
)

ER_COLUMNS = [
    Column("ID", 0.7, 0),
    Column("Class", 2.3, 18),
    Column("Requirement", 5.4, 58),
    Column("Source", 2.1, 22),
]

ER_ROWS = [
    ["ER1", "Modality isolation",
     "LLM reasoning engine, prompt, and post-processing are held absolutely constant across OCR-mediated and vision-mediated pipelines within a condition; only input modality varies within a provider row.",
     "\u00a73.5 (i), (ii); \u00a73.3"],
    ["ER2", "Multilingual coverage",
     "Dataset spans at least two languages; accuracy reported in aggregate and sliced by language.",
     "\u00a7\u00a73.2, 3.5 (iii)"],
    ["ER3", "Operational instrumentation",
     "Per-stage wall-clock latency and per-document dollar cost are first-class metrics for every document in every condition.",
     "\u00a7\u00a73.4, 3.5 (iv)"],
    ["ER4", "Reproducibility",
     "Every run archives configuration, manifest, prompt template, and per-document artefacts sufficient to reconstruct the run.",
     "\u00a73.6"],
    ["ER5", "Failure attribution",
     "Every non-correct extraction in OCR-mediated conditions is attributed automatically to OCR or LLM; vision-mediated failures are attributed to the vision model.",
     "\u00a7\u00a73.2, 3.6"],
    ["ER6", "Null-aware evaluation",
     "Accuracy computed under the four-class taxonomy separating correct-absence, hallucination, omission, and value mismatch; both-null excluded from denominator.",
     "\u00a73.6; MUC-7"],
    ["ER7", "Cross-provider generality",
     "Comparison repeated with two providers from different architectural families so that provider-specificity is testable rather than assumed.",
     "\u00a7\u00a73.3, 3.5"],
]

render_table(
    OUT_DIR / "fig-4-4-er-table.png",
    "Table 4.3.  Experimental requirements with upstream traceability.",
    ER_COLUMNS, ER_ROWS,
)

SCHEMA_COLUMNS = [
    Column("Field", 3.3, 0, mono=True),
    Column("Type", 1.5, 0, mono=True),
    Column("Rationale", 7.0, 74),
]

SCHEMA_ROWS = [
    ["provider_name",         "string", "Issuer identity; legal suffixes stripped before comparison."],
    ["utility_type",          "enum",   "electricity | gas | water."],
    ["bill_number",           "string", "Invoice or bill reference."],
    ["bill_date",             "date",   "Issue date, ISO 8601."],
    ["billing_period_start",  "date",   "Period start, ISO 8601."],
    ["billing_period_end",    "date",   "Period end, ISO 8601."],
    ["due_date",              "date",   "Payment deadline, ISO 8601."],
    ["total_amount_due",      "float",  "Amount payable."],
    ["currency",              "string", "ISO 4217 code."],
    ["account_number",        "string", "Customer account reference."],
    ["consumption_amount",    "float",  "Usage quantity."],
    ["consumption_unit",      "string", "kWh, m^3, SMC, L, therm, etc."],
]

render_table(
    OUT_DIR / "fig-4-5-schema-table.png",
    "Table 4.4.  The 12-field BillExtraction schema.",
    SCHEMA_COLUMNS, SCHEMA_ROWS,
)

NULL_COLUMNS = [
    Column("Ground truth", 1.7, 0, mono=True, align="center"),
    Column("Prediction",   2.2, 0, mono=True, align="center"),
    Column("Class",        1.8, 0, align="center"),
    Column("In denom.",    1.2, 0, align="center"),
    Column("Counted as",   1.5, 0, align="center"),
]

NULL_ROWS = [
    ["value", "value, equal",     "Correct",        "yes", "positive"],
    ["value", "value, mismatch",  "Incorrect",      "yes", "negative"],
    ["null",  "value",            "Hallucination",  "yes", "negative"],
    ["value", "null",             "Omission",       "yes", "negative"],
    ["null",  "null",             "Both-null",      "no",  "excluded"],
]

render_table(
    OUT_DIR / "fig-4-6-null-taxonomy.png",
    "Table 4.5.  Null-aware evaluation taxonomy.",
    NULL_COLUMNS, NULL_ROWS,
)
