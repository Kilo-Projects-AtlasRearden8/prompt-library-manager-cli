"""Send a filled prompt to an OpenAI-compatible endpoint (default Ollama).

Uses only the standard library (urllib) so no HTTP client dependency is
required. The endpoint base defaults to http://localhost:11434 (Ollama) and
the chat path is /v1/chat/completions, which Ollama and most OpenAI-compatible
servers support. Set PROMPT_LIB_ENDPOINT / PROMPT_LIB_MODEL / PROMPT_LIB_API_KEY
to target a different provider.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass

from .config import Config


class SendError(Exception):
    """Raised when sending a prompt to the LLM endpoint fails."""


@dataclass
class SendResult:
    text: str
    model: str
    endpoint: str


def build_messages(system: str | None, user: str) -> list[dict]:
    messages: list[dict] = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": user})
    return messages


def post_json(url: str, payload: dict, headers: dict, timeout: float) -> dict:
    """POST JSON to url and return the parsed response body.

    Exists as a standalone function so tests can monkeypatch it instead of
    hitting the network.
    """
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json", **headers},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise SendError(f"HTTP {exc.code}: {body}") from exc
    except urllib.error.URLError as exc:
        raise SendError(f"cannot reach endpoint {url}: {exc}") from exc
    try:
        return json.loads(body)
    except json.JSONDecodeError as exc:
        raise SendError(f"invalid JSON from endpoint: {body!r}") from exc


def send_prompt(
    prompt_text: str,
    config: Config | None = None,
    *,
    endpoint: str | None = None,
    model: str | None = None,
    system: str | None = None,
    api_key: str | None = None,
    temperature: float | None = None,
) -> SendResult:
    """Send prompt_text to the chat completions endpoint and return the reply."""
    config = config or Config.load()
    base = endpoint or config.endpoint
    model_name = model or config.model
    key = api_key if api_key is not None else config.api_key

    payload: dict = {
        "model": model_name,
        "messages": build_messages(system, prompt_text),
        "stream": False,
    }
    if temperature is not None:
        payload["temperature"] = temperature

    headers: dict = {}
    if key:
        headers["Authorization"] = f"Bearer {key}"

    url = f"{base}/v1/chat/completions"
    response = post_json(url, payload, headers, config.request_timeout)

    choices = response.get("choices") or []
    if not choices:
        raise SendError(f"no choices in response: {response!r}")
    message = choices[0].get("message") or {}
    text = message.get("content") or ""
    return SendResult(text=text, model=model_name, endpoint=base)
