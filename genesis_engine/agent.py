from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Iterator, List

from genesis_engine.config import GenesisConfig


@dataclass
class Message:
    role: str   # "system" | "user" | "assistant"
    content: str


# Maps provider name → environment variable holding the API key
_PROVIDER_ENV: dict[str, str] = {
    "deepseek":          "DEEPSEEK_API_KEY",
    "deepseek-reasoner": "DEEPSEEK_API_KEY",
    "gpt-4":             "OPENAI_API_KEY",
    "gpt-4o":            "OPENAI_API_KEY",
    "openai":            "OPENAI_API_KEY",
    "gemini":            "GEMINI_API_KEY",
}

# OpenAI-compatible base URLs for non-OpenAI providers
_PROVIDER_BASE_URL: dict[str, str] = {
    "deepseek":          "https://api.deepseek.com",
    "deepseek-reasoner": "https://api.deepseek.com",
    "gemini":            "https://generativelanguage.googleapis.com/v1beta/openai/",
}

# Default model identifiers per provider
_PROVIDER_MODEL: dict[str, str] = {
    "deepseek":          "deepseek-chat",
    "deepseek-reasoner": "deepseek-reasoner",
    "gpt-4":             "gpt-4",
    "gpt-4o":            "gpt-4o",
    "openai":            "gpt-4o",
    "gemini":            "gemini-2.0-flash",
}


class AgentConnector:
    """Unified LLM client with provider routing from GenesisConfig.

    Supports DeepSeek, OpenAI (GPT), and Gemini. All use the openai SDK —
    DeepSeek and Gemini expose OpenAI-compatible endpoints. API keys are
    read exclusively from environment variables; never from config files.

    Usage:
        connector = AgentConnector(config)
        response = connector.chat(messages, task="business")
    """

    def __init__(self, config: GenesisConfig) -> None:
        self._config = config

    def _resolve_provider(self, task: str) -> str:
        routing = self._config.llm_routing
        return getattr(routing, task, routing.default)

    def _api_key(self, provider: str) -> str:
        env_var = _PROVIDER_ENV.get(provider)
        if not env_var:
            raise ValueError(
                f"Unknown provider '{provider}'. "
                f"Supported: {', '.join(_PROVIDER_ENV)}"
            )
        key = os.environ.get(env_var)
        if not key:
            raise EnvironmentError(
                f"API key not set. Export {env_var} before running Genesis Engine.\n"
                f"  export {env_var}=<your-key>"
            )
        return key

    def _build_client(self, provider: str):
        from openai import OpenAI
        kwargs: dict = {"api_key": self._api_key(provider)}
        if provider in _PROVIDER_BASE_URL:
            kwargs["base_url"] = _PROVIDER_BASE_URL[provider]
        return OpenAI(**kwargs)

    def chat(self, messages: List[Message], task: str = "default") -> str:
        """Send messages to the appropriate LLM and return the response text."""
        provider = self._resolve_provider(task)
        client = self._build_client(provider)
        model = _PROVIDER_MODEL.get(provider, provider)

        response = client.chat.completions.create(
            model=model,
            messages=[{"role": m.role, "content": m.content} for m in messages],
        )
        return response.choices[0].message.content

    def stream(self, messages: List[Message], task: str = "default") -> Iterator[str]:
        """Stream the response token by token."""
        provider = self._resolve_provider(task)
        client = self._build_client(provider)
        model = _PROVIDER_MODEL.get(provider, provider)

        with client.chat.completions.create(
            model=model,
            messages=[{"role": m.role, "content": m.content} for m in messages],
            stream=True,
        ) as stream:
            for chunk in stream:
                delta = chunk.choices[0].delta.content
                if delta:
                    yield delta
