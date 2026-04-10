"""Pipeline orchestrator — wires dataset, OCR, LLM, and normalisation into a
single batch run with per-document disk output, resume logic, and robust JSON
parsing.
"""

from __future__ import annotations

import json
import logging
import re
import traceback
from datetime import datetime
from pathlib import Path

from .dataset_loader import DatasetLoader
from .llm import get_provider, LLMProvider
from .normalisation import normalise_extraction
from .ocr.tesseract import TesseractOCR
from .performance import Timer, estimate_cost
from .schema import BillExtraction, DocumentEntry, PipelineResult
from .utils import (
    copy_file,
    load_prompt_template,
    pdf_to_images,
    write_json,
    write_text,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Run-ID generation
# ---------------------------------------------------------------------------


def _generate_run_id(config: dict) -> str:
    """Create a human-readable, unique-ish run identifier."""
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    provider = config["llm"]["provider"]
    model = config["llm"]["model"].replace("-", "").replace(".", "")
    mode = config["pipeline"]["mode"]
    return f"{ts}_{provider}_{model}_{mode}"


# ---------------------------------------------------------------------------
# JSON parsing hardening
# ---------------------------------------------------------------------------

# Regex to match markdown-fenced JSON blocks (```json ... ```)
_FENCE_RE = re.compile(r"^```(?:json)?\s*\n?(.*?)\n?\s*```$", re.DOTALL)


def _parse_llm_json(raw: str) -> dict:
    """Parse LLM output to a dict, handling common wrapper patterns.

    Attempts in order:
      1. Direct ``json.loads``
      2. Strip markdown fences (```json ... ```)
      3. Extract substring from first ``{`` to last matching ``}``
      4. Raise ``ValueError`` with diagnostic excerpt
    """
    text = raw.strip()

    # 1. Direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # 2. Markdown fence strip
    m = _FENCE_RE.search(text)
    if m:
        try:
            return json.loads(m.group(1).strip())
        except json.JSONDecodeError:
            pass

    # 3. Brace extraction — find first { and matching }
    start = text.find("{")
    if start != -1:
        depth = 0
        end = -1
        for i in range(start, len(text)):
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
                if depth == 0:
                    end = i
                    break
        if end != -1:
            try:
                return json.loads(text[start : end + 1])
            except json.JSONDecodeError:
                pass

    # 4. Failure
    excerpt = text[:500]
    raise ValueError(
        f"Could not parse LLM output as JSON. First 500 chars:\n{excerpt}"
    )


# ---------------------------------------------------------------------------
# Single-document processing
# ---------------------------------------------------------------------------


def _process_document(
    doc: DocumentEntry,
    config: dict,
    provider: LLMProvider,
    prompt_template: str,
    ocr_engine: TesseractOCR | None,
    doc_output_dir: Path,
) -> PipelineResult:
    """Run the full extraction pipeline for a single document."""

    mode = config["pipeline"]["mode"]
    schema_desc = BillExtraction.schema_description()
    ocr_text: str | None = None

    # --- Timed pipeline stages ---
    with Timer() as t_total:
        # Stage 1: Convert PDF pages to PIL images
        with Timer() as t_pdf:
            images = pdf_to_images(doc.pdf_path)

        # Stage 2: Render the prompt (instructions only — data goes in the user message)
        rendered_prompt = prompt_template.format(schema_description=schema_desc)

        # Stage 3: OCR-text path vs vision path
        if mode == "ocr_text":
            # OCR path: run Tesseract on each page, concatenate text, send to LLM
            with Timer() as t_ocr:
                ocr_texts = [
                    ocr_engine.extract_text(img, doc.language) for img in images
                ]
                ocr_text = "\n\n".join(ocr_texts)

            with Timer() as t_llm:
                result = provider.extract_from_text(ocr_text, rendered_prompt)
        else:
            # Vision path: skip OCR, send page images directly to the LLM
            t_ocr = Timer()  # 0 ms placeholder
            vision_images = images[:2]  # locked baseline: first 2 pages only

            with Timer() as t_llm:
                result = provider.extract_from_image(vision_images, rendered_prompt)

        # Stage 4: Parse raw LLM JSON → normalise → validate via Pydantic
        with Timer() as t_parse:
            fields = _parse_llm_json(result["raw_output"])
            normalised = normalise_extraction(fields)
            extraction = BillExtraction(**normalised)

    # Build timings
    timings = {
        "total_ms": round(t_total.elapsed_ms, 1),
        "pdf_to_images_ms": round(t_pdf.elapsed_ms, 1),
        "ocr_ms": round(t_ocr.elapsed_ms, 1),
        "llm_call_ms": round(t_llm.elapsed_ms, 1),
        "parse_normalise_ms": round(t_parse.elapsed_ms, 1),
    }

    token_usage = result.get("token_usage", {})
    model_id = provider.get_model_id()

    # Cost estimation
    cost = estimate_cost(
        provider=config["llm"]["provider"],
        model=config["llm"]["model"],
        input_tokens=token_usage.get("input_tokens", 0),
        output_tokens=token_usage.get("output_tokens", 0),
    )

    pipeline_result = PipelineResult(
        document_id=doc.document_id,
        extraction=extraction,
        raw_llm_output=result["raw_output"],
        ocr_text=ocr_text,
        timings=timings,
        token_usage=token_usage,
        model_id=model_id,
        pipeline_mode=mode,
    )

    # ---- Persist each artefact to disk for later evaluation/diagnosis ----
    doc_output_dir.mkdir(parents=True, exist_ok=True)

    write_json(
        doc_output_dir / "extraction.json",      # normalised 12-field output
        extraction.model_dump(mode="json"),
    )
    write_text(doc_output_dir / "raw_llm_output.txt", result["raw_output"])

    if ocr_text is not None:
        write_text(doc_output_dir / "ocr_text.txt", ocr_text)  # for diagnosis later

    write_json(doc_output_dir / "timings.json", timings)

    metadata = {
        "document_id": doc.document_id,
        "language": doc.language,
        "utility_type": doc.utility_type,
        # Billing company from manifest (not the LLM provider).
        "provider_name": doc.provider,
        "llm_provider": config["llm"]["provider"],
        "llm_model": config["llm"]["model"],
        "model_id": model_id,
        "pipeline_mode": mode,
        "estimated_cost_usd": cost,
        "timestamp": datetime.now().isoformat(),
    }
    write_json(doc_output_dir / "metadata.json", metadata)

    return pipeline_result


# ---------------------------------------------------------------------------
# Batch orchestration
# ---------------------------------------------------------------------------


def run_pipeline(config: dict, force: bool = False) -> Path:
    """Execute the extraction pipeline for every document in the manifest.

    Args:
        config: Fully-resolved pipeline config dict.
        force:  If *True*, re-process documents even when a previous result
                exists on disk.

    Returns:
        Path to the run directory containing all outputs.
    """
    # 1. Resolve paths
    manifest_path = Path(config["data"]["manifest"])
    bills_dir = Path(config["data"]["bills_dir"])
    gt_dir = Path(config["data"]["ground_truth_dir"])
    results_dir = Path(config["output"]["results_dir"])
    prompt_file = Path(config["llm"]["prompt_file"])
    mode = config["pipeline"]["mode"]

    # 2. Load dataset
    loader = DatasetLoader(manifest_path, bills_dir, gt_dir)
    documents = loader.load_and_validate()
    logger.info("Loaded %d documents from manifest", len(documents))

    # 3. Instantiate provider & prompt
    provider = get_provider(config)
    prompt_template = load_prompt_template(prompt_file)

    # 4. OCR engine (only for ocr_text mode)
    ocr_engine = TesseractOCR() if mode == "ocr_text" else None

    # 5. Create run directory and snapshot inputs for reproducibility
    run_id = _generate_run_id(config)
    run_dir = results_dir / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    # Freeze the exact config, manifest, and prompt used for this run
    import yaml

    write_text(run_dir / "config.yaml", yaml.dump(config, default_flow_style=False))
    copy_file(manifest_path, run_dir / "manifest_snapshot.csv")
    copy_file(prompt_file, run_dir / "prompt.txt")

    logger.info("Run ID: %s", run_id)
    logger.info("Output directory: %s", run_dir)

    # 6. Process each document
    processed = 0
    skipped = 0
    failed = 0

    for doc in documents:
        doc_dir = run_dir / "documents" / doc.document_id

        # Resume logic: skip documents that already have results (unless --force)
        if (doc_dir / "extraction.json").exists() and not force:
            logger.info("Skipping %s (already processed)", doc.document_id)
            skipped += 1
            continue

        try:
            _process_document(
                doc, config, provider, prompt_template, ocr_engine, doc_dir
            )
            processed += 1
            logger.info("OK  %s", doc.document_id)
        except Exception as exc:
            failed += 1
            logger.error("FAIL %s: %s", doc.document_id, exc)
            doc_dir.mkdir(parents=True, exist_ok=True)
            write_json(
                doc_dir / "error.json",
                {"error": str(exc), "traceback": traceback.format_exc()},
            )

    # 7. Write run summary
    summary = {
        "run_id": run_id,
        "provider": config["llm"]["provider"],
        "model": config["llm"]["model"],
        "pipeline_mode": mode,
        "total_documents": len(documents),
        "processed": processed,
        "skipped": skipped,
        "failed": failed,
        "timestamp": datetime.now().isoformat(),
    }
    write_json(run_dir / "summary.json", summary)

    logger.info(
        "Run complete — processed: %d, skipped: %d, failed: %d",
        processed,
        skipped,
        failed,
    )
    return run_dir
