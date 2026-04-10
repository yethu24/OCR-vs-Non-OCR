"""TDD-style specification for src/performance.py — Timer, estimate_cost, get_system_snapshot."""

import time

import pytest

from src.performance import Timer, estimate_cost, get_system_snapshot, _PRICING


# =========================================================================
# Spec: Timer context manager
# =========================================================================


class TestTimerShouldMeasureElapsedTime:
    """Given work done inside a Timer context, elapsed_ms should reflect
    the wall-clock duration in milliseconds."""

    def test_elapsed_is_positive_for_real_work(self):
        with Timer() as t:
            time.sleep(0.01)
        assert t.elapsed_ms > 0

    def test_elapsed_roughly_correct(self):
        with Timer() as t:
            time.sleep(0.05)
        # Allow wide tolerance for CI variability
        assert 20 < t.elapsed_ms < 500

    def test_near_zero_for_no_work(self):
        with Timer() as t:
            pass
        assert t.elapsed_ms < 50


class TestTimerShouldInitialiseToZero:
    """Before entering the context, elapsed_ms should be 0."""

    def test_initial_value(self):
        t = Timer()
        assert t.elapsed_ms == 0.0


class TestTimerShouldSupportContextProtocol:
    """Timer should work as a context manager and return itself."""

    def test_returns_self(self):
        timer = Timer()
        with timer as t:
            assert t is timer

    def test_elapsed_set_after_exit(self):
        with Timer() as t:
            pass
        assert isinstance(t.elapsed_ms, float)


# =========================================================================
# Spec: estimate_cost
# =========================================================================


class TestEstimateCostShouldCalculateForKnownModels:
    """Given a known model, estimate_cost should return the correct USD cost
    based on per-token pricing."""

    def test_gpt4o(self):
        # (1000 * 2.50 + 500 * 10.00) / 1_000_000 = 0.0075
        cost = estimate_cost("openai", "gpt-4o", input_tokens=1000, output_tokens=500)
        assert abs(cost - 0.0075) < 1e-9

    def test_gpt4o_mini(self):
        # (1000 * 0.15 + 500 * 0.60) / 1_000_000 = 0.00045
        cost = estimate_cost("openai", "gpt-4o-mini", input_tokens=1000, output_tokens=500)
        assert abs(cost - 0.00045) < 1e-9

    def test_claude_sonnet(self):
        # (2000 * 3.00 + 1000 * 15.00) / 1_000_000 = 0.021
        cost = estimate_cost("anthropic", "claude-3-5-sonnet", input_tokens=2000, output_tokens=1000)
        assert abs(cost - 0.021) < 1e-9

    def test_claude_haiku(self):
        # (10000 * 0.25 + 5000 * 1.25) / 1_000_000 = 0.00875
        cost = estimate_cost("anthropic", "claude-3-haiku-20240307", input_tokens=10000, output_tokens=5000)
        assert abs(cost - 0.00875) < 1e-9


class TestEstimateCostShouldHandleProviderPrefix:
    """Given a model ID with a provider prefix (e.g. 'openai/gpt-4o'),
    should strip the prefix and look up pricing."""

    def test_strips_prefix(self):
        cost = estimate_cost("openai", "openai/gpt-4o", input_tokens=1000, output_tokens=500)
        assert abs(cost - 0.0075) < 1e-9


class TestEstimateCostShouldReturnZeroForUnknown:
    """Given an unknown model, should return 0.0 without raising."""

    def test_unknown_model(self):
        cost = estimate_cost("openai", "unknown-model-xyz", 1000, 500)
        assert cost == 0.0


class TestEstimateCostEdgeCases:
    def test_zero_tokens(self):
        cost = estimate_cost("openai", "gpt-4o", 0, 0)
        assert cost == 0.0

    def test_only_input_tokens(self):
        cost = estimate_cost("openai", "gpt-4o", input_tokens=1000, output_tokens=0)
        assert abs(cost - 0.0025) < 1e-9

    def test_only_output_tokens(self):
        cost = estimate_cost("openai", "gpt-4o", input_tokens=0, output_tokens=1000)
        assert abs(cost - 0.01) < 1e-9


class TestPricingTableShouldCoverAllBaselineModels:
    """The pricing table should contain entries for all models used in the project."""

    @pytest.mark.parametrize("model", [
        "gpt-4o", "gpt-4o-mini",
        "claude-sonnet-4-5-20250929", "claude-3-5-sonnet",
        "claude-3-haiku-20240307",
    ])
    def test_model_in_pricing(self, model):
        assert model in _PRICING

    def test_pricing_tuples_are_positive(self):
        for model, (inp, out) in _PRICING.items():
            assert inp >= 0, f"{model} input price negative"
            assert out >= 0, f"{model} output price negative"


# =========================================================================
# Spec: get_system_snapshot
# =========================================================================


class TestGetSystemSnapshotShouldReturnDict:
    """get_system_snapshot should always return a dict (empty if psutil missing)."""

    def test_returns_dict(self):
        snap = get_system_snapshot()
        assert isinstance(snap, dict)

    def test_has_expected_keys_if_available(self):
        snap = get_system_snapshot()
        if snap:  # psutil may not be installed in CI
            assert "cpu_percent" in snap
            assert "memory_rss_mb" in snap
            assert isinstance(snap["memory_rss_mb"], float)


class TestGetSystemSnapshotShouldHandleFailures:
    """get_system_snapshot should return {} if psutil raises any exception."""

    def test_returns_empty_on_process_error(self):
        try:
            import psutil
            from unittest.mock import patch
            with patch.object(psutil, "Process", side_effect=RuntimeError("mocked")):
                snap = get_system_snapshot()
                assert snap == {}
        except ImportError:
            snap = get_system_snapshot()
            assert snap == {}

    def test_returns_empty_when_psutil_unavailable(self):
        import sys
        from unittest.mock import patch
        import builtins

        saved = {}
        for key in list(sys.modules.keys()):
            if key == "psutil" or key.startswith("psutil."):
                saved[key] = sys.modules.pop(key)

        real_import = builtins.__import__

        def blocking_import(name, *args, **kwargs):
            if name == "psutil" or name.startswith("psutil."):
                raise ImportError(f"Mocked: no {name}")
            return real_import(name, *args, **kwargs)

        try:
            with patch("builtins.__import__", side_effect=blocking_import):
                snap = get_system_snapshot()
                assert snap == {}
        finally:
            sys.modules.update(saved)
