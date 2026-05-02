from __future__ import annotations

import argparse
import csv
import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class BatchRun:
    batch_index: int
    run_dir: Path
    doc_ids: list[str]


def _read_manifest_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    if not rows:
        raise ValueError(f"Manifest appears empty: {path}")
    return rows


def _write_manifest_rows(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _is_truthy(v: str | None) -> bool:
    return (v or "").strip().lower() in {"true", "1", "yes", "y"}


def _runnable_doc_ids(rows: list[dict[str, str]]) -> list[str]:
    runnable: list[str] = []
    for r in rows:
        status = (r.get("status") or "").strip().lower()
        if status != "active":
            continue
        if not _is_truthy(r.get("annotated")):
            continue
        if not _is_truthy(r.get("verified")):
            continue
        runnable.append((r.get("document_id") or "").strip())
    runnable = [d for d in runnable if d]
    if len(set(runnable)) != len(runnable):
        raise ValueError("Duplicate document_id detected in runnable set.")
    return runnable


def _split_batches(doc_ids: list[str], batch_size: int) -> list[list[str]]:
    if batch_size <= 0:
        raise ValueError("batch_size must be > 0")
    return [doc_ids[i : i + batch_size] for i in range(0, len(doc_ids), batch_size)]


def _set_active_status(rows: list[dict[str, str]], active_ids: set[str]) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    for r in rows:
        rr = dict(r)
        doc_id = (rr.get("document_id") or "").strip()
        if doc_id and doc_id in active_ids:
            rr["status"] = "active"
        elif doc_id:
            rr["status"] = "excluded"
        out.append(rr)
    return out


def _run_cli_run(config_path: Path, cwd: Path) -> Path:
    cmd = [sys.executable, "cli.py", "run", "--config", str(config_path)]
    proc = subprocess.run(cmd, cwd=str(cwd), text=True, capture_output=True)
    if proc.returncode != 0:
        raise RuntimeError(
            "cli.py run failed.\n"
            f"Command: {' '.join(cmd)}\n"
            f"Exit: {proc.returncode}\n"
            f"STDOUT:\n{proc.stdout}\n"
            f"STDERR:\n{proc.stderr}\n"
        )

    # Parse: "Run complete. Results saved to: <path>"
    marker = "Run complete. Results saved to:"
    for line in (proc.stdout or "").splitlines():
        if marker in line:
            run_dir = line.split(marker, 1)[1].strip()
            if run_dir:
                return Path(run_dir)
    raise RuntimeError(
        "Could not locate run_dir in cli output.\n"
        f"STDOUT:\n{proc.stdout}\n"
        f"STDERR:\n{proc.stderr}\n"
    )


def _read_summary(run_dir: Path) -> dict:
    p = run_dir / "summary.json"
    if not p.exists():
        raise FileNotFoundError(f"Missing summary.json: {p}")
    return json.loads(p.read_text(encoding="utf-8"))


def _verify_batch(run_dir: Path, expected_doc_ids: list[str]) -> None:
    summary = _read_summary(run_dir)
    failed = int(summary.get("failed", 0))
    if failed != 0:
        raise RuntimeError(f"Batch run has failed documents (failed={failed}). See {run_dir}")

    docs_dir = run_dir / "documents"
    missing: list[str] = []
    for doc_id in expected_doc_ids:
        p = docs_dir / doc_id / "extraction.json"
        if not p.exists():
            missing.append(doc_id)
    if missing:
        raise RuntimeError(f"Missing extraction.json for {len(missing)} docs: {missing}")


def _copy_doc_dir(src_doc_dir: Path, dst_docs_dir: Path) -> None:
    dst = dst_docs_dir / src_doc_dir.name
    if dst.exists():
        raise FileExistsError(f"Destination already exists (collision?): {dst}")
    shutil.copytree(src_doc_dir, dst)


def _consolidate_runs(target_run_dir: Path, other_run_dirs: list[Path]) -> None:
    dst_docs_dir = target_run_dir / "documents"
    dst_docs_dir.mkdir(parents=True, exist_ok=True)

    for rd in other_run_dirs:
        src_docs_dir = rd / "documents"
        if not src_docs_dir.exists():
            raise FileNotFoundError(f"Missing documents dir: {src_docs_dir}")
        for doc_dir in sorted(src_docs_dir.iterdir()):
            if not doc_dir.is_dir():
                continue
            _copy_doc_dir(doc_dir, dst_docs_dir)


def _rewrite_consolidated_summary(
    run_dir: Path,
    provider: str | None = None,
    model: str | None = None,
    pipeline_mode: str | None = None,
) -> None:
    """Rewrite summary.json to reflect the consolidated run contents.

    Batch runs write summary.json for only that batch. After consolidation, the
    run_dir contains many more document directories; this rewrites counts by
    scanning run_dir/documents/* and counting error.json presence.
    """
    docs_dir = run_dir / "documents"
    if not docs_dir.exists():
        raise FileNotFoundError(f"Missing documents dir: {docs_dir}")

    doc_dirs = [p for p in docs_dir.iterdir() if p.is_dir()]
    total_documents = len(doc_dirs)
    failed = 0
    for d in doc_dirs:
        if (d / "error.json").exists():
            failed += 1

    processed = total_documents - failed
    skipped = 0  # consolidation implies we're counting what's present on disk

    summary_path = run_dir / "summary.json"
    summary = _read_summary(run_dir) if summary_path.exists() else {}
    summary["total_documents"] = total_documents
    summary["processed"] = processed
    summary["skipped"] = skipped
    summary["failed"] = failed
    if provider is not None:
        summary["provider"] = provider
    if model is not None:
        summary["model"] = model
    if pipeline_mode is not None:
        summary["pipeline_mode"] = pipeline_mode

    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def _refresh_manifest_snapshot(run_dir: Path, restored_manifest_path: Path) -> None:
    """Overwrite manifest_snapshot.csv so the consolidated run reflects full manifest."""
    dst = run_dir / "manifest_snapshot.csv"
    if restored_manifest_path.exists():
        shutil.copy2(restored_manifest_path, dst)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Run extraction in 10-doc batches by flipping manifest status, "
            "then consolidate batch run outputs into the first run directory."
        )
    )
    parser.add_argument(
        "--config",
        default="config/default.yaml",
        help="Path to YAML config file (default: config/default.yaml).",
    )
    parser.add_argument(
        "--manifest",
        default="data/dataset_manifest.csv",
        help="Path to dataset manifest CSV (default: data/dataset_manifest.csv).",
    )
    parser.add_argument("--batch-size", type=int, default=10, help="Docs per batch (default: 10).")
    parser.add_argument(
        "--batches",
        type=int,
        default=None,
        help="Optional: run only the first N batches (for smoke testing).",
    )
    args = parser.parse_args()

    config_path = (REPO_ROOT / args.config).resolve()
    manifest_path = (REPO_ROOT / args.manifest).resolve()

    if not config_path.exists():
        raise FileNotFoundError(f"Config not found: {config_path}")
    if not manifest_path.exists():
        raise FileNotFoundError(f"Manifest not found: {manifest_path}")

    # Backup manifest for restore, even if we crash.
    backup_path = manifest_path.with_suffix(manifest_path.suffix + ".bak")
    if backup_path.exists():
        raise FileExistsError(f"Refusing to overwrite existing backup: {backup_path}")
    shutil.copy2(manifest_path, backup_path)

    try:
        rows = _read_manifest_rows(manifest_path)
        fieldnames = list(rows[0].keys())
        if "document_id" not in fieldnames or "status" not in fieldnames:
            raise ValueError("Manifest missing required columns document_id/status.")

        runnable_ids = _runnable_doc_ids(rows)
        if len(runnable_ids) == 0:
            raise ValueError("No runnable docs found (status=active + annotated + verified).")

        # Deterministic order: keep manifest order as-is.
        batches = _split_batches(runnable_ids, args.batch_size)
        if args.batches is not None:
            batches = batches[: args.batches]

        print(f"Runnable docs: {len(runnable_ids)}", flush=True)
        print(f"Batches: {len(batches)} (batch_size={args.batch_size})", flush=True)

        batch_runs: list[BatchRun] = []

        for i, batch_ids in enumerate(batches, start=1):
            print(f"\n=== Batch {i}/{len(batches)} ({len(batch_ids)} docs) ===", flush=True)

            updated_rows = _set_active_status(rows, set(batch_ids))
            _write_manifest_rows(manifest_path, updated_rows, fieldnames)

            run_dir = _run_cli_run(config_path, cwd=REPO_ROOT)
            run_dir = (REPO_ROOT / run_dir).resolve() if not run_dir.is_absolute() else run_dir
            print(f"Run dir: {run_dir}", flush=True)

            _verify_batch(run_dir, batch_ids)
            batch_runs.append(BatchRun(batch_index=i, run_dir=run_dir, doc_ids=batch_ids))
            print("Batch verified OK.", flush=True)

        if not batch_runs:
            print("No batches executed.", flush=True)
            return 0

        # Consolidate: copy docs from batch 2..N into batch 1 run dir.
        target = batch_runs[0].run_dir
        others = [br.run_dir for br in batch_runs[1:]]
        if others:
            print(f"\nConsolidating {len(others)} batch runs into: {target}", flush=True)
            _consolidate_runs(target, others)
            print("Consolidation complete.", flush=True)
        else:
            print("\nOnly one batch executed; no consolidation needed.", flush=True)

        # Rewrite summary.json so it reflects consolidated document count.
        # Provider/model/mode are read from the config used for this script invocation.
        # (cli.py run snapshots config.yaml separately inside run_dir.)
        try:
            import yaml

            cfg = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
            _rewrite_consolidated_summary(
                target,
                provider=((cfg.get("llm") or {}).get("provider")),
                model=((cfg.get("llm") or {}).get("model")),
                pipeline_mode=((cfg.get("pipeline") or {}).get("mode")),
            )
        except Exception as exc:
            raise RuntimeError(f"Failed to rewrite consolidated summary.json in {target}: {exc}") from exc

        print(f"\nCONSOLIDATED_RUN_DIR={target}", flush=True)
        return 0
    finally:
        # Always try to restore the original manifest.
        # If the backup was deleted or moved, leave the current manifest as-is.
        if backup_path.exists():
            shutil.copy2(backup_path, manifest_path)
            os.remove(backup_path)

            # After restoring, refresh manifest_snapshot.csv so consolidated run points at
            # the full original manifest rather than the last batch subset.
            # This is best-effort (only if we executed at least one batch).
            try:
                # batch_runs is defined in the try-block; may not exist if we failed early.
                target_run_dir = locals().get("batch_runs", [None])[0]
                if target_run_dir and getattr(target_run_dir, "run_dir", None):
                    _refresh_manifest_snapshot(target_run_dir.run_dir, manifest_path)
            except Exception:
                pass


if __name__ == "__main__":
    raise SystemExit(main())

