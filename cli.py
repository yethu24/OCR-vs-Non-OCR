"""CLI entry point for the OCR vs Non-OCR extraction pipeline.

Usage examples::

    python cli.py run --config config/default.yaml
    python cli.py run --config config/default.yaml --mode vision --provider openai --model gpt-4o
    python cli.py run --config config/default.yaml --force
"""

from __future__ import annotations

import click

from pathlib import Path

from src.evaluation import evaluate_run, diagnose_document, compare_runs
from src.pipeline import run_pipeline
from src.reporting import generate_report
from src.utils import load_config, read_json, setup_logging


@click.group()
def cli():
    """OCR vs Non-OCR extraction pipeline."""


@cli.command()
@click.option(
    "--config",
    "config_path",
    required=True,
    type=click.Path(exists=True),
    help="Path to YAML config file.",
)
@click.option("--manifest", default=None, type=click.Path(exists=True), help="Override manifest CSV path.")
@click.option("--mode", default=None, type=click.Choice(["ocr_text", "vision"]), help="Pipeline mode.")
@click.option("--provider", default=None, type=click.Choice(["openai", "anthropic"]), help="LLM provider.")
@click.option("--model", default=None, help="LLM model name.")
@click.option("--force", is_flag=True, default=False, help="Re-process documents even if results exist.")
def run(config_path, manifest, mode, provider, model, force):
    """Run the extraction pipeline."""
    setup_logging()

    # Build overrides dict from CLI flags; these are deep-merged into the YAML config
    overrides: dict = {}
    if manifest:
        overrides.setdefault("data", {})["manifest"] = manifest
    if mode:
        overrides.setdefault("pipeline", {})["mode"] = mode
    if provider:
        overrides.setdefault("llm", {})["provider"] = provider
    if model:
        overrides.setdefault("llm", {})["model"] = model

    config = load_config(config_path, overrides if overrides else None)

    run_dir = run_pipeline(config, force=force)
    click.echo(f"\nRun complete. Results saved to: {run_dir}")


@cli.command()
@click.option(
    "--run-dir",
    required=True,
    type=click.Path(exists=True),
    help="Path to a pipeline run directory.",
)
@click.option(
    "--gt-dir",
    default="data/ground_truth",
    type=click.Path(exists=True),
    help="Path to ground truth directory.",
)
@click.option(
    "--diagnose",
    is_flag=True,
    default=False,
    help="Run failure diagnosis on incorrect fields.",
)
def evaluate(run_dir, gt_dir, diagnose):
    """Evaluate a single pipeline run against ground truth."""
    setup_logging()

    evaluation = evaluate_run(run_dir, gt_dir)
    click.echo(f"Overall accuracy:        {evaluation.overall_accuracy:.2%}")
    click.echo(f"Document-level accuracy: {evaluation.document_level_accuracy:.2%}")
    click.echo(f"Errors skipped:          {len(evaluation.errors_skipped)}")
    click.echo()

    click.echo("Field accuracies:")
    for fname, acc in evaluation.field_accuracies.items():
        click.echo(f"  {fname:<25s} {acc:.2%}")

    if diagnose:
        # Attribute each incorrect field to OCR failure vs LLM extraction failure
        click.echo()
        click.echo("Running failure diagnosis...")
        run_dir_path = Path(run_dir)
        total_diagnosed = 0
        for doc_id, dr in evaluation.documents.items():
            if dr.all_correct:
                continue
            doc_dir = run_dir_path / "documents" / doc_id
            meta_path = doc_dir / "metadata.json"
            mode = "vision"
            if meta_path.exists():
                meta = read_json(meta_path)
                mode = meta.get("pipeline_mode", "vision")
            diags = diagnose_document(doc_id, dr, doc_dir, mode)
            total_diagnosed += len(diags)
            for d in diags:
                click.echo(f"  {doc_id} / {d.field_name}: {d.failure_type}")
        click.echo(f"\nTotal failures diagnosed: {total_diagnosed}")

    click.echo(f"\nEvaluation saved to: {Path(run_dir) / 'evaluation.json'}")


@cli.command()
@click.option(
    "--runs",
    required=True,
    multiple=True,
    type=click.Path(exists=True),
    help="Paths to run directories (repeat for each run).",
)
@click.option(
    "--gt-dir",
    default="data/ground_truth",
    type=click.Path(exists=True),
    help="Path to ground truth directory.",
)
@click.option(
    "--output",
    default="results/reports",
    type=click.Path(),
    help="Output directory for comparison report.",
)
def compare(runs, gt_dir, output):
    """Compare multiple pipeline runs (e.g. the 2x2 matrix)."""
    setup_logging()

    report = compare_runs(list(runs), gt_dir, output)

    click.echo("Accuracy matrix:")
    for label, row in report["accuracy_matrix"].items():
        overall = row["overall_accuracy"]
        doc_lvl = row["document_level_accuracy"]
        click.echo(f"  {label}")
        click.echo(f"    Overall: {overall:.2%}  Document-level: {doc_lvl:.2%}")

    click.echo()
    click.echo("Performance matrix:")
    for label, perf in report["performance_matrix"].items():
        click.echo(f"  {label}")
        click.echo(
            f"    Mean total: {perf.get('mean_total_ms', 0):.0f}ms  "
            f"Mean LLM: {perf.get('mean_llm_call_ms', 0):.0f}ms  "
            f"Cost: ${perf.get('total_estimated_cost_usd', 0):.4f}"
        )

    click.echo(f"\nComparison saved to: {Path(output) / 'comparison.json'}")


@cli.command()
@click.option(
    "--comparison",
    default="results/reports/comparison.json",
    type=click.Path(exists=True),
    help="Path to comparison.json from a compare run.",
)
@click.option(
    "--output",
    default="results/reports",
    type=click.Path(),
    help="Output directory for figures and summary.",
)
def report(comparison, output):
    """Generate charts and text summary from a comparison report."""
    setup_logging()
    out = generate_report(Path(comparison), Path(output))
    click.echo(f"Figures saved to: {out / 'figures'}")
    click.echo(f"Summary saved to: {out / 'summary.txt'}")


if __name__ == "__main__":
    cli()
