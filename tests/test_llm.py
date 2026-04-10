"""TDD-style specification for src/llm/ — LLMProvider, providers, registry, fence stripping.

All tests mock external SDK calls (openai, anthropic) via sys.modules
since the packages are not installed in the test environment.
"""

from unittest.mock import patch, MagicMock
import io
import base64
import os
import sys

import pytest
from PIL import Image

from src.llm.base import LLMProvider
from src.llm.anthropic_provider import _strip_json_fencing
from src.llm.registry import get_provider, _import_class


# ---------------------------------------------------------------------------
# Helpers: create mock SDK modules
# ---------------------------------------------------------------------------

def _mock_openai_module():
    """Create a fake 'openai' module with OpenAI client mock."""
    mock_mod = MagicMock()
    mock_mod.OpenAI.return_value = MagicMock()  # client instance
    return mock_mod


def _mock_anthropic_module():
    """Create a fake 'anthropic' module with Anthropic client mock."""
    mock_mod = MagicMock()
    mock_mod.Anthropic.return_value = MagicMock()  # client instance
    return mock_mod


# =========================================================================
# Spec: LLMProvider ABC
# =========================================================================


class TestLLMProviderShouldBeAbstract:
    """LLMProvider defines the contract — it cannot be instantiated directly."""

    def test_cannot_instantiate(self):
        with pytest.raises(TypeError):
            LLMProvider(model="test")

    def test_incomplete_subclass_raises(self):
        class Incomplete(LLMProvider):
            pass

        with pytest.raises(TypeError):
            Incomplete(model="test")


class TestLLMProviderShouldStoreConfig:
    """A concrete subclass should inherit constructor defaults."""

    def _make_concrete(self):
        class Concrete(LLMProvider):
            def extract_from_text(self, ocr_text, prompt):
                return {}
            def extract_from_image(self, images, prompt):
                return {}
            def get_model_id(self):
                return "test/model"
        return Concrete

    def test_default_values(self):
        cls = self._make_concrete()
        p = cls(model="test-model")
        assert p.model == "test-model"
        assert p.temperature == 0.0
        assert p.max_tokens == 2000
        assert p.timeout == 120.0
        assert p.max_retries == 2

    def test_custom_values(self):
        cls = self._make_concrete()
        p = cls(model="m", temperature=0.5, max_tokens=500, timeout=60, max_retries=5)
        assert p.temperature == 0.5
        assert p.max_tokens == 500
        assert p.timeout == 60.0
        assert p.max_retries == 5


class TestLLMProviderEncodeImageBase64:
    """encode_image_base64 should convert a PIL Image to a base64 string."""

    def test_returns_base64_string(self):
        img = Image.new("RGB", (10, 10), color="red")
        result = LLMProvider.encode_image_base64(img, fmt="PNG")
        assert isinstance(result, str)
        decoded = base64.b64decode(result)
        assert len(decoded) > 0

    def test_roundtrip(self):
        img = Image.new("RGB", (5, 5), color="blue")
        b64 = LLMProvider.encode_image_base64(img, fmt="PNG")
        decoded = base64.b64decode(b64)
        restored = Image.open(io.BytesIO(decoded))
        assert restored.size == (5, 5)


# =========================================================================
# Spec: _strip_json_fencing
# =========================================================================


class TestStripJsonFencingShouldRemoveFences:
    """Given text wrapped in markdown code fences, should return the inner JSON."""

    def test_json_fence(self):
        raw = '```json\n{"key": "value"}\n```'
        assert _strip_json_fencing(raw) == '{"key": "value"}'

    def test_plain_fence(self):
        raw = '```\n{"key": "value"}\n```'
        assert _strip_json_fencing(raw) == '{"key": "value"}'

    def test_fence_with_whitespace(self):
        raw = '  ```json\n{"key": "value"}\n```  '
        assert _strip_json_fencing(raw) == '{"key": "value"}'

    def test_multiline_json(self):
        raw = '```json\n{\n  "a": 1,\n  "b": 2\n}\n```'
        result = _strip_json_fencing(raw)
        assert '"a": 1' in result
        assert '"b": 2' in result


