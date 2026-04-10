"""TDD-style specification for src/utils.py.

Covers: load_config, deep_merge, pdf_to_images (error path),
load_prompt_template, read_json, write_json, write_text, copy_file, setup_logging.
"""

import json
import logging
from pathlib import Path

import pytest
import yaml

from src.utils import (
    copy_file,
    deep_merge,
    load_config,
    load_prompt_template,
    pdf_to_images,
    read_json,
    setup_logging,
    write_json,
    write_text,
)


# =========================================================================
# Spec: deep_merge
# =========================================================================


class TestDeepMergeShouldMergeInPlace:
    """Given a base dict and overrides, deep_merge should recursively merge
    overrides into base, mutating base."""

    def test_flat_override(self):
        base = {"a": 1, "b": 2}
        deep_merge(base, {"b": 99, "c": 3})
        assert base == {"a": 1, "b": 99, "c": 3}

    def test_nested_merge(self):
        base = {"llm": {"provider": "openai", "model": "gpt-4o"}}
        deep_merge(base, {"llm": {"model": "gpt-4o-mini"}})
        assert base["llm"]["provider"] == "openai"
        assert base["llm"]["model"] == "gpt-4o-mini"

    def test_adds_new_nested_key(self):
        base = {"llm": {"provider": "openai"}}
        deep_merge(base, {"llm": {"temperature": 0.5}})
        assert base["llm"]["temperature"] == 0.5
        assert base["llm"]["provider"] == "openai"

    def test_override_scalar_with_dict_replaces(self):
        base = {"key": "scalar"}
        deep_merge(base, {"key": {"nested": True}})
        assert base["key"] == {"nested": True}

    def test_override_dict_with_scalar_replaces(self):
        base = {"key": {"nested": True}}
        deep_merge(base, {"key": "scalar"})
        assert base["key"] == "scalar"

    def test_empty_overrides(self):
        base = {"a": 1}
        deep_merge(base, {})
        assert base == {"a": 1}

    def test_empty_base(self):
        base = {}
        deep_merge(base, {"a": 1})
        assert base == {"a": 1}

    def test_deeply_nested(self):
        base = {"a": {"b": {"c": 1}}}
        deep_merge(base, {"a": {"b": {"d": 2}}})
        assert base == {"a": {"b": {"c": 1, "d": 2}}}


# =========================================================================
# Spec: load_config
# =========================================================================


class TestLoadConfigShouldLoadYaml:
    """Given a valid YAML config file, load_config should return a dict."""

    def test_loads_yaml(self, tmp_path):
        cfg = tmp_path / "config.yaml"
        cfg.write_text(yaml.dump({"pipeline": {"mode": "vision"}}), encoding="utf-8")
        result = load_config(cfg)
        assert result["pipeline"]["mode"] == "vision"

    def test_with_overrides(self, tmp_path):
        cfg = tmp_path / "config.yaml"
        cfg.write_text(
            yaml.dump({"llm": {"provider": "openai", "model": "gpt-4o"}}),
            encoding="utf-8",
        )
        result = load_config(cfg, overrides={"llm": {"model": "gpt-4o-mini"}})
        assert result["llm"]["model"] == "gpt-4o-mini"
        assert result["llm"]["provider"] == "openai"

    def test_empty_yaml_returns_empty_dict(self, tmp_path):
        cfg = tmp_path / "empty.yaml"
        cfg.write_text("", encoding="utf-8")
        result = load_config(cfg)
        assert result == {}


class TestLoadConfigShouldRaiseOnMissing:
    def test_missing_file(self, tmp_path):
        with pytest.raises(FileNotFoundError, match="Config file not found"):
            load_config(tmp_path / "missing.yaml")


class TestLoadConfigShouldRaiseOnInvalidYaml:
    """Given a YAML file with syntax errors, load_config should propagate
    the YAML parsing error."""

    def test_invalid_yaml_syntax(self, tmp_path):
        cfg = tmp_path / "bad.yaml"
        cfg.write_text("key: [unclosed bracket\n  bad: indent", encoding="utf-8")
        with pytest.raises(yaml.YAMLError):
            load_config(cfg)

    def test_yaml_with_tabs(self, tmp_path):
        cfg = tmp_path / "tabs.yaml"
        cfg.write_text("key:\n\t- tab indented", encoding="utf-8")
        with pytest.raises(yaml.YAMLError):
            load_config(cfg)


# =========================================================================
# Spec: load_prompt_template
# =========================================================================


class TestLoadPromptTemplateShouldReadFile:
    def test_reads_template(self, tmp_path):
        p = tmp_path / "prompt.txt"
        p.write_text("Extract {schema_description}", encoding="utf-8")
        result = load_prompt_template(p)
        assert "Extract" in result
        assert "{schema_description}" in result

    def test_preserves_content(self, tmp_path):
        content = "Line 1\nLine 2\nLine 3"
        p = tmp_path / "prompt.txt"
        p.write_text(content, encoding="utf-8")
        assert load_prompt_template(p) == content


