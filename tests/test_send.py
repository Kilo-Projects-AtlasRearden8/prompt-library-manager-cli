"""Tests for the send module without hitting the network."""

from __future__ import annotations

from pathlib import Path

import pytest
import urllib.error

from prompt_lib.config import Config
from prompt_lib.send import SendError, SendResult, post_json, send_prompt


def test_post_json_success(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list = []

    class FakeResp:
        def __init__(self, body: str) -> None:
            self._body = body.encode()

        def read(self) -> bytes:
            return self._body

        def __enter__(self) -> "FakeResp":
            return self

        def __exit__(self, *args) -> None:
            return None

    def fake_urlopen(request, timeout=None) -> FakeResp:
        calls.append((request.full_url, request.data, dict(request.header_items())))
        return FakeResp('{"choices": [{"message": {"content": "Hello, Dylan!"}}]}')

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)

    result = post_json("http://example.com/v1/chat/completions", {"m": 1}, {}, 5.0)
    assert result == {"choices": [{"message": {"content": "Hello, Dylan!"}}]}
    assert calls[0][0] == "http://example.com/v1/chat/completions"
    assert b'"m": 1' in calls[0][1]


def test_post_json_http_error(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeHTTPError(urllib.error.HTTPError):
        def __init__(self) -> None:
            self.code = 401

        def read(self) -> bytes:
            return b'{"error": "bad key"}'

    def fake_urlopen(request, timeout=None):
        raise FakeHTTPError()

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    with pytest.raises(SendError, match="HTTP 401"):
        post_json("http://example.com/v1/chat/completions", {}, {}, 5.0)


def test_send_prompt_returns_text(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_post(url, payload, headers, timeout):
        assert payload["model"] == "llama3"
        assert payload["messages"][0]["content"] == "filled prompt"
        assert "Authorization" not in headers
        return {"choices": [{"message": {"content": "model reply"}}]}

    monkeypatch.setattr("prompt_lib.send.post_json", fake_post)
    result = send_prompt("filled prompt", Config(endpoint="http://x", model="llama3", api_key=None, library_dir=Path("/tmp"), request_timeout=10))
    assert isinstance(result, SendResult)
    assert result.text == "model reply"
    assert result.model == "llama3"


def test_send_prompt_no_choices_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("prompt_lib.send.post_json", lambda *a, **k: {"choices": []})
    with pytest.raises(SendError, match="no choices"):
        send_prompt("x", Config(endpoint="http://x", model="m", api_key=None, library_dir=Path("/tmp"), request_timeout=10))
