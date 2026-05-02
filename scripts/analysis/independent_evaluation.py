"""Independent re-analysis of the four-way OCR vs Vision experiment.

Reads every per-document artefact from disk, recomputes headline metrics,
verifies them against comparison.json, and emits derived CSVs that the
markdown report draws on. Designed to be deterministic and reproducible:
running this script regenerates every number cited in the accompanying
markdown report.

Outputs (all under results/reports/four_way_20260429/derived/):
  - field_long.csv          one row per (run, doc_id, field_name)
  - run_metrics.csv         recomputed run-level metrics
  - field_matrix.csv        per-field accuracy per run
  - null_counts.csv         hallucination/omission/both_null per run
  - modality_gap_by_<slice>.csv     accuracy by language / utility_type / page bucket / digital_native / provider
  - flip_table.csv          per provider: doc_id x field with OCR/Vision verdicts and flip flag
  - flip_summary.csv        per provider, per field counts of OCR-only-correct / Vision-only-correct / both / neither
  - agreement.csv           per modality, doc x field cross-provider agreement
  - diagnosis_audit.csv     OCR-mode failures with strict + relaxed substring rule + true cause label hooks
  - page_coverage.csv       per doc: page_count, OCR text length, page-marker hits
  - timings_by_pages.csv    cost and latency stratified by page-count bucket
"""

from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path
from typing import Any

import pandas as pd

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parents[2]
RUNS_DIR = ROOT / "results" / "runs"
REPORTS_DIR = ROOT / "results" / "reports" / "four_way_20260429"
DERIVED_DIR = REPORTS_DIR / "derived"
GT_DIR = ROOT / "data" / "ground_truth"

RUN_DIRS = {
    "sonnet_ocr":   RUNS_DIR / "20260429_204310_anthropic_claudesonnet4520250929_ocr_text",
    "sonnet_vision": RUNS_DIR / "20260429_205453_anthropic_claudesonnet4520250929_vision",
    "gpt4o_ocr":    RUNS_DIR / "20260429_210332_openai_gpt4o_ocr_text",
    "gpt4o_vision": RUNS_DIR / "20260429_211339_openai_gpt4o_vision",
}

PROVIDERS = ["sonnet", "gpt4o"]
MODALITIES = ["ocr", "vision"]

SCHEMA_FIELDS = [
    "provider_name", "utility_type", "bill_number", "bill_date",
    "billing_period_start", "billing_period_end", "due_date",
    "total_amount_due", "currency", "account_number",
    "consumption_amount", "consumption_unit",
]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def page_bucket(p: int) -> str:
    if p <= 2:
        return "1-2"
    if p <= 4:
        return "3-4"
    return "5+"


def load_manifest() -> pd.DataFrame:
    # Use any of the run snapshots since they are identical
    df = pd.read_csv(RUN_DIRS["sonnet_ocr"] / "manifest_snapshot.csv")
    df["page_bucket"] = df["page_count"].astype(int).apply(page_bucket)
    # Rename to avoid collision with field_df.provider (sonnet/gpt4o)
    df = df.rename(columns={"provider": "issuer"})
    return df.set_index("document_id")


def load_field_long() -> pd.DataFrame:
    """Long-form table: one row per (run, doc_id, field_name).

    Columns: run, provider, modality, doc_id, field_name, category,
             match (bool), predicted, ground_truth, similarity.
    """
    rows: list[dict] = []
    for run_key, run_dir in RUN_DIRS.items():
        provider, modality = run_key.split("_")
        ev = load_json(run_dir / "evaluation.json")
        for doc_id, doc in ev["documents"].items():
            for fr in doc["fields"]:
                rows.append({
                    "run": run_key,
                    "provider": provider,
                    "modality": modality,
                    "doc_id": doc_id,
                    "field_name": fr["field_name"],
                    "category": fr["category"],
                    "match": bool(fr["match"]),
                    "predicted": fr["predicted"],
                    "ground_truth": fr["ground_truth"],
                    "similarity": fr["similarity"],
                })
    return pd.DataFrame(rows)