class TestStripJsonFencingShouldPassthroughUnfenced:
    """Given text without fences, should return it stripped."""

    def test_plain_json(self):
        raw = '{"key": "value"}'
        assert _strip_json_fencing(raw) == '{"key": "value"}'

    def test_with_surrounding_whitespace(self):
        raw = '  {"key": "value"}  '
        assert _strip_json_fencing(raw) == '{"key": "value"}'

    def test_empty_string(self):
        assert _strip_json_fencing("") == ""


# =========================================================================
# Spec: OpenAIProvider
# =========================================================================


class TestOpenAIProviderShouldRequireApiKey:
    """Given no OPENAI_API_KEY in env, constructing OpenAIProvider should raise."""

    def test_missing_key_raises(self):
        mock_openai = _mock_openai_module()
        env = {k: v for k, v in os.environ.items() if k != "OPENAI_API_KEY"}
        with patch.dict(sys.modules, {"openai": mock_openai}):
            from src.llm.openai_provider import OpenAIProvider
            with patch.dict(os.environ, env, clear=True):
                with pytest.raises(ValueError, match="OPENAI_API_KEY"):
                    OpenAIProvider(model="gpt-4o")


class TestOpenAIProviderShouldReturnModelId:
    """get_model_id should return 'openai/{model}'."""

    def test_model_id_format(self):
        mock_openai = _mock_openai_module()
        with patch.dict(sys.modules, {"openai": mock_openai}):
            from src.llm.openai_provider import OpenAIProvider
            with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
                p = OpenAIProvider(model="gpt-4o")
                assert p.get_model_id() == "openai/gpt-4o"

    def test_model_id_mini(self):
        mock_openai = _mock_openai_module()
        with patch.dict(sys.modules, {"openai": mock_openai}):
            from src.llm.openai_provider import OpenAIProvider
            with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
                p = OpenAIProvider(model="gpt-4o-mini")
                assert p.get_model_id() == "openai/gpt-4o-mini"


class TestOpenAIProviderShouldStoreVisionDetail:
    def test_default_vision_detail(self):
        mock_openai = _mock_openai_module()
        with patch.dict(sys.modules, {"openai": mock_openai}):
            from src.llm.openai_provider import OpenAIProvider
            with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
                p = OpenAIProvider(model="gpt-4o")
                assert p.vision_detail == "high"

    def test_custom_vision_detail(self):
        mock_openai = _mock_openai_module()
        with patch.dict(sys.modules, {"openai": mock_openai}):
            from src.llm.openai_provider import OpenAIProvider
            with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
                p = OpenAIProvider(model="gpt-4o", vision_detail="low")
                assert p.vision_detail == "low"


class TestOpenAIProviderShouldBeAnLLMProvider:
    def test_isinstance(self):
        mock_openai = _mock_openai_module()
        with patch.dict(sys.modules, {"openai": mock_openai}):
            from src.llm.openai_provider import OpenAIProvider
            with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
                p = OpenAIProvider(model="gpt-4o")
                assert isinstance(p, LLMProvider)


# =========================================================================
# Spec: AnthropicProvider
# =========================================================================


class TestAnthropicProviderShouldRequireApiKey:
    """Given no ANTHROPIC_API_KEY in env, constructing AnthropicProvider should raise."""

    def test_missing_key_raises(self):
        mock_anthropic = _mock_anthropic_module()
        env = {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}
        with patch.dict(sys.modules, {"anthropic": mock_anthropic}):
            from src.llm.anthropic_provider import AnthropicProvider
            with patch.dict(os.environ, env, clear=True):
                with pytest.raises(ValueError, match="ANTHROPIC_API_KEY"):
                    AnthropicProvider(model="claude-3-5-sonnet")


