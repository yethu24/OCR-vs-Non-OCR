"""TDD-style specification for src/env.py — load_env."""

from __future__ import annotations

import builtins
import sys
from unittest.mock import patch, MagicMock

import pytest

from src.env import load_env


# =========================================================================
# Spec: load_env — normal operation
# =========================================================================


class TestLoadEnvShouldNotRaise:
    """load_env should never raise regardless of environment state."""

    def test_does_not_raise(self):
        load_env()

    def test_idempotent(self):
        load_env()
        load_env()


# =========================================================================
# Spec: load_env — dotenv unavailable
# =========================================================================


class TestLoadEnvShouldHandleMissingDotenv:
    """When python-dotenv is not installed, load_env should return silently."""

    def test_returns_silently_without_dotenv(self):
        saved = {}
        for key in list(sys.modules.keys()):
            if key == "dotenv" or key.startswith("dotenv."):
                saved[key] = sys.modules.pop(key)

        real_import = builtins.__import__

        def blocking_import(name, *args, **kwargs):
            if name == "dotenv" or name.startswith("dotenv."):
                raise ImportError(f"Mocked: no {name}")
            return real_import(name, *args, **kwargs)

        try:
            with patch("builtins.__import__", side_effect=blocking_import):
                load_env()
        finally:
            sys.modules.update(saved)


# =========================================================================
# Spec: load_env — .env file missing
# =========================================================================


class TestLoadEnvShouldHandleMissingEnvFile:
    """When .env file does not exist, load_env should return silently
    (dotenv.load_dotenv is not called)."""

    def test_no_crash_without_env_file(self):
        load_env()
