"""TDD-style specification for cli.py — Click CLI commands.

Uses Click's CliRunner for isolated testing without real API calls or file I/O.
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
from click.testing import CliRunner

from cli import cli


@pytest.fixture
def runner():
    return CliRunner()


# =========================================================================
# Spec: CLI group
# =========================================================================


class TestCliGroupShouldShowHelp:
    """The top-level CLI group should display help text."""

    def test_help_flag(self, runner):
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "OCR vs Non-OCR" in result.output

    def test_no_args_shows_usage(self, runner):
        result = runner.invoke(cli, [])
        # Click groups show usage/help; exit code may be 0 or 2
        assert "Usage" in result.output or "OCR vs Non-OCR" in result.output


class TestCliGroupShouldHaveAllCommands:
    """The CLI should expose run, evaluate, compare, and report commands."""

    def test_run_in_help(self, runner):
        result = runner.invoke(cli, ["--help"])
        assert "run" in result.output

    def test_evaluate_in_help(self, runner):
        result = runner.invoke(cli, ["--help"])
        assert "evaluate" in result.output

    def test_compare_in_help(self, runner):
        result = runner.invoke(cli, ["--help"])
        assert "compare" in result.output

    def test_report_in_help(self, runner):
        result = runner.invoke(cli, ["--help"])
        assert "report" in result.output


# =========================================================================
# Spec: run command
# =========================================================================


class TestRunCommandShouldRequireConfig:
    """The run command should require --config."""

    def test_missing_config_exits_with_error(self, runner):
        result = runner.invoke(cli, ["run"])
        assert result.exit_code != 0
        assert "config" in result.output.lower() or "missing" in result.output.lower() or "required" in result.output.lower()


class TestRunCommandShouldShowHelp:
    def test_help_flag(self, runner):
        result = runner.invoke(cli, ["run", "--help"])
        assert result.exit_code == 0
        assert "--config" in result.output
        assert "--mode" in result.output
        assert "--provider" in result.output
        assert "--model" in result.output
        assert "--force" in result.output


class TestRunCommandShouldAcceptOptions:
    """The run command should accept --mode, --provider, --model, --force options."""

    @patch("cli.run_pipeline")
    @patch("cli.load_config")
    def test_with_all_options(self, mock_load_config, mock_run_pipeline, runner, tmp_path):
        config_file = tmp_path / "config.yaml"
        config_file.write_text("pipeline:\n  mode: ocr_text\n", encoding="utf-8")
        mock_load_config.return_value = {"pipeline": {"mode": "vision"}, "llm": {"provider": "openai", "model": "gpt-4o"}}
        mock_run_pipeline.return_value = tmp_path / "results" / "run_001"

        result = runner.invoke(cli, [
            "run",
            "--config", str(config_file),
            "--mode", "vision",
            "--provider", "openai",
            "--model", "gpt-4o",
            "--force",
        ])
        assert result.exit_code == 0
        mock_run_pipeline.assert_called_once()
        # Check force was passed
        call_kwargs = mock_run_pipeline.call_args
        assert call_kwargs[1].get("force") is True or call_kwargs.kwargs.get("force") is True


# =========================================================================
# Spec: evaluate command
# =========================================================================


class TestEvaluateCommandShouldShowHelp:
    def test_help_flag(self, runner):
        result = runner.invoke(cli, ["evaluate", "--help"])
        assert result.exit_code == 0
        assert "--run-dir" in result.output
        assert "--gt-dir" in result.output
        assert "--diagnose" in result.output


class TestEvaluateCommandShouldRequireRunDir:
    def test_missing_run_dir_exits_with_error(self, runner):
        result = runner.invoke(cli, ["evaluate"])
        assert result.exit_code != 0


class TestEvaluateCommandShouldDisplayResults:
    @patch("cli.evaluate_run")
    def test_shows_accuracy(self, mock_eval, runner, tmp_path):
        from src.evaluation.metrics import RunEvaluation

        run_dir = tmp_path / "run"
        run_dir.mkdir()
        gt_dir = tmp_path / "gt"
        gt_dir.mkdir()

        mock_eval.return_value = RunEvaluation(
            run_id="test_run",
            overall_accuracy=0.85,
            document_level_accuracy=0.6,
            field_accuracies={"provider_name": 1.0, "currency": 0.8},
            documents={},
            by_language={},
            by_utility_type={},
            null_summary={"hallucinations": 0, "omissions": 0, "both_null": 0},
        )

        result = runner.invoke(cli, [
            "evaluate",
            "--run-dir", str(run_dir),
            "--gt-dir", str(gt_dir),
        ])
        assert result.exit_code == 0
        assert "85" in result.output  # 0.85 -> 85%
        assert "accuracy" in result.output.lower()


# =========================================================================
# Spec: compare command
# =========================================================================


class TestCompareCommandShouldShowHelp:
    def test_help_flag(self, runner):
        result = runner.invoke(cli, ["compare", "--help"])
        assert result.exit_code == 0
        assert "--runs" in result.output
        assert "--gt-dir" in result.output
        assert "--output" in result.output


class TestCompareCommandShouldRequireRuns:
    def test_missing_runs_exits_with_error(self, runner):
        result = runner.invoke(cli, ["compare"])
        assert result.exit_code != 0


class TestCompareCommandShouldDisplayMatrix:
    @patch("cli.compare_runs")
    def test_shows_accuracy_matrix(self, mock_compare, runner, tmp_path):
        run_a = tmp_path / "run_a"
        run_a.mkdir()
        run_b = tmp_path / "run_b"
        run_b.mkdir()
        gt_dir = tmp_path / "gt"
        gt_dir.mkdir()

        mock_compare.return_value = {
            "accuracy_matrix": {
                "run_a": {"overall_accuracy": 0.9, "document_level_accuracy": 0.8},
                "run_b": {"overall_accuracy": 0.7, "document_level_accuracy": 0.5},
            },
            "performance_matrix": {
                "run_a": {"mean_total_ms": 5000, "mean_llm_call_ms": 3000, "total_estimated_cost_usd": 0.05},
                "run_b": {"mean_total_ms": 4000, "mean_llm_call_ms": 3500, "total_estimated_cost_usd": 0.08},
            },
        }

        result = runner.invoke(cli, [
            "compare",
            "--runs", str(run_a),
            "--runs", str(run_b),
            "--gt-dir", str(gt_dir),
            "--output", str(tmp_path / "reports"),
        ])
        assert result.exit_code == 0
        assert "run_a" in result.output
        assert "run_b" in result.output


# =========================================================================
# Spec: report command
# =========================================================================


class TestReportCommandShouldShowHelp:
    def test_help_flag(self, runner):
        result = runner.invoke(cli, ["report", "--help"])
        assert result.exit_code == 0
        assert "--comparison" in result.output
        assert "--output" in result.output


class TestReportCommandShouldCallGenerateReport:
    @patch("cli.generate_report")
    def test_calls_generate_report(self, mock_gen, runner, tmp_path):
        comp = tmp_path / "comparison.json"
        comp.write_text("{}", encoding="utf-8")
        output = tmp_path / "reports"
        mock_gen.return_value = output

        result = runner.invoke(cli, [
            "report",
            "--comparison", str(comp),
            "--output", str(output),
        ])
        assert result.exit_code == 0
        mock_gen.assert_called_once()


# =========================================================================
# Spec: evaluate --diagnose flag
# =========================================================================


class TestEvaluateCommandDiagnoseFlag:
    """The --diagnose flag should trigger failure diagnosis and print results."""

    @patch("cli.diagnose_document")
    @patch("cli.evaluate_run")
    def test_diagnose_prints_failures(self, mock_eval, mock_diag, runner, tmp_path):
        from src.evaluation.metrics import RunEvaluation, DocumentResult, FieldResult
        from src.evaluation.diagnosis import FieldDiagnosis

        run_dir = tmp_path / "run"
        doc_dir = run_dir / "documents" / "doc1"
        doc_dir.mkdir(parents=True)
        (doc_dir / "metadata.json").write_text(
            json.dumps({"pipeline_mode": "vision"}), encoding="utf-8"
        )
        gt_dir = tmp_path / "gt"
        gt_dir.mkdir()

        fr = FieldResult(
            field_name="provider_name",
            predicted="wrong",
            ground_truth="correct",
            match=False,
            category="incorrect",
            similarity=0.5,
        )
        dr = DocumentResult(
            document_id="doc1",
            fields=[fr],
            all_correct=False,
            incorrect=1,
        )
        mock_eval.return_value = RunEvaluation(
            run_id="test_run",
            overall_accuracy=0.5,
            document_level_accuracy=0.0,
            field_accuracies={"provider_name": 0.0},
            documents={"doc1": dr},
            by_language={},
            by_utility_type={},
            null_summary={"hallucinations": 0, "omissions": 0, "both_null": 0},
        )
        mock_diag.return_value = [
            FieldDiagnosis(
                field_name="provider_name",
                predicted="wrong",
                ground_truth="correct",
                failure_type="vision_model_failure",
            )
        ]

        result = runner.invoke(cli, [
            "evaluate",
            "--run-dir", str(run_dir),
            "--gt-dir", str(gt_dir),
            "--diagnose",
        ])
        assert result.exit_code == 0
        assert "diagnosis" in result.output.lower() or "diagnosed" in result.output.lower()
        assert "provider_name" in result.output
        assert "vision_model_failure" in result.output

    @patch("cli.diagnose_document")
    @patch("cli.evaluate_run")
    def test_diagnose_skips_correct_docs(self, mock_eval, mock_diag, runner, tmp_path):
        from src.evaluation.metrics import RunEvaluation, DocumentResult, FieldResult

        run_dir = tmp_path / "run"
        doc_dir = run_dir / "documents" / "doc1"
        doc_dir.mkdir(parents=True)
        gt_dir = tmp_path / "gt"
        gt_dir.mkdir()

        fr = FieldResult(
            field_name="provider_name",
            predicted="correct",
            ground_truth="correct",
            match=True,
            category="correct",
            similarity=1.0,
        )
        dr = DocumentResult(
            document_id="doc1",
            fields=[fr],
            all_correct=True,
        )
        mock_eval.return_value = RunEvaluation(
            run_id="test_run",
            overall_accuracy=1.0,
            document_level_accuracy=1.0,
            field_accuracies={"provider_name": 1.0},
            documents={"doc1": dr},
            by_language={},
            by_utility_type={},
            null_summary={"hallucinations": 0, "omissions": 0, "both_null": 0},
        )

        result = runner.invoke(cli, [
            "evaluate",
            "--run-dir", str(run_dir),
            "--gt-dir", str(gt_dir),
            "--diagnose",
        ])
        assert result.exit_code == 0
        assert "Total failures diagnosed: 0" in result.output
        mock_diag.assert_not_called()

    @patch("cli.evaluate_run")
    def test_without_diagnose_flag_no_diagnosis_output(self, mock_eval, runner, tmp_path):
        from src.evaluation.metrics import RunEvaluation

        run_dir = tmp_path / "run"
        (run_dir / "documents").mkdir(parents=True)
        gt_dir = tmp_path / "gt"
        gt_dir.mkdir()

        mock_eval.return_value = RunEvaluation(
            run_id="test_run",
            overall_accuracy=0.85,
            document_level_accuracy=0.6,
            field_accuracies={"provider_name": 1.0},
            documents={},
            by_language={},
            by_utility_type={},
            null_summary={"hallucinations": 0, "omissions": 0, "both_null": 0},
        )

        result = runner.invoke(cli, [
            "evaluate",
            "--run-dir", str(run_dir),
            "--gt-dir", str(gt_dir),
        ])
        assert result.exit_code == 0
        assert "diagnosis" not in result.output.lower()
        assert "diagnosed" not in result.output.lower()