class TestAnthropicProviderShouldReturnModelId:
    def test_model_id_format(self):
        mock_anthropic = _mock_anthropic_module()
        with patch.dict(sys.modules, {"anthropic": mock_anthropic}):
            from src.llm.anthropic_provider import AnthropicProvider
            with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
                p = AnthropicProvider(model="claude-3-5-sonnet")
                assert p.get_model_id() == "anthropic/claude-3-5-sonnet"


class TestAnthropicProviderShouldBeAnLLMProvider:
    def test_isinstance(self):
        mock_anthropic = _mock_anthropic_module()
        with patch.dict(sys.modules, {"anthropic": mock_anthropic}):
            from src.llm.anthropic_provider import AnthropicProvider
            with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
                p = AnthropicProvider(model="claude-3-5-sonnet")
                assert isinstance(p, LLMProvider)


# =========================================================================
# Spec: registry — get_provider
# =========================================================================


class TestGetProviderShouldInstantiateCorrectClass:
    """Given a config with a known provider, get_provider should return
    the correct LLMProvider subclass."""

    def test_openai(self):
        mock_openai = _mock_openai_module()
        with patch.dict(sys.modules, {"openai": mock_openai}):
            with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
                config = {"llm": {"provider": "openai", "model": "gpt-4o"}}
                p = get_provider(config)
                assert p.get_model_id() == "openai/gpt-4o"

    def test_anthropic(self):
        mock_anthropic = _mock_anthropic_module()
        with patch.dict(sys.modules, {"anthropic": mock_anthropic}):
            with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
                config = {"llm": {"provider": "anthropic", "model": "claude-3-5-sonnet"}}
                p = get_provider(config)
                assert p.get_model_id() == "anthropic/claude-3-5-sonnet"


class TestGetProviderShouldPassConfig:
    """get_provider should forward temperature, max_tokens, etc. from config."""

    def test_passes_temperature(self):
        mock_openai = _mock_openai_module()
        with patch.dict(sys.modules, {"openai": mock_openai}):
            with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
                config = {"llm": {"provider": "openai", "model": "gpt-4o", "temperature": 0.7}}
                p = get_provider(config)
                assert p.temperature == 0.7

    def test_passes_max_tokens(self):
        mock_openai = _mock_openai_module()
        with patch.dict(sys.modules, {"openai": mock_openai}):
            with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
                config = {"llm": {"provider": "openai", "model": "gpt-4o", "max_tokens": 500}}
                p = get_provider(config)
                assert p.max_tokens == 500


class TestGetProviderShouldRaiseOnUnknown:
    """Given an unknown provider name, get_provider should raise ValueError."""

    def test_unknown_provider(self):
        config = {"llm": {"provider": "unknown_llm", "model": "x"}}
        with pytest.raises(ValueError, match="Unknown LLM provider"):
            get_provider(config)

    def test_error_lists_available(self):
        config = {"llm": {"provider": "bad", "model": "x"}}
        with pytest.raises(ValueError) as exc_info:
            get_provider(config)
        msg = str(exc_info.value)
        assert "anthropic" in msg
        assert "openai" in msg


class TestGetProviderShouldHandleMissingConfig:
    def test_empty_provider_raises(self):
        config = {"llm": {}}
        with pytest.raises(ValueError, match="Unknown LLM provider"):
            get_provider(config)

    def test_no_llm_key_raises(self):
        config = {}
        with pytest.raises(ValueError, match="Unknown LLM provider"):
            get_provider(config)


# =========================================================================
# Spec: _import_class
# =========================================================================


class TestImportClassShouldLoadModule:
    """_import_class should dynamically import a class from a dotted path."""

    def test_imports_openai_provider(self):
        cls = _import_class("src.llm.openai_provider.OpenAIProvider")
        from src.llm.openai_provider import OpenAIProvider
        assert cls is OpenAIProvider

    def test_imports_anthropic_provider(self):
        cls = _import_class("src.llm.anthropic_provider.AnthropicProvider")
        from src.llm.anthropic_provider import AnthropicProvider
        assert cls is AnthropicProvider