class TestLoadPromptTemplateShouldRaiseOnMissing:
    def test_missing_file(self, tmp_path):
        with pytest.raises(FileNotFoundError, match="Prompt template not found"):
            load_prompt_template(tmp_path / "missing.txt")


# =========================================================================
# Spec: pdf_to_images
# =========================================================================


class TestPdfToImagesShouldRaiseOnMissingFile:
    """Given a path to a non-existent PDF, should raise FileNotFoundError."""

    def test_missing_pdf(self, tmp_path):
        with pytest.raises(FileNotFoundError, match="PDF not found"):
            pdf_to_images(tmp_path / "missing.pdf")


# =========================================================================
# Spec: read_json
# =========================================================================


class TestReadJsonShouldParseFile:
    def test_reads_dict(self, tmp_path):
        p = tmp_path / "data.json"
        p.write_text('{"key": "value", "num": 42}', encoding="utf-8")
        result = read_json(p)
        assert result == {"key": "value", "num": 42}

    def test_reads_list(self, tmp_path):
        p = tmp_path / "data.json"
        p.write_text('[1, 2, 3]', encoding="utf-8")
        result = read_json(p)
        assert result == [1, 2, 3]

    def test_reads_nested(self, tmp_path):
        p = tmp_path / "data.json"
        p.write_text('{"a": {"b": [1, 2]}}', encoding="utf-8")
        result = read_json(p)
        assert result["a"]["b"] == [1, 2]


class TestReadJsonShouldRaiseOnInvalid:
    def test_invalid_json(self, tmp_path):
        p = tmp_path / "bad.json"
        p.write_text("not json", encoding="utf-8")
        with pytest.raises(json.JSONDecodeError):
            read_json(p)


# =========================================================================
# Spec: write_json
# =========================================================================


class TestWriteJsonShouldPersistData:
    def test_writes_and_reads_back(self, tmp_path):
        p = tmp_path / "out.json"
        data = {"name": "test", "values": [1, 2, 3]}
        write_json(p, data)
        assert json.loads(p.read_text(encoding="utf-8")) == data

    def test_creates_parent_directories(self, tmp_path):
        p = tmp_path / "sub" / "dir" / "out.json"
        write_json(p, {"ok": True})
        assert p.exists()
        assert json.loads(p.read_text(encoding="utf-8")) == {"ok": True}

    def test_handles_non_serialisable_with_default_str(self, tmp_path):
        """write_json uses default=str, so dates/paths should be serialised."""
        from datetime import date

        p = tmp_path / "out.json"
        write_json(p, {"date": date(2024, 1, 1)})
        result = json.loads(p.read_text(encoding="utf-8"))
        assert result["date"] == "2024-01-01"

    def test_non_ascii_preserved(self, tmp_path):
        p = tmp_path / "out.json"
        write_json(p, {"name": "café"})
        content = p.read_text(encoding="utf-8")
        assert "café" in content  # ensure_ascii=False


# =========================================================================
# Spec: write_text
# =========================================================================


class TestWriteTextShouldPersistString:
    def test_writes_and_reads_back(self, tmp_path):
        p = tmp_path / "out.txt"
        write_text(p, "hello world")
        assert p.read_text(encoding="utf-8") == "hello world"

    def test_creates_parent_directories(self, tmp_path):
        p = tmp_path / "sub" / "dir" / "out.txt"
        write_text(p, "nested")
        assert p.exists()
        assert p.read_text(encoding="utf-8") == "nested"

    def test_overwrites_existing(self, tmp_path):
        p = tmp_path / "out.txt"
        write_text(p, "first")
        write_text(p, "second")
        assert p.read_text(encoding="utf-8") == "second"


# =========================================================================
# Spec: copy_file
# =========================================================================


class TestCopyFileShouldDuplicate:
    def test_copies_content(self, tmp_path):
        src = tmp_path / "src.txt"
        src.write_text("content", encoding="utf-8")
        dst = tmp_path / "dst.txt"
        copy_file(src, dst)
        assert dst.read_text(encoding="utf-8") == "content"

    def test_creates_parent_directories(self, tmp_path):
        src = tmp_path / "src.txt"
        src.write_text("data", encoding="utf-8")
        dst = tmp_path / "sub" / "dir" / "dst.txt"
        copy_file(src, dst)
        assert dst.exists()
        assert dst.read_text(encoding="utf-8") == "data"

    def test_binary_copy(self, tmp_path):
        src = tmp_path / "src.bin"
        src.write_bytes(b"\x00\x01\x02")
        dst = tmp_path / "dst.bin"
        copy_file(src, dst)
        assert dst.read_bytes() == b"\x00\x01\x02"


# =========================================================================
# Spec: setup_logging
# =========================================================================


class TestSetupLoggingShouldNotCrash:
    """setup_logging should configure logging without raising."""

    def test_default_level(self):
        setup_logging()

    def test_custom_level(self):
        setup_logging(level=logging.DEBUG)
