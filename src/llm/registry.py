"""Provider registry — maps config strings to LLM provider classes.

Adding a new provider requires only a new module and one entry in
``_PROVIDERS``.
"""

from __future__ import annotations

from typing import Type

from .base import LLMProvider

# Lazy imports are used inside the factory to avoid importing SDK
# packages (openai, anthropic) unless the provider is actually requested.

_PROVIDERS: dict[str, str] = {
    "openai": "src.llm.openai_provider.OpenAIProvider",
    "anthropic": "src.llm.anthropic_provider.AnthropicProvider",
}


def _import_class(dotted_path: str) -> Type[LLMProvider]:
    """Import a class from a dotted module path."""
    module_path, class_name = dotted_path.rsplit(".", 1)
    import importlib

    module = importlib.import_module(module_path)
    return getattr(module, class_name)


def get_provider(config: dict) -> LLMProvider:
    """Instantiate an LLM provider from a pipeline config dict.

    Reads ``config["llm"]["provider"]`` to select the class, then passes
    ``model``, ``temperature``, and ``max_tokens`` from the same section
    to the constructor.

    Args:
        config: The full pipeline config (as returned by ``load_config``).

    Returns:
        An instantiated :class:`LLMProvider`.

    Raises:
        ValueError: If the provider string is not in the registry.
    """
    llm_cfg = config.get("llm", {})
    provider_name = llm_cfg.get("provider", "")

    if provider_name not in _PROVIDERS:
        available = ", ".join(sorted(_PROVIDERS))
        raise ValueError(
            f"Unknown LLM provider '{provider_name}'. "
            f"Available providers: {available}"
        )

    cls = _import_class(_PROVIDERS[provider_name])

    return cls(
        model=llm_cfg.get("model", ""),
        temperature=llm_cfg.get("temperature", 0.0),
        max_tokens=llm_cfg.get("max_tokens", 2000),
    )
