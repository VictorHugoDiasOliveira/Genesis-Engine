from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class LLMRouting:
    """Per-task LLM provider routing."""
    default: str = "deepseek"
    business: str = "gpt-4"
    code: str = "deepseek"
    analysis: str = "gemini"


@dataclass
class GenesisConfig:
    """Runtime configuration for a Genesis Engine instance or connected project."""

    project: str = "genesis-engine"
    # "local"  → use local knowledge/ directory and disk-cached embeddings (prototype mode)
    # "hosted" → connect to a remote Genesis Engine API (Phase 1+)
    mode: str = "local"
    genesis_engine_url: Optional[str] = None
    api_key: Optional[str] = None
    knowledge_dir: str = "knowledge"
    llm_routing: LLMRouting = field(default_factory=LLMRouting)

    @property
    def is_local(self) -> bool:
        return self.mode == "local"

    @property
    def is_hosted(self) -> bool:
        return self.mode == "hosted"


def load_config(config_path: str | Path = "genesis.yaml") -> GenesisConfig:
    """Load config from genesis.yaml, falling back to defaults if not found."""
    path = Path(config_path)
    if not path.exists():
        return GenesisConfig()

    try:
        import yaml
        data: dict = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except ImportError:
        import json
        data = json.loads(path.read_text(encoding="utf-8"))

    routing_data = data.pop("llm_routing", {})
    routing = LLMRouting(
        **{k: v for k, v in routing_data.items() if k in LLMRouting.__dataclass_fields__}
    )

    valid = set(GenesisConfig.__dataclass_fields__) - {"llm_routing"}
    return GenesisConfig(
        **{k: v for k, v in data.items() if k in valid},
        llm_routing=routing,
    )
