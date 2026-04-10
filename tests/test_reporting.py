"""TDD-style specification for src/reporting.py — generate_report, _label, chart/summary output.

Uses a synthetic comparison.json to avoid depending on real pipeline runs.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.reporting import generate_report, _label


# =========================================================================
# Spec: _label helper
# =========================================================================


class TestLabelShouldMapKnownRunIds:
    """Given a run ID ending with a known condition suffix, _label should
    return the human-readable short name."""

    @pytest.mark.parametrize("suffix, expected", [
        ("20260402_162321_openai_gpt4o_ocr_text", "GPT-4o OCR"),
        ("20260402_162321_openai_gpt4o_vision", "GPT-4o Vision"),
        ("20260402_162321_anthropic_claudesonnet4520250929_ocr_text", "Sonnet 4.5 OCR"),
        ("20260402_162321_anthropic_claudesonnet4520250929_vision", "Sonnet 4.5 Vision"),
    ])
    def test_known_suffix(self, suffix, expected):
        assert _label(suffix) == expected


class TestLabelShouldFallbackForUnknown:
    """Given a run ID with no known suffix, _label should return last 30 chars."""

    def test_unknown_run_id(self):
        result = _label("20260402_unknown_provider_model_mode")
        assert len(result) <= 30

    def test_short_id(self):
        result = _label("short")
        assert result == "short"


# =========================================================================
# Spec: generate_report
# =========================================================================


@pytest.fixture
def comparison_data(tmp_path):
    """Create a synthetic comparison.json for testing report generation."""
    # Two conditions with realistic structure
    data = {
        "runs": ["results/runs/run_openai_gpt4o_ocr_text", "results/runs/run_openai_gpt4o_vision"],
        "accuracy_matrix": {
            "run_openai_gpt4o_ocr_text": {
                "overall_accuracy": 0.85,
                "document_level_accuracy": 0.6,
                "provider_name": 1.0,
                "utility_type": 1.0,
                "bill_number": 0.8,
                "bill_date": 0.8,
                "billing_period_start": 0.6,
                "billing_period_end": 0.6,
                "due_date": 0.8,
                "total_amount_due": 1.0,
                "currency": 1.0,
                "account_number": 0.8,
                "consumption_amount": 0.8,
                "consumption_unit": 1.0,
            },
            "run_openai_gpt4o_vision": {
                "overall_accuracy": 0.75,
                "document_level_accuracy": 0.4,
                "provider_name": 0.8,
                "utility_type": 1.0,
                "bill_number": 0.6,
                "bill_date": 0.6,
                "billing_period_start": 0.6,
                "billing_period_end": 0.6,
                "due_date": 0.8,
                "total_amount_due": 0.8,
                "currency": 1.0,
                "account_number": 0.6,
                "consumption_amount": 0.8,
                "consumption_unit": 0.8,
            },
        },
        "performance_matrix": {
            "run_openai_gpt4o_ocr_text": {
                "mean_total_ms": 5000,
                "mean_llm_call_ms": 3000,
                "mean_ocr_ms": 1200,
                "total_estimated_cost_usd": 0.05,
                "documents_timed": 5,
            },
            "run_openai_gpt4o_vision": {
                "mean_total_ms": 4000,
                "mean_llm_call_ms": 3500,
                "mean_ocr_ms": 0,
                "total_estimated_cost_usd": 0.08,
                "documents_timed": 5,
            },
        },
        "null_analysis": {
            "run_openai_gpt4o_ocr_text": {"hallucinations": 1, "omissions": 2, "both_null": 10},
            "run_openai_gpt4o_vision": {"hallucinations": 3, "omissions": 1, "both_null": 10},
        },
        "slice_by_language": {
            "run_openai_gpt4o_ocr_text": {
                "en": {"accuracy": 0.9, "document_level_accuracy": 0.8, "documents": 3},
                "de": {"accuracy": 0.7, "document_level_accuracy": 0.5, "documents": 2},
            },
            "run_openai_gpt4o_vision": {
                "en": {"accuracy": 0.8, "document_level_accuracy": 0.6, "documents": 3},
                "de": {"accuracy": 0.6, "document_level_accuracy": 0.0, "documents": 2},
            },
        },
        "slice_by_utility_type": {
            "run_openai_gpt4o_ocr_text": {
                "electricity": {"accuracy": 0.9, "document_level_accuracy": 0.8, "documents": 3},
                "gas": {"accuracy": 0.8, "document_level_accuracy": 0.5, "documents": 2},
            },
            "run_openai_gpt4o_vision": {
                "electricity": {"accuracy": 0.8, "document_level_accuracy": 0.5, "documents": 3},
                "gas": {"accuracy": 0.7, "document_level_accuracy": 0.0, "documents": 2},
            },
        },
    }

    comparison_path = tmp_path / "comparison.json"
    comparison_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    output_dir = tmp_path / "output"
    return comparison_path, output_dir


class TestGenerateReportShouldCreateFiguresDirectory:
    def test_figures_dir_created(self, comparison_data):
        comp_path, out_dir = comparison_data
        generate_report(comp_path, out_dir)
        assert (out_dir / "figures").is_dir()


class TestGenerateReportShouldCreate6Charts:
    """Given a valid comparison.json, generate_report should produce
    exactly 6 PNG chart files."""

    def test_overall_accuracy_chart(self, comparison_data):
        comp_path, out_dir = comparison_data
        generate_report(comp_path, out_dir)
        assert (out_dir / "figures" / "overall_accuracy.png").exists()

    def test_field_accuracy_heatmap(self, comparison_data):
        comp_path, out_dir = comparison_data
        generate_report(comp_path, out_dir)
        assert (out_dir / "figures" / "field_accuracy_heatmap.png").exists()

    def test_timing_breakdown_chart(self, comparison_data):
        comp_path, out_dir = comparison_data
        generate_report(comp_path, out_dir)
        assert (out_dir / "figures" / "timing_breakdown.png").exists()

    def test_cost_comparison_chart(self, comparison_data):
        comp_path, out_dir = comparison_data
        generate_report(comp_path, out_dir)
        assert (out_dir / "figures" / "cost_comparison.png").exists()

    def test_accuracy_by_language_chart(self, comparison_data):
        comp_path, out_dir = comparison_data
        generate_report(comp_path, out_dir)
        assert (out_dir / "figures" / "accuracy_by_language.png").exists()

    def test_accuracy_by_utility_type_chart(self, comparison_data):
        comp_path, out_dir = comparison_data
        generate_report(comp_path, out_dir)
        assert (out_dir / "figures" / "accuracy_by_utility_type.png").exists()

    def test_all_six_charts_exist(self, comparison_data):
        comp_path, out_dir = comparison_data
        generate_report(comp_path, out_dir)
        expected_charts = [
            "overall_accuracy.png",
            "field_accuracy_heatmap.png",
            "timing_breakdown.png",
            "cost_comparison.png",
            "accuracy_by_language.png",
            "accuracy_by_utility_type.png",
        ]
        for chart in expected_charts:
            assert (out_dir / "figures" / chart).exists(), f"Missing: {chart}"


class TestGenerateReportShouldCreateSummaryText:
    """generate_report should produce a summary.txt with key information."""

    def test_summary_exists(self, comparison_data):
        comp_path, out_dir = comparison_data
        generate_report(comp_path, out_dir)
        assert (out_dir / "summary.txt").exists()

    def test_summary_contains_header(self, comparison_data):
        comp_path, out_dir = comparison_data
        generate_report(comp_path, out_dir)
        content = (out_dir / "summary.txt").read_text(encoding="utf-8")
        assert "COMPARISON SUMMARY" in content

    def test_summary_contains_results_overview(self, comparison_data):
        comp_path, out_dir = comparison_data
        generate_report(comp_path, out_dir)
        content = (out_dir / "summary.txt").read_text(encoding="utf-8")
        assert "RESULTS OVERVIEW" in content

    def test_summary_contains_null_analysis(self, comparison_data):
        comp_path, out_dir = comparison_data
        generate_report(comp_path, out_dir)
        content = (out_dir / "summary.txt").read_text(encoding="utf-8")
        assert "NULL ANALYSIS" in content

    def test_summary_contains_accuracy_by_language(self, comparison_data):
        comp_path, out_dir = comparison_data
        generate_report(comp_path, out_dir)
        content = (out_dir / "summary.txt").read_text(encoding="utf-8")
        assert "ACCURACY BY LANGUAGE" in content

    def test_summary_contains_accuracy_by_utility_type(self, comparison_data):
        comp_path, out_dir = comparison_data
        generate_report(comp_path, out_dir)
        content = (out_dir / "summary.txt").read_text(encoding="utf-8")
        assert "ACCURACY BY UTILITY TYPE" in content

    def test_summary_contains_field_level_accuracy(self, comparison_data):
        comp_path, out_dir = comparison_data
        generate_report(comp_path, out_dir)
        content = (out_dir / "summary.txt").read_text(encoding="utf-8")
        assert "FIELD-LEVEL ACCURACY" in content

    def test_summary_contains_best_worst(self, comparison_data):
        comp_path, out_dir = comparison_data
        generate_report(comp_path, out_dir)
        content = (out_dir / "summary.txt").read_text(encoding="utf-8")
        assert "Best overall accuracy" in content
        assert "Worst overall accuracy" in content

    def test_summary_contains_easiest_hardest_field(self, comparison_data):
        comp_path, out_dir = comparison_data
        generate_report(comp_path, out_dir)
        content = (out_dir / "summary.txt").read_text(encoding="utf-8")
        assert "Easiest field" in content
        assert "Hardest field" in content


class TestGenerateReportShouldReturnOutputDir:
    def test_returns_output_path(self, comparison_data):
        comp_path, out_dir = comparison_data
        result = generate_report(comp_path, out_dir)
        assert result == out_dir


class TestGenerateReportChartsShouldBeNonEmpty:
    """Chart PNG files should have non-trivial file sizes."""

    def test_charts_have_content(self, comparison_data):
        comp_path, out_dir = comparison_data
        generate_report(comp_path, out_dir)
        for png in (out_dir / "figures").glob("*.png"):
            assert png.stat().st_size > 1000, f"{png.name} seems too small"


# =========================================================================
# Spec: generate_report — single condition (degenerate comparison)
# =========================================================================


@pytest.fixture
def single_condition_data(tmp_path):
    """Create a comparison.json with only one experimental condition."""
    data = {
        "runs": ["results/runs/run_openai_gpt4o_ocr_text"],
        "accuracy_matrix": {
            "run_openai_gpt4o_ocr_text": {
                "overall_accuracy": 0.85,
                "document_level_accuracy": 0.6,
                "provider_name": 1.0,
                "utility_type": 1.0,
                "bill_number": 0.8,
                "bill_date": 0.8,
                "billing_period_start": 0.6,
                "billing_period_end": 0.6,
                "due_date": 0.8,
                "total_amount_due": 1.0,
                "currency": 1.0,
                "account_number": 0.8,
                "consumption_amount": 0.8,
                "consumption_unit": 1.0,
            },
        },
        "performance_matrix": {
            "run_openai_gpt4o_ocr_text": {
                "mean_total_ms": 5000,
                "mean_llm_call_ms": 3000,
                "mean_ocr_ms": 1200,
                "total_estimated_cost_usd": 0.05,
                "documents_timed": 5,
            },
        },
        "null_analysis": {
            "run_openai_gpt4o_ocr_text": {
                "hallucinations": 1,
                "omissions": 2,
                "both_null": 10,
            },
        },
        "slice_by_language": {
            "run_openai_gpt4o_ocr_text": {
                "en": {"accuracy": 0.9, "document_level_accuracy": 0.8, "documents": 3},
            },
        },
        "slice_by_utility_type": {
            "run_openai_gpt4o_ocr_text": {
                "electricity": {"accuracy": 0.9, "document_level_accuracy": 0.8, "documents": 3},
            },
        },
    }
    comparison_path = tmp_path / "comparison.json"
    comparison_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    output_dir = tmp_path / "output_single"
    return comparison_path, output_dir


class TestGenerateReportSingleCondition:
    """generate_report should handle a single-condition comparison gracefully."""

    def test_produces_all_charts(self, single_condition_data):
        comp_path, out_dir = single_condition_data
        generate_report(comp_path, out_dir)
        expected = [
            "overall_accuracy.png",
            "field_accuracy_heatmap.png",
            "timing_breakdown.png",
            "cost_comparison.png",
            "accuracy_by_language.png",
            "accuracy_by_utility_type.png",
        ]
        for chart in expected:
            assert (out_dir / "figures" / chart).exists(), f"Missing: {chart}"

    def test_produces_summary(self, single_condition_data):
        comp_path, out_dir = single_condition_data
        generate_report(comp_path, out_dir)
        assert (out_dir / "summary.txt").exists()
        content = (out_dir / "summary.txt").read_text(encoding="utf-8")
        assert "COMPARISON SUMMARY" in content

    def test_best_and_worst_present(self, single_condition_data):
        comp_path, out_dir = single_condition_data
        generate_report(comp_path, out_dir)
        content = (out_dir / "summary.txt").read_text(encoding="utf-8")
        assert "Best overall accuracy" in content
        assert "Worst overall accuracy" in content

    def test_returns_output_dir(self, single_condition_data):
        comp_path, out_dir = single_condition_data
        result = generate_report(comp_path, out_dir)
        assert result == out_dir

    def test_charts_are_non_empty(self, single_condition_data):
        comp_path, out_dir = single_condition_data
        generate_report(comp_path, out_dir)
        for png in (out_dir / "figures").glob("*.png"):
            assert png.stat().st_size > 1000, f"{png.name} seems too small"
