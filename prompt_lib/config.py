"""Configuration for the prompt library.

Reads from environment variables and an optional JSON config file. No secrets
are stored by default; an API key may be supplied via PROMPT_LIB_API_KEY for
OpenAI-compatible endpoints that require one.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path

CONFIG_DIR = Path(os.environ.get("PROMPT_LIB_CONFIG_DIR", Path.home() / ".config" / "prompt-library"))
CONFIG_FILE = CONFIG_DIR / "config.json"
DEFAULT_LIBRARY_DIR = Path.home() / ".prompt-library"
DEFAULT_ENDPOINT = "http://localhost:11434"
DEFAULT_MODEL = "llama3"


@dataclass
class Config:
    library_dir: Path
    endpoint: str
    model: str
    api_key: str | None
    request_timeout: float

    @classmethod
    def load(cls) -> "Config":
        data: dict = {}
        if CONFIG_FILE.exists():
            try:
                data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                data = {}

        library_dir = Path(
            os.environ.get("PROMPT_LIB_DIR")
            or data.get("library_dir")
            or str(DEFAULT_LIBRARY_DIR)
        )
        endpoint = (
            os.environ.get("PROMPT_LIB_ENDPOINT")
            or data.get("endpoint")
            or DEFAULT_ENDPOINT
        ).rstrip("/")
        model = os.environ.get("PROMPT_LIB_MODEL") or data.get("model") or DEFAULT_MODEL
        api_key = os.environ.get("PROMPT_LIB_API_KEY") or data.get("api_key") or None
        try:
            request_timeout = float(
                os.environ.get("PROMPT_LIB_TIMEOUT")
                or data.get("request_timeout")
                or 60
            )
        except (TypeError, ValueError):
            request_timeout = 60.0

        return cls(
            library_dir=library_dir,
            endpoint=endpoint,
            model=model,
            api_key=api_key,
            request_timeout=request_timeout,
        )

    def save(self) -> None:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        payload = {
            "library_dir": str(self.library_dir),
            "endpoint": self.endpoint,
            "model": self.model,
            "request_timeout": self.request_timeout,
        }
        if self.api_key:
            payload["api_key"] = self.api_key
        CONFIG_FILE.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
