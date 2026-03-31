from __future__ import annotations

import json
import logging
import shutil
from pathlib import Path
from typing import Any

import yaml
from PIL import Image

from .env import load_env

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Config loading
# ---------------------------------------------------------------------------

def load_config(config_path: str | Path, overrides: dict | None = None) -> dict:
    """Load a YAML config file and optionally merge CLI overrides."""
    load_env()
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    with open(path, encoding="utf-8") as f:
        config = yaml.safe_load(f) or {}

    if overrides:
        deep_merge(config, overrides)

    return config


def deep_merge(base: dict, overrides: dict) -> None:
    """Recursively merge *overrides* into *base* in place."""
    for key, value in overrides.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            deep_merge(base[key], value)
        else:
            base[key] = value


# ---------------------------------------------------------------------------
# PDF conversion
# ---------------------------------------------------------------------------

def pdf_to_images(pdf_path: str | Path, dpi: int = 300) -> list[Image.Image]:
    """Convert every page of a PDF into a PIL Image.

    Requires the ``poppler`` system library and the ``pdf2image`` package.
    """
    from pdf2image import convert_from_path

    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    images = convert_from_path(str(pdf_path), dpi=dpi)
    logger.info("Converted %s: %d page(s)", pdf_path.name, len(images))
    return images


# ---------------------------------------------------------------------------
# Prompt template loading
# ---------------------------------------------------------------------------

def load_prompt_template(prompt_path: str | Path) -> str:
    """Read a prompt template file and return its contents as a string."""
    path = Path(prompt_path)
    if not path.exists():
        raise FileNotFoundError(f"Prompt template not found: {path}")
    return path.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# JSON / file helpers
# ---------------------------------------------------------------------------

def read_json(path: str | Path) -> Any:
    """Read and parse a JSON file."""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def write_json(path: str | Path, data: Any, indent: int = 2) -> None:
    """Write data to a JSON file, creating parent directories as needed."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent, default=str, ensure_ascii=False)


def write_text(path: str | Path, text: str) -> None:
    """Write text to a file, creating parent directories as needed."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def copy_file(src: str | Path, dst: str | Path) -> None:
    """Copy a file, creating the destination's parent directories."""
    dst = Path(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------

def setup_logging(level: int = logging.INFO) -> None:
    """Configure basic logging for the pipeline."""
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