def load_run_perf() -> pd.DataFrame:
    """Per-document timing + cost from each run, joined for cross-tab analyses."""
    rows: list[dict] = []
    for run_key, run_dir in RUN_DIRS.items():
        provider, modality = run_key.split("_")
        for doc_dir in sorted((run_dir / "documents").iterdir()):
            if not doc_dir.is_dir():
                continue
            timings_path = doc_dir / "timings.json"
            metadata_path = doc_dir / "metadata.json"
            if not timings_path.exists() or not metadata_path.exists():
                continue
            t = load_json(timings_path)
            m = load_json(metadata_path)
            rows.append({
                "run": run_key,
                "provider": provider,
                "modality": modality,
                "doc_id": doc_dir.name,
                "total_ms": t.get("total_ms", 0.0),
                "pdf_to_images_ms": t.get("pdf_to_images_ms", 0.0),
                "ocr_ms": t.get("ocr_ms", 0.0),
                "llm_call_ms": t.get("llm_call_ms", 0.0),
                "parse_normalise_ms": t.get("parse_normalise_ms", 0.0),
                "input_tokens": int((m.get("token_usage") or {}).get("input_tokens", 0) or 0),
                "output_tokens": int((m.get("token_usage") or {}).get("output_tokens", 0) or 0),
                "cost_usd": m.get("estimated_cost_usd", 0.0),
            })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Headline metrics
# ---------------------------------------------------------------------------


