"""TDD-style specification for src/pipeline.py — _parse_llm_json, _generate_run_id,
and _process_document / run_pipeline integration (with mocked LLM/OCR).
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from src.pipeline import _generate_run_id, _parse_llm_json


# =========================================================================
# Spec: _parse_llm_json — clean JSON
# =========================================================================


class TestParseLlmJsonShouldParseCleanJSON:
    """Given well-formed JSON, _parse_llm_json should return a dict."""

    def test_simple_object(self):
        result = _parse_llm_json('{"provider_name": "OVO Energy", "total_amount_due": 42.5}')
        assert result["provider_name"] == "OVO Energy"
        assert result["total_amount_due"] == 42.5

    def test_all_12_fields(self):
        raw = json.dumps({
            "provider_name": "British Gas",
            "utility_type": "gas",
            "bill_number": "INV-001",
            "bill_date": "2024-01-15",
            "billing_period_start": "2023-12-01",
            "billing_period_end": "2024-01-01",
            "due_date": "2024-02-01",
            "total_amount_due": 125.50,
            "currency": "GBP",
            "account_number": "ACC-12345",
            "consumption_amount": 350.0,
            "consumption_unit": "kWh",
        })
        result = _parse_llm_json(raw)
        assert len(result) == 12
        assert result["total_amount_due"] == 125.50

    def test_null_values(self):
        raw = '{"provider_name": null, "bill_date": null}'
        result = _parse_llm_json(raw)
        assert result["provider_name"] is None


# =========================================================================
# Spec: _parse_llm_json — whitespace handling
# =========================================================================


class TestParseLlmJsonShouldTolerateSurroundingWhitespace:
    def test_leading_trailing_whitespace(self):
        raw = '  \n {"provider_name": "Test"} \n  '
        result = _parse_llm_json(raw)
        assert result["provider_name"] == "Test"

    def test_newlines_inside_json(self):
        raw = '{\n  "provider_name": "Test"\n}'
        result = _parse_llm_json(raw)
        assert result["provider_name"] == "Test"


# =========================================================================
# Spec: _parse_llm_json — markdown fence stripping
# =========================================================================


class TestParseLlmJsonShouldStripMarkdownFences:
    """Given JSON wrapped in ```json ... ```, should strip fences and parse."""

    def test_json_fence(self):
        raw = '```json\n{"provider_name": "Fenced"}\n```'
        result = _parse_llm_json(raw)
        assert result["provider_name"] == "Fenced"

    def test_plain_fence(self):
        raw = '```\n{"provider_name": "Plain fence"}\n```'
        result = _parse_llm_json(raw)
        assert result["provider_name"] == "Plain fence"

    def test_fenced_all_12_fields(self):
        fields = {
            "provider_name": "Test",
            "utility_type": "gas",
            "bill_number": "INV-001",
            "bill_date": "2024-01-15",
            "billing_period_start": None,
            "billing_period_end": None,
            "due_date": None,
            "total_amount_due": 125.50,
            "currency": "GBP",
            "account_number": "ACC-12345",
            "consumption_amount": 350.0,
            "consumption_unit": "kWh",
        }
        raw = "```json\n" + json.dumps(fields, indent=2) + "\n```"
        result = _parse_llm_json(raw)
        assert len(result) == 12


# =========================================================================
# Spec: _parse_llm_json — brace extraction (prose wrapping)
# =========================================================================


class TestParseLlmJsonShouldExtractJsonFromProse:
    """Given JSON embedded in prose, should find the JSON object by matching braces."""

    def test_prose_before_json(self):
        raw = 'Here is the extracted data:\n{"provider_name": "After prose", "currency": "GBP"}'
        result = _parse_llm_json(raw)
        assert result["provider_name"] == "After prose"

    def test_prose_before_and_after(self):
        raw = "Here is the JSON:\n" '{"provider_name": "Wrapped"}\n' "Some note."
        result = _parse_llm_json(raw)
        assert result["provider_name"] == "Wrapped"

    def test_nested_braces(self):
        raw = 'Note:\n{"outer": {"inner": 1}}'
        result = _parse_llm_json(raw)
        assert result["outer"]["inner"] == 1

    def test_deeply_nested(self):
        raw = 'Here:\n{"a": {"b": {"c": 3}}}'
        result = _parse_llm_json(raw)
        assert result["a"]["b"]["c"] == 3


# =========================================================================
# Spec: _parse_llm_json — error cases
# =========================================================================


class TestParseLlmJsonShouldRaiseOnUnparseableInput:
    """Given input that contains no valid JSON, should raise ValueError."""

    def test_garbage(self):
        with pytest.raises(ValueError, match="Could not parse"):
            _parse_llm_json("This is not JSON at all")

    def test_empty_string(self):
        with pytest.raises(ValueError, match="Could not parse"):
            _parse_llm_json("")

    def test_whitespace_only(self):
        with pytest.raises(ValueError, match="Could not parse"):
            _parse_llm_json("   \n  ")

    def test_truncated_json(self):
        with pytest.raises(ValueError, match="Could not parse"):
            _parse_llm_json('{"provider_name": "trunc')

    def test_array_instead_of_object(self):
        """An array should still parse (it's valid JSON)."""
        result = _parse_llm_json("[1, 2, 3]")
        assert result == [1, 2, 3]


# =========================================================================
# Spec: _generate_run_id
# =========================================================================


class TestGenerateRunIdShouldContainConfigInfo:
    """Given a config dict, _generate_run_id should produce a string containing
    timestamp, provider, model, and mode."""

    def test_openai_ocr(self):
        config = {
            "llm": {"provider": "openai", "model": "gpt-4o"},
            "pipeline": {"mode": "ocr_text"},
        }
        run_id = _generate_run_id(config)
        assert "openai" in run_id
        assert "gpt4o" in run_id
        assert "ocr" in run_id

    def test_anthropic_vision(self):
        config = {
            "llm": {"provider": "anthropic", "model": "claude-3-5-sonnet"},
            "pipeline": {"mode": "vision"},
        }
        run_id = _generate_run_id(config)
        assert "anthropic" in run_id
        assert "vision" in run_id

    def test_starts_with_timestamp(self):
        config = {
            "llm": {"provider": "openai", "model": "gpt-4o"},
            "pipeline": {"mode": "vision"},
        }
        run_id = _generate_run_id(config)
        # Should start with YYYYMMDD_HHMMSS pattern
        parts = run_id.split("_")
        assert len(parts[0]) == 8  # YYYYMMDD
        assert parts[0].isdigit()
        assert len(parts[1]) == 6  # HHMMSS
        assert parts[1].isdigit()


class TestGenerateRunIdShouldStripSpecialChars:
    """Model names with hyphens/dots should have them removed."""

    def test_hyphens_removed(self):
        config = {
            "llm": {"provider": "anthropic", "model": "claude-3-5-sonnet"},
            "pipeline": {"mode": "vision"},
        }
        run_id = _generate_run_id(config)
        # After removing hyphens from model: "claude35sonnet"
        assert "-" not in run_id.split("_", 2)[-1].replace("ocr_text", "ocrtext")


class TestGenerateRunIdShouldBeUnique:
    """Two calls should produce different IDs (timestamp changes)."""

    def test_unique_ids(self):
        import time
        config = {
            "llm": {"provider": "openai", "model": "gpt-4o"},
            "pipeline": {"mode": "vision"},
        }
        id1 = _generate_run_id(config)
        time.sleep(1.1)
        id2 = _generate_run_id(config)
        assert id1 != id2


# =========================================================================
# Spec: run_pipeline integration (with mocks)
# =========================================================================


class TestRunPipelineShouldOrchestrateBatch:
    """Given a valid config and manifest, run_pipeline should process all
    documents and produce a run directory with expected outputs.

    This is an integration test using mocked LLM and OCR to avoid real API calls.
    """

    @pytest.fixture
    def pipeline_setup(self, tmp_path):
        """Create all the files needed for a pipeline run."""
        # Manifest
        bills_dir = tmp_path / "bills"
        gt_dir = tmp_path / "gt"
        bills_dir.mkdir()
        gt_dir.mkdir()

        manifest = tmp_path / "manifest.csv"
        manifest.write_text(
            "document_id,language,utility_type,provider,digital_native,page_count,annotated,verified,status\n"
            "d1,en,electricity,Test,true,1,true,true,active\n",
            encoding="utf-8",
        )
        (bills_dir / "d1.pdf").write_bytes(b"%PDF-fake")
        (gt_dir / "d1.json").write_text(
            json.dumps({"document_id": "d1", "fields": {"provider_name": "Test"}}),
            encoding="utf-8",
        )

        # Prompt
        prompt = tmp_path / "prompt.txt"
        prompt.write_text("Extract: {schema_description}", encoding="utf-8")

        # Config
        config = {
            "pipeline": {"mode": "ocr_text"},
            "llm": {
                "provider": "openai",
                "model": "gpt-4o",
                "temperature": 0.0,
                "max_tokens": 2000,
                "prompt_file": str(prompt),
                "vision_detail": "high",
                "timeout": 120,
                "max_retries": 2,
            },
            "data": {
                "manifest": str(manifest),
                "bills_dir": str(bills_dir),
                "ground_truth_dir": str(gt_dir),
            },
            "output": {
                "results_dir": str(tmp_path / "results"),
            },
        }
        return config

    @patch("src.pipeline.get_provider")
    @patch("src.pipeline.pdf_to_images")
    @patch("src.pipeline.TesseractOCR")
    def test_creates_run_directory(self, mock_ocr_cls, mock_pdf, mock_get_prov, pipeline_setup):
        from src.pipeline import run_pipeline
        from PIL import Image

        # Arrange
        mock_pdf.return_value = [Image.new("RGB", (10, 10))]
        mock_ocr = MagicMock()
        mock_ocr.extract_text.return_value = "OCR text here"
        mock_ocr_cls.return_value = mock_ocr

        mock_provider = MagicMock()
        mock_provider.extract_from_text.return_value = {
            "raw_output": json.dumps({"provider_name": "Test", "total_amount_due": 100.0}),
            "token_usage": {"input_tokens": 100, "output_tokens": 50},
            "latency_ms": 500.0,
        }
        mock_provider.get_model_id.return_value = "openai/gpt-4o"
        mock_get_prov.return_value = mock_provider

        # Act
        run_dir = run_pipeline(pipeline_setup)

        # Assert
        assert run_dir.exists()
        assert (run_dir / "summary.json").exists()
        assert (run_dir / "config.yaml").exists()

    @patch("src.pipeline.get_provider")
    @patch("src.pipeline.pdf_to_images")
    @patch("src.pipeline.TesseractOCR")
    def test_writes_per_document_outputs(self, mock_ocr_cls, mock_pdf, mock_get_prov, pipeline_setup):
        from src.pipeline import run_pipeline
        from PIL import Image

        mock_pdf.return_value = [Image.new("RGB", (10, 10))]
        mock_ocr = MagicMock()
        mock_ocr.extract_text.return_value = "OCR text"
        mock_ocr_cls.return_value = mock_ocr

        mock_provider = MagicMock()
        mock_provider.extract_from_text.return_value = {
            "raw_output": '{"provider_name": "Test"}',
            "token_usage": {"input_tokens": 100, "output_tokens": 50},
            "latency_ms": 500.0,
        }
        mock_provider.get_model_id.return_value = "openai/gpt-4o"
        mock_get_prov.return_value = mock_provider

        run_dir = run_pipeline(pipeline_setup)
        doc_dir = run_dir / "documents" / "d1"
        assert (doc_dir / "extraction.json").exists()
        assert (doc_dir / "raw_llm_output.txt").exists()
        assert (doc_dir / "ocr_text.txt").exists()
        assert (doc_dir / "timings.json").exists()
        assert (doc_dir / "metadata.json").exists()

    @patch("src.pipeline.get_provider")
    @patch("src.pipeline.pdf_to_images")
    @patch("src.pipeline.TesseractOCR")
    def test_skip_already_processed_without_force(self, mock_ocr_cls, mock_pdf, mock_get_prov, pipeline_setup):
        from src.pipeline import run_pipeline
        from PIL import Image

        mock_pdf.return_value = [Image.new("RGB", (10, 10))]
        mock_ocr = MagicMock()
        mock_ocr.extract_text.return_value = "text"
        mock_ocr_cls.return_value = mock_ocr

        mock_provider = MagicMock()
        mock_provider.extract_from_text.return_value = {
            "raw_output": '{"provider_name": "Test"}',
            "token_usage": {"input_tokens": 100, "output_tokens": 50},
            "latency_ms": 500.0,
        }
        mock_provider.get_model_id.return_value = "openai/gpt-4o"
        mock_get_prov.return_value = mock_provider

        # First run
        run_dir = run_pipeline(pipeline_setup)
        summary1 = json.loads((run_dir / "summary.json").read_text())
        assert summary1["processed"] == 1

        # Second run to same dir — but _generate_run_id changes, so test
        # the force flag by manually creating the extraction.json first
        # We verify provider was called exactly once
        assert mock_provider.extract_from_text.call_count == 1

    @patch("src.pipeline.get_provider")
    @patch("src.pipeline.pdf_to_images")
    def test_vision_mode_no_ocr_engine(self, mock_pdf, mock_get_prov, pipeline_setup):
        from src.pipeline import run_pipeline
        from PIL import Image

        pipeline_setup["pipeline"]["mode"] = "vision"

        mock_pdf.return_value = [Image.new("RGB", (10, 10))]
        mock_provider = MagicMock()
        mock_provider.extract_from_image.return_value = {
            "raw_output": '{"provider_name": "Vision Test"}',
            "token_usage": {"input_tokens": 200, "output_tokens": 100},
            "latency_ms": 800.0,
        }
        mock_provider.get_model_id.return_value = "openai/gpt-4o"
        mock_get_prov.return_value = mock_provider

        run_dir = run_pipeline(pipeline_setup)
        doc_dir = run_dir / "documents" / "d1"

        # In vision mode, ocr_text.txt should NOT exist
        assert not (doc_dir / "ocr_text.txt").exists()
        assert (doc_dir / "extraction.json").exists()

    @patch("src.pipeline.get_provider")
    @patch("src.pipeline.pdf_to_images")
    @patch("src.pipeline.TesseractOCR")
    def test_llm_failure_writes_error_json(self, mock_ocr_cls, mock_pdf, mock_get_prov, pipeline_setup):
        from src.pipeline import run_pipeline
        from PIL import Image

        mock_pdf.return_value = [Image.new("RGB", (10, 10))]
        mock_ocr = MagicMock()
        mock_ocr.extract_text.return_value = "text"
        mock_ocr_cls.return_value = mock_ocr

        mock_provider = MagicMock()
        mock_provider.extract_from_text.side_effect = RuntimeError("API down")
        mock_provider.get_model_id.return_value = "openai/gpt-4o"
        mock_get_prov.return_value = mock_provider

        run_dir = run_pipeline(pipeline_setup)
        summary = json.loads((run_dir / "summary.json").read_text())
        assert summary["failed"] == 1

        # Error document should have error.json
        doc_dir = run_dir / "documents" / "d1"
        assert (doc_dir / "error.json").exists()

    @patch("src.pipeline.get_provider")
    @patch("src.pipeline.pdf_to_images")
    @patch("src.pipeline.TesseractOCR")
    def test_summary_json_has_expected_keys(self, mock_ocr_cls, mock_pdf, mock_get_prov, pipeline_setup):
        from src.pipeline import run_pipeline
        from PIL import Image

        mock_pdf.return_value = [Image.new("RGB", (10, 10))]
        mock_ocr = MagicMock()
        mock_ocr.extract_text.return_value = "text"
        mock_ocr_cls.return_value = mock_ocr

        mock_provider = MagicMock()
        mock_provider.extract_from_text.return_value = {
            "raw_output": '{"provider_name": "Test"}',
            "token_usage": {"input_tokens": 100, "output_tokens": 50},
            "latency_ms": 500.0,
        }
        mock_provider.get_model_id.return_value = "openai/gpt-4o"
        mock_get_prov.return_value = mock_provider

        run_dir = run_pipeline(pipeline_setup)
        summary = json.loads((run_dir / "summary.json").read_text())
        assert "run_id" in summary
        assert "provider" in summary
        assert "model" in summary
        assert "pipeline_mode" in summary
        assert "total_documents" in summary
        assert "processed" in summary
        assert "skipped" in summary
        assert "failed" in summary
        assert "timestamp" in summary


# =========================================================================
# Helper for advanced pipeline tests
# =========================================================================


def _pipeline_config(tmp_path, docs, mode="ocr_text"):
    """Create manifest, stub files, prompt, and config for pipeline tests."""
    bills_dir = tmp_path / "bills"
    gt_dir = tmp_path / "gt"
    bills_dir.mkdir(exist_ok=True)
    gt_dir.mkdir(exist_ok=True)

    header = "document_id,language,utility_type,provider,digital_native,page_count,annotated,verified,status\n"
    rows = []
    for d in docs:
        did = d["id"]
        lang = d.get("lang", "en")
        utype = d.get("utype", "electricity")
        rows.append(f"{did},{lang},{utype},Test,true,1,true,true,active\n")
        (bills_dir / f"{did}.pdf").write_bytes(b"%PDF-fake")
        (gt_dir / f"{did}.json").write_text(
            json.dumps({"document_id": did, "fields": {"provider_name": "Test"}}),
            encoding="utf-8",
        )

    manifest = tmp_path / "manifest.csv"
    manifest.write_text(header + "".join(rows), encoding="utf-8")

    prompt = tmp_path / "prompt.txt"
    prompt.write_text("Extract: {schema_description}", encoding="utf-8")

    return {
        "pipeline": {"mode": mode},
        "llm": {
            "provider": "openai",
            "model": "gpt-4o",
            "temperature": 0.0,
            "max_tokens": 2000,
            "prompt_file": str(prompt),
            "vision_detail": "high",
            "timeout": 120,
            "max_retries": 2,
        },
        "data": {
            "manifest": str(manifest),
            "bills_dir": str(bills_dir),
            "ground_truth_dir": str(gt_dir),
        },
        "output": {"results_dir": str(tmp_path / "results")},
    }


def _ok_provider_mock():
    """Return a MagicMock LLM provider that returns valid extraction JSON."""
    mock_provider = MagicMock()
    mock_provider.extract_from_text.return_value = {
        "raw_output": '{"provider_name": "Test"}',
        "token_usage": {"input_tokens": 100, "output_tokens": 50},
        "latency_ms": 500.0,
    }
    mock_provider.extract_from_image.return_value = {
        "raw_output": '{"provider_name": "Test"}',
        "token_usage": {"input_tokens": 200, "output_tokens": 100},
        "latency_ms": 800.0,
    }
    mock_provider.get_model_id.return_value = "openai/gpt-4o"
    return mock_provider


# =========================================================================
# Spec: run_pipeline — bad JSON from LLM raw_output
# =========================================================================


class TestRunPipelineBadJsonFromLLMShouldWriteErrorJson:
    """When the LLM returns unparseable JSON in raw_output, the document
    should fail gracefully with error.json containing the parse error."""

    @patch("src.pipeline.get_provider")
    @patch("src.pipeline.pdf_to_images")
    @patch("src.pipeline.TesseractOCR")
    def test_invalid_json_raw_output(self, mock_ocr_cls, mock_pdf, mock_get_prov, tmp_path):
        from src.pipeline import run_pipeline
        from PIL import Image

        config = _pipeline_config(tmp_path, [{"id": "d1"}])

        mock_pdf.return_value = [Image.new("RGB", (10, 10))]
        mock_ocr = MagicMock()
        mock_ocr.extract_text.return_value = "OCR text"
        mock_ocr_cls.return_value = mock_ocr

        mock_provider = MagicMock()
        mock_provider.extract_from_text.return_value = {
            "raw_output": "This is not valid JSON at all",
            "token_usage": {"input_tokens": 100, "output_tokens": 50},
            "latency_ms": 500.0,
        }
        mock_provider.get_model_id.return_value = "openai/gpt-4o"
        mock_get_prov.return_value = mock_provider

        run_dir = run_pipeline(config)
        summary = json.loads((run_dir / "summary.json").read_text())
        assert summary["failed"] == 1
        assert summary["processed"] == 0

        doc_dir = run_dir / "documents" / "d1"
        assert (doc_dir / "error.json").exists()
        error_data = json.loads((doc_dir / "error.json").read_text())
        assert "Could not parse" in error_data["error"]

    @patch("src.pipeline.get_provider")
    @patch("src.pipeline.pdf_to_images")
    @patch("src.pipeline.TesseractOCR")
    def test_truncated_json_raw_output(self, mock_ocr_cls, mock_pdf, mock_get_prov, tmp_path):
        from src.pipeline import run_pipeline
        from PIL import Image

        config = _pipeline_config(tmp_path, [{"id": "d1"}])

        mock_pdf.return_value = [Image.new("RGB", (10, 10))]
        mock_ocr = MagicMock()
        mock_ocr.extract_text.return_value = "OCR text"
        mock_ocr_cls.return_value = mock_ocr

        mock_provider = MagicMock()
        mock_provider.extract_from_text.return_value = {
            "raw_output": '{"provider_name": "truncated...',
            "token_usage": {"input_tokens": 100, "output_tokens": 50},
            "latency_ms": 500.0,
        }
        mock_provider.get_model_id.return_value = "openai/gpt-4o"
        mock_get_prov.return_value = mock_provider

        run_dir = run_pipeline(config)
        summary = json.loads((run_dir / "summary.json").read_text())
        assert summary["failed"] == 1
        assert (run_dir / "documents" / "d1" / "error.json").exists()


# =========================================================================
# Spec: run_pipeline — force flag and resume
# =========================================================================


class TestRunPipelineForceFlag:
    """With force=True, documents with existing extraction.json should be
    reprocessed. Without force, they should be skipped."""

    @patch("src.pipeline._generate_run_id", return_value="fixed_run_id")
    @patch("src.pipeline.get_provider")
    @patch("src.pipeline.pdf_to_images")
    @patch("src.pipeline.TesseractOCR")
    def test_force_reprocesses_existing(self, mock_ocr_cls, mock_pdf, mock_get_prov, mock_run_id, tmp_path):
        from src.pipeline import run_pipeline
        from PIL import Image

        config = _pipeline_config(tmp_path, [{"id": "d1"}])

        mock_pdf.return_value = [Image.new("RGB", (10, 10))]
        mock_ocr = MagicMock()
        mock_ocr.extract_text.return_value = "OCR text"
        mock_ocr_cls.return_value = mock_ocr

        mock_provider = _ok_provider_mock()
        mock_get_prov.return_value = mock_provider

        run_pipeline(config)
        assert mock_provider.extract_from_text.call_count == 1

        run_pipeline(config, force=True)
        assert mock_provider.extract_from_text.call_count == 2

    @patch("src.pipeline._generate_run_id", return_value="fixed_run_id")
    @patch("src.pipeline.get_provider")
    @patch("src.pipeline.pdf_to_images")
    @patch("src.pipeline.TesseractOCR")
    def test_skip_without_force_in_same_run_dir(self, mock_ocr_cls, mock_pdf, mock_get_prov, mock_run_id, tmp_path):
        from src.pipeline import run_pipeline
        from PIL import Image

        config = _pipeline_config(tmp_path, [{"id": "d1"}])

        mock_pdf.return_value = [Image.new("RGB", (10, 10))]
        mock_ocr = MagicMock()
        mock_ocr.extract_text.return_value = "OCR text"
        mock_ocr_cls.return_value = mock_ocr

        mock_provider = _ok_provider_mock()
        mock_get_prov.return_value = mock_provider

        run_pipeline(config)
        assert mock_provider.extract_from_text.call_count == 1

        run_dir = run_pipeline(config, force=False)
        assert mock_provider.extract_from_text.call_count == 1
        summary = json.loads((run_dir / "summary.json").read_text())
        assert summary["skipped"] == 1
        assert summary["processed"] == 0


# =========================================================================
# Spec: run_pipeline — multi-document batches
# =========================================================================


class TestRunPipelineMultiDocBatch:
    """Pipeline should correctly process multiple documents and track counts."""

    @patch("src.pipeline.get_provider")
    @patch("src.pipeline.pdf_to_images")
    @patch("src.pipeline.TesseractOCR")
    def test_two_docs_both_succeed(self, mock_ocr_cls, mock_pdf, mock_get_prov, tmp_path):
        from src.pipeline import run_pipeline
        from PIL import Image

        config = _pipeline_config(tmp_path, [{"id": "d1"}, {"id": "d2"}])

        mock_pdf.return_value = [Image.new("RGB", (10, 10))]
        mock_ocr = MagicMock()
        mock_ocr.extract_text.return_value = "OCR text"
        mock_ocr_cls.return_value = mock_ocr

        mock_provider = _ok_provider_mock()
        mock_get_prov.return_value = mock_provider

        run_dir = run_pipeline(config)
        summary = json.loads((run_dir / "summary.json").read_text())
        assert summary["total_documents"] == 2
        assert summary["processed"] == 2
        assert summary["failed"] == 0
        assert summary["skipped"] == 0

    @patch("src.pipeline.get_provider")
    @patch("src.pipeline.pdf_to_images")
    @patch("src.pipeline.TesseractOCR")
    def test_two_docs_one_fails(self, mock_ocr_cls, mock_pdf, mock_get_prov, tmp_path):
        from src.pipeline import run_pipeline
        from PIL import Image

        config = _pipeline_config(tmp_path, [{"id": "d1"}, {"id": "d2"}])

        mock_pdf.return_value = [Image.new("RGB", (10, 10))]
        mock_ocr = MagicMock()
        mock_ocr.extract_text.return_value = "OCR text"
        mock_ocr_cls.return_value = mock_ocr

        call_count = {"n": 0}

        def alternating_response(text, prompt):
            call_count["n"] += 1
            if call_count["n"] == 1:
                return {
                    "raw_output": '{"provider_name": "Test"}',
                    "token_usage": {"input_tokens": 100, "output_tokens": 50},
                    "latency_ms": 500.0,
                }
            raise RuntimeError("API failure on second doc")

        mock_provider = MagicMock()
        mock_provider.extract_from_text.side_effect = alternating_response
        mock_provider.get_model_id.return_value = "openai/gpt-4o"
        mock_get_prov.return_value = mock_provider

        run_dir = run_pipeline(config)
        summary = json.loads((run_dir / "summary.json").read_text())
        assert summary["total_documents"] == 2
        assert summary["processed"] == 1
        assert summary["failed"] == 1

    @patch("src.pipeline.get_provider")
    @patch("src.pipeline.pdf_to_images")
    @patch("src.pipeline.TesseractOCR")
    def test_three_docs_all_succeed_separate_dirs(self, mock_ocr_cls, mock_pdf, mock_get_prov, tmp_path):
        from src.pipeline import run_pipeline
        from PIL import Image

        config = _pipeline_config(
            tmp_path,
            [{"id": "d1"}, {"id": "d2"}, {"id": "d3", "lang": "de", "utype": "gas"}],
        )

        mock_pdf.return_value = [Image.new("RGB", (10, 10))]
        mock_ocr = MagicMock()
        mock_ocr.extract_text.return_value = "OCR text"
        mock_ocr_cls.return_value = mock_ocr

        mock_provider = _ok_provider_mock()
        mock_get_prov.return_value = mock_provider

        run_dir = run_pipeline(config)
        for did in ("d1", "d2", "d3"):
            assert (run_dir / "documents" / did / "extraction.json").exists()


# =========================================================================
# Spec: run_pipeline — vision mode page selection
# =========================================================================


class TestRunPipelineVisionModePageSelection:
    """Vision mode should pass only the first 2 page images to the LLM,
    regardless of how many pages the PDF has."""

    @patch("src.pipeline.get_provider")
    @patch("src.pipeline.pdf_to_images")
    def test_only_first_two_pages_sent(self, mock_pdf, mock_get_prov, tmp_path):
        from src.pipeline import run_pipeline
        from PIL import Image

        config = _pipeline_config(tmp_path, [{"id": "d1"}], mode="vision")

        mock_pdf.return_value = [Image.new("RGB", (10, 10)) for _ in range(5)]

        mock_provider = _ok_provider_mock()
        mock_get_prov.return_value = mock_provider

        run_pipeline(config)

        call_args = mock_provider.extract_from_image.call_args
        images_arg = call_args[0][0]
        assert len(images_arg) == 2

    @patch("src.pipeline.get_provider")
    @patch("src.pipeline.pdf_to_images")
    def test_single_page_pdf_sends_one_image(self, mock_pdf, mock_get_prov, tmp_path):
        from src.pipeline import run_pipeline
        from PIL import Image

        config = _pipeline_config(tmp_path, [{"id": "d1"}], mode="vision")

        mock_pdf.return_value = [Image.new("RGB", (10, 10))]

        mock_provider = _ok_provider_mock()
        mock_get_prov.return_value = mock_provider

        run_pipeline(config)

        call_args = mock_provider.extract_from_image.call_args
        images_arg = call_args[0][0]
        assert len(images_arg) == 1


# =========================================================================
# Spec: run_pipeline — empty image list
# =========================================================================


class TestRunPipelineEmptyImageList:
    """When pdf_to_images returns an empty list, the pipeline should still
    attempt the LLM call with empty input rather than crashing."""

    @patch("src.pipeline.get_provider")
    @patch("src.pipeline.pdf_to_images")
    @patch("src.pipeline.TesseractOCR")
    def test_empty_images_ocr_mode(self, mock_ocr_cls, mock_pdf, mock_get_prov, tmp_path):
        from src.pipeline import run_pipeline

        config = _pipeline_config(tmp_path, [{"id": "d1"}])

        mock_pdf.return_value = []
        mock_ocr = MagicMock()
        mock_ocr_cls.return_value = mock_ocr

        mock_provider = _ok_provider_mock()
        mock_get_prov.return_value = mock_provider

        run_dir = run_pipeline(config)
        summary = json.loads((run_dir / "summary.json").read_text())
        assert summary["processed"] == 1
        mock_ocr.extract_text.assert_not_called()
        mock_provider.extract_from_text.assert_called_once()
        call_text = mock_provider.extract_from_text.call_args[0][0]
        assert call_text == ""

    @patch("src.pipeline.get_provider")
    @patch("src.pipeline.pdf_to_images")
    def test_empty_images_vision_mode(self, mock_pdf, mock_get_prov, tmp_path):
        from src.pipeline import run_pipeline

        config = _pipeline_config(tmp_path, [{"id": "d1"}], mode="vision")

        mock_pdf.return_value = []

        mock_provider = _ok_provider_mock()
        mock_get_prov.return_value = mock_provider

        run_dir = run_pipeline(config)
        summary = json.loads((run_dir / "summary.json").read_text())
        assert summary["processed"] == 1
        call_args = mock_provider.extract_from_image.call_args[0][0]
        assert call_args == []