def compute_run_metrics(field_df: pd.DataFrame, perf_df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for run_key in RUN_DIRS:
        sub = field_df[field_df["run"] == run_key]
        # both_null excluded from denominator (per spec)
        evaluated = sub[sub["category"] != "both_null"]
        n_correct = int((evaluated["category"] == "correct").sum())
        n_eval = len(evaluated)
        overall_acc = n_correct / n_eval if n_eval else 0.0

        # doc-level: a doc is correct if no incorrect/hallucination/omission
        bad_per_doc = (
            sub[sub["category"].isin(["incorrect", "hallucination", "omission"])]
            .groupby("doc_id").size()
        )
        n_docs = sub["doc_id"].nunique()
        n_perfect = n_docs - bad_per_doc.size
        doc_acc = n_perfect / n_docs if n_docs else 0.0

        # null counts
        halluc = int((sub["category"] == "hallucination").sum())
        omiss = int((sub["category"] == "omission").sum())
        both_null = int((sub["category"] == "both_null").sum())

        # perf
        perf_sub = perf_df[perf_df["run"] == run_key]
        rows.append({
            "run": run_key,
            "n_docs": n_docs,
            "n_eval": n_eval,
            "overall_accuracy": round(overall_acc, 4),
            "document_level_accuracy": round(doc_acc, 4),
            "hallucinations": halluc,
            "omissions": omiss,
            "both_null": both_null,
            "mean_total_ms": round(perf_sub["total_ms"].mean(), 1),
            "mean_pdf_ms": round(perf_sub["pdf_to_images_ms"].mean(), 1),
            "mean_ocr_ms": round(perf_sub["ocr_ms"].mean(), 1),
            "mean_llm_ms": round(perf_sub["llm_call_ms"].mean(), 1),
            "mean_parse_ms": round(perf_sub["parse_normalise_ms"].mean(), 1),
            "total_cost_usd": round(perf_sub["cost_usd"].sum(), 4),
            "total_input_tokens": int(perf_sub["input_tokens"].sum()),
            "total_output_tokens": int(perf_sub["output_tokens"].sum()),
        })
    return pd.DataFrame(rows).set_index("run")


def compute_field_matrix(field_df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for run_key in RUN_DIRS:
        sub = field_df[field_df["run"] == run_key]
        eval_sub = sub[sub["category"] != "both_null"]
        for fname in SCHEMA_FIELDS:
            f_sub = eval_sub[eval_sub["field_name"] == fname]
            n_eval = len(f_sub)
            n_correct = int((f_sub["category"] == "correct").sum())
            rows.append({
                "run": run_key,
                "field": fname,
                "n_eval": n_eval,
                "n_correct": n_correct,
                "accuracy": round(n_correct / n_eval, 4) if n_eval else 0.0,
            })
    return pd.DataFrame(rows)


def verify_against_comparison(my_metrics: pd.DataFrame, my_field_matrix: pd.DataFrame) -> list[str]:
    cmp_data = load_json(REPORTS_DIR / "comparison.json")
    cmp_acc = cmp_data["accuracy_matrix"]
    cmp_null = cmp_data["null_analysis"]
    cmp_perf = cmp_data["performance_matrix"]
    inconsistencies: list[str] = []

    label_map = {
        "20260429_204310_anthropic_claudesonnet4520250929_ocr_text": "sonnet_ocr",
        "20260429_205453_anthropic_claudesonnet4520250929_vision": "sonnet_vision",
        "20260429_210332_openai_gpt4o_ocr_text": "gpt4o_ocr",
        "20260429_211339_openai_gpt4o_vision": "gpt4o_vision",
    }
    for cmp_label, run_key in label_map.items():
        ours = my_metrics.loc[run_key]
        theirs = cmp_acc[cmp_label]
        # Overall accuracy
        if abs(ours["overall_accuracy"] - theirs["overall_accuracy"]) > 1e-3:
            inconsistencies.append(
                f"overall_accuracy mismatch for {run_key}: ours={ours['overall_accuracy']} cmp={theirs['overall_accuracy']}"
            )
        if abs(ours["document_level_accuracy"] - theirs["document_level_accuracy"]) > 1e-3:
            inconsistencies.append(
                f"document_level_accuracy mismatch for {run_key}: ours={ours['document_level_accuracy']} cmp={theirs['document_level_accuracy']}"
            )
        # Per field
        for fname in SCHEMA_FIELDS:
            ours_f = my_field_matrix[(my_field_matrix["run"] == run_key) & (my_field_matrix["field"] == fname)]["accuracy"].iloc[0]
            theirs_f = theirs[fname]
            if abs(ours_f - theirs_f) > 1e-3:
                inconsistencies.append(
                    f"per-field {fname} mismatch for {run_key}: ours={ours_f} cmp={theirs_f}"
                )
        # Null counts
        nulls = cmp_null[cmp_label]
        if int(ours["hallucinations"]) != int(nulls["hallucinations"]):
            inconsistencies.append(f"hallucinations mismatch for {run_key}: ours={ours['hallucinations']} cmp={nulls['hallucinations']}")
        if int(ours["omissions"]) != int(nulls["omissions"]):
            inconsistencies.append(f"omissions mismatch for {run_key}: ours={ours['omissions']} cmp={nulls['omissions']}")
        if int(ours["both_null"]) != int(nulls["both_null"]):
            inconsistencies.append(f"both_null mismatch for {run_key}: ours={ours['both_null']} cmp={nulls['both_null']}")
        # Cost
        their_cost = cmp_perf[cmp_label]["total_estimated_cost_usd"]
        if abs(ours["total_cost_usd"] - their_cost) > 0.001:
            inconsistencies.append(f"cost mismatch for {run_key}: ours={ours['total_cost_usd']} cmp={their_cost}")
    return inconsistencies


# ---------------------------------------------------------------------------
# Stratification
# ---------------------------------------------------------------------------


def stratified_accuracy(field_df: pd.DataFrame, manifest: pd.DataFrame, slice_col: str) -> pd.DataFrame:
    """Within-provider modality gap stratified by *slice_col*."""
    merged = field_df.merge(manifest[[slice_col]], left_on="doc_id", right_index=True)
    eval_sub = merged[merged["category"] != "both_null"]
    rows = []
    for slice_val in sorted(merged[slice_col].astype(str).unique()):
        s = eval_sub[eval_sub[slice_col].astype(str) == slice_val]
        n_docs = s["doc_id"].nunique()
        for run_key in RUN_DIRS:
            ss = s[s["run"] == run_key]
            n_eval = len(ss)
            n_correct = int((ss["category"] == "correct").sum())
            acc = n_correct / n_eval if n_eval else 0.0
            rows.append({
                "slice": slice_val,
                "n_docs": n_docs,
                "run": run_key,
                "n_eval": n_eval,
                "n_correct": n_correct,
                "accuracy": round(acc, 4),
            })
    return pd.DataFrame(rows)


def modality_gap_table(strat: pd.DataFrame) -> pd.DataFrame:
    """Pivot stratified table into within-provider gap (vision - ocr)."""
    p = strat.pivot_table(index="slice", columns="run", values="accuracy")
    p["sonnet_gap_v_minus_o"] = (p.get("sonnet_vision", 0) - p.get("sonnet_ocr", 0)).round(4)
    p["gpt4o_gap_v_minus_o"] = (p.get("gpt4o_vision", 0) - p.get("gpt4o_ocr", 0)).round(4)
    return p


# ---------------------------------------------------------------------------
# Within-document modality flips (per provider)
# ---------------------------------------------------------------------------


def flip_table(field_df: pd.DataFrame) -> pd.DataFrame:
    """For each provider, build doc x field with OCR and Vision verdicts."""
    rows = []
    for prov in PROVIDERS:
        sub = field_df[field_df["provider"] == prov]
        ocr_df = sub[sub["modality"] == "ocr"].set_index(["doc_id", "field_name"])
        vis_df = sub[sub["modality"] == "vision"].set_index(["doc_id", "field_name"])
        # Iterate over union of indices
        idx = ocr_df.index.union(vis_df.index)
        for doc_id, field in idx:
            o = ocr_df.loc[(doc_id, field)] if (doc_id, field) in ocr_df.index else None
            v = vis_df.loc[(doc_id, field)] if (doc_id, field) in vis_df.index else None
            o_cat = o["category"] if o is not None else None
            v_cat = v["category"] if v is not None else None
            o_correct = (o_cat == "correct") if o_cat else None
            v_correct = (v_cat == "correct") if v_cat else None
            # Only count flips on fields evaluated in both (exclude both_null in either)
            both_eval = (o_cat not in (None, "both_null")) and (v_cat not in (None, "both_null"))
            ocr_only = bool(o_correct) and not bool(v_correct) if both_eval else False
            vis_only = bool(v_correct) and not bool(o_correct) if both_eval else False
            rows.append({
                "provider": prov,
                "doc_id": doc_id,
                "field": field,
                "ocr_category": o_cat,
                "vision_category": v_cat,
                "ocr_correct": o_correct,
                "vision_correct": v_correct,
                "ocr_only_correct": ocr_only,
                "vision_only_correct": vis_only,
                "both_correct": bool(o_correct) and bool(v_correct) if both_eval else False,
                "neither_correct": (o_correct is False and v_correct is False) if both_eval else False,
                "both_evaluated": both_eval,
                "ocr_predicted": (o["predicted"] if o is not None else None),
                "vision_predicted": (v["predicted"] if v is not None else None),
                "ground_truth": (o["ground_truth"] if o is not None else (v["ground_truth"] if v is not None else None)),
            })
    return pd.DataFrame(rows)


def flip_summary(flips: pd.DataFrame) -> pd.DataFrame:
    g = flips[flips["both_evaluated"]].groupby(["provider", "field"]).agg(
        ocr_only_correct=("ocr_only_correct", "sum"),
        vision_only_correct=("vision_only_correct", "sum"),
        both_correct=("both_correct", "sum"),
        neither_correct=("neither_correct", "sum"),
        n=("both_evaluated", "sum"),
    ).reset_index()
    return g


# ---------------------------------------------------------------------------
# Cross-provider agreement (per modality)
# ---------------------------------------------------------------------------


def normalised_pred(value: Any) -> str:
    """Stable string representation for agreement comparison."""
    if value is None:
        return "<NULL>"
    return str(value).strip().lower()


def agreement_table(field_df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for mod in MODALITIES:
        sub = field_df[field_df["modality"] == mod]
        sonnet = sub[sub["provider"] == "sonnet"].set_index(["doc_id", "field_name"])
        gpt4o = sub[sub["provider"] == "gpt4o"].set_index(["doc_id", "field_name"])
        idx = sonnet.index.intersection(gpt4o.index)
        for doc_id, field in idx:
            s = sonnet.loc[(doc_id, field)]
            g = gpt4o.loc[(doc_id, field)]
            s_pred = normalised_pred(s["predicted"])
            g_pred = normalised_pred(g["predicted"])
            agree = s_pred == g_pred
            s_correct = (s["category"] == "correct")
            g_correct = (g["category"] == "correct")
            rows.append({
                "modality": mod,
                "doc_id": doc_id,
                "field": field,
                "sonnet_pred": s_pred,
                "gpt4o_pred": g_pred,
                "agree": agree,
                "sonnet_correct": bool(s_correct),
                "gpt4o_correct": bool(g_correct),
                "ground_truth": s["ground_truth"],
                "sonnet_category": s["category"],
                "gpt4o_category": g["category"],
            })
    return pd.DataFrame(rows)


def agreement_summary(agree_df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for mod in MODALITIES:
        sub = agree_df[agree_df["modality"] == mod]
        # exclude both-null pairs (they trivially agree on null)
        evaluated = sub[~((sub["sonnet_category"] == "both_null") & (sub["gpt4o_category"] == "both_null"))]
        n = len(evaluated)
        if n == 0:
            continue
        n_agree = int(evaluated["agree"].sum())
        n_disagree = n - n_agree
        # disagreement breakdown
        disagree = evaluated[~evaluated["agree"]]
        n_one_right = int(((disagree["sonnet_correct"] | disagree["gpt4o_correct"])).sum())
        n_neither_right = int(((~disagree["sonnet_correct"]) & (~disagree["gpt4o_correct"])).sum())
        n_sonnet_only_right = int((disagree["sonnet_correct"] & ~disagree["gpt4o_correct"]).sum())
        n_gpt4o_only_right = int((disagree["gpt4o_correct"] & ~disagree["sonnet_correct"]).sum())
        rows.append({
            "modality": mod,
            "n_evaluated": n,
            "n_agree": n_agree,
            "agreement_rate": round(n_agree / n, 4),
            "n_disagree": n_disagree,
            "disagree_one_right": n_one_right,
            "disagree_neither_right": n_neither_right,
            "disagree_sonnet_only_right": n_sonnet_only_right,
            "disagree_gpt4o_only_right": n_gpt4o_only_right,
        })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Diagnosis heuristic audit (OCR-mode failures only)
# ---------------------------------------------------------------------------


def value_in_text(value: Any, text: str) -> bool:
    if value is None:
        return False
    needle = str(value).strip().lower()
    if not needle:
        return False
    return needle in text.lower()


def value_in_text_relaxed(value: Any, text: str) -> bool:
    """Whitespace + non-alnum-stripped substring match. Handles e.g. '0 0000 000' vs '00000000'."""
    if value is None:
        return False
    needle = re.sub(r"[^a-z0-9]", "", str(value).lower())
    haystack = re.sub(r"[^a-z0-9]", "", text.lower())
    if not needle:
        return False
    return needle in haystack


def diagnosis_audit(field_df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for prov in PROVIDERS:
        run_key = f"{prov}_ocr"
        run_dir = RUN_DIRS[run_key]
        sub = field_df[(field_df["run"] == run_key)
                       & field_df["category"].isin(["incorrect", "hallucination", "omission"])]
        for _, fr in sub.iterrows():
            ocr_path = run_dir / "documents" / fr["doc_id"] / "ocr_text.txt"
            text = ocr_path.read_text(encoding="utf-8") if ocr_path.exists() else ""
            strict = value_in_text(fr["ground_truth"], text)
            relaxed = value_in_text_relaxed(fr["ground_truth"], text)
            # Heuristic decision per spec
            if fr["category"] == "hallucination":
                # gt is null - not applicable; pick LLM-attribution by convention
                strict_attr = "llm_extraction_failure"
            else:
                strict_attr = "llm_extraction_failure" if (fr["ground_truth"] is None or strict) else "ocr_failure"
            relaxed_attr = "llm_extraction_failure" if (fr["ground_truth"] is None or relaxed) else "ocr_failure"
            rows.append({
                "provider": prov,
                "doc_id": fr["doc_id"],
                "field": fr["field_name"],
                "category": fr["category"],
                "ground_truth": fr["ground_truth"],
                "predicted": fr["predicted"],
                "strict_in_ocr": strict,
                "relaxed_in_ocr": relaxed,
                "strict_attribution": strict_attr,
                "relaxed_attribution": relaxed_attr,
                "disagree": strict_attr != relaxed_attr,
            })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Page coverage check
# ---------------------------------------------------------------------------


_PAGE_MARKER_RE = re.compile(
    r"(\bpage\s*\d+\s*of\s*\d+\b|\bseite\s*\d+\s*(von|/)\s*\d+\b|\bpagina\s*\d+\s*(di|/)\s*\d+\b|\bp\.\s*\d+\s*/\s*\d+\b)",
    re.IGNORECASE,
)


def page_coverage(manifest: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for prov in PROVIDERS:
        run_dir = RUN_DIRS[f"{prov}_ocr"]
        for doc_dir in sorted((run_dir / "documents").iterdir()):
            if not doc_dir.is_dir():
                continue
            doc_id = doc_dir.name
            ocr_path = doc_dir / "ocr_text.txt"
            if not ocr_path.exists():
                continue
            text = ocr_path.read_text(encoding="utf-8")
            page_count = int(manifest.loc[doc_id, "page_count"])
            markers = _PAGE_MARKER_RE.findall(text)
            rows.append({
                "provider": prov,
                "doc_id": doc_id,
                "page_count": page_count,
                "ocr_chars": len(text),
                "ocr_lines": text.count("\n") + 1,
                "page_markers_found": len(markers),
                "first_marker": markers[0] if markers else "",
            })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Latency / cost stratified by page bucket
# ---------------------------------------------------------------------------


def perf_by_page_bucket(perf_df: pd.DataFrame, manifest: pd.DataFrame) -> pd.DataFrame:
    merged = perf_df.merge(manifest[["page_bucket", "page_count"]], left_on="doc_id", right_index=True)
    g = merged.groupby(["run", "page_bucket"]).agg(
        n=("doc_id", "count"),
        mean_total_ms=("total_ms", "mean"),
        mean_ocr_ms=("ocr_ms", "mean"),
        mean_llm_ms=("llm_call_ms", "mean"),
        mean_cost_usd=("cost_usd", "mean"),
        sum_cost_usd=("cost_usd", "sum"),
    ).round(2).reset_index()
    return g


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    DERIVED_DIR.mkdir(parents=True, exist_ok=True)

    print("Loading manifest and per-document artefacts ...")
    manifest = load_manifest()
    field_df = load_field_long()
    perf_df = load_run_perf()

    field_df.to_csv(DERIVED_DIR / "field_long.csv", index=False)
    perf_df.to_csv(DERIVED_DIR / "perf_long.csv", index=False)

    # ---- Headline metrics ----
    print("Recomputing headline metrics ...")
    metrics = compute_run_metrics(field_df, perf_df)
    field_matrix = compute_field_matrix(field_df)
    metrics.to_csv(DERIVED_DIR / "run_metrics.csv")
    field_matrix.to_csv(DERIVED_DIR / "field_matrix.csv", index=False)

    null_counts = metrics[["hallucinations", "omissions", "both_null"]].copy()
    null_counts.to_csv(DERIVED_DIR / "null_counts.csv")

    # Verify
    inconsistencies = verify_against_comparison(metrics, field_matrix)
    if inconsistencies:
        print("INCONSISTENCIES vs comparison.json:")
        for line in inconsistencies:
            print("  -", line)
    else:
        print("All recomputed metrics match comparison.json (within 1e-3).")

    # ---- Stratifications ----
    print("Stratifying by language / utility_type / page_bucket / digital_native / provider issuer ...")
    for slice_col in ["language", "utility_type", "page_bucket", "digital_native", "issuer"]:
        strat = stratified_accuracy(field_df, manifest, slice_col)
        gap = modality_gap_table(strat)
        strat.to_csv(DERIVED_DIR / f"strat_{slice_col}.csv", index=False)
        gap.to_csv(DERIVED_DIR / f"modality_gap_by_{slice_col}.csv")

    # ---- Flips ----
    print("Computing within-document modality flips ...")
    flips = flip_table(field_df)
    flips.to_csv(DERIVED_DIR / "flip_table.csv", index=False)
    fsum = flip_summary(flips)
    fsum.to_csv(DERIVED_DIR / "flip_summary.csv", index=False)

    # also count: documents with at least one flip in either direction
    flip_doc_summary = flips[flips["both_evaluated"]].groupby(["provider", "doc_id"]).agg(
        any_ocr_only=("ocr_only_correct", "any"),
        any_vision_only=("vision_only_correct", "any"),
    ).reset_index()
    flip_doc_summary["any_flip"] = flip_doc_summary["any_ocr_only"] | flip_doc_summary["any_vision_only"]
    flip_doc_summary.to_csv(DERIVED_DIR / "flip_doc_summary.csv", index=False)

    # ---- Agreement ----
    print("Computing cross-provider agreement ...")
    agree_df = agreement_table(field_df)
    agree_df.to_csv(DERIVED_DIR / "agreement.csv", index=False)
    asum = agreement_summary(agree_df)
    asum.to_csv(DERIVED_DIR / "agreement_summary.csv", index=False)

    # ---- Diagnosis audit ----
    print("Auditing diagnosis heuristic on OCR-mode failures ...")
    da = diagnosis_audit(field_df)
    da.to_csv(DERIVED_DIR / "diagnosis_audit.csv", index=False)

    # ---- Page coverage ----
    print("Checking page coverage ...")
    pc = page_coverage(manifest)
    pc.to_csv(DERIVED_DIR / "page_coverage.csv", index=False)

    # ---- Performance bucketing ----
    print("Bucketing latency and cost by page count ...")
    pbg = perf_by_page_bucket(perf_df, manifest)
    pbg.to_csv(DERIVED_DIR / "timings_by_pages.csv", index=False)

    # ---- Console summary ----
    print("\n=== HEADLINE METRICS (recomputed) ===")
    print(metrics.to_string())

    print("\n=== AGREEMENT SUMMARY ===")
    print(asum.to_string(index=False))

    print("\n=== FLIP SUMMARY (top 10 per provider by vision_only_correct) ===")
    for prov in PROVIDERS:
        print(f"-- {prov} --")
        print(fsum[fsum["provider"] == prov].sort_values("vision_only_correct", ascending=False).head(10).to_string(index=False))

    print("\n=== DIAGNOSIS AUDIT: cases where strict and relaxed rules disagree ===")
    diag_disagree = da[da["disagree"]]
    print(f"strict-vs-relaxed disagreements: {len(diag_disagree)} of {len(da)} OCR-mode failure rows")
    if len(diag_disagree):
        print(diag_disagree[["provider", "doc_id", "field", "category", "ground_truth", "predicted", "strict_in_ocr", "relaxed_in_ocr"]].to_string(index=False))

    print("\n=== PAGE COVERAGE: documents with >2 pages ===")
    multi = pc[pc["page_count"] > 2]
    print(multi.groupby("provider").agg(n=("doc_id", "count"),
                                        mean_chars=("ocr_chars", "mean"),
                                        markers=("page_markers_found", "sum")).to_string())

    print("\nDerived CSVs written to:", DERIVED_DIR)
    return 0


if __name__ == "__main__":
    sys.exit(main())
