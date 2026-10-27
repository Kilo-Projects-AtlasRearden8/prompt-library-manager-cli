"""Tests for JSON and Markdown export."""

from __future__ import annotations

import json
from pathlib import Path

from prompt_lib.export import export_json, export_markdown
from prompt_lib.store import Prompt, PromptStore


def test_export_json(tmp_path: Path) -> None:
    store = PromptStore(tmp_path)
    store.save(Prompt(name="a", body="body {{x}}", tags=["t"], variables=["x"]))
    out = tmp_path / "out.json"
    count = export_json(store, out)
    assert count == 1
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data[0]["name"] == "a"
    assert data[0]["body"] == "body {{x}}\n"
    assert data[0]["tags"] == ["t"]


def test_export_markdown(tmp_path: Path) -> None:
    store = PromptStore(tmp_path)
    store.save(Prompt(name="a", body="hello {{x}}", tags=["t", "w"], variables=["x"]))
    out = tmp_path / "out.md"
    count = export_markdown(store, out)
    assert count == 1
    text = out.read_text(encoding="utf-8")
    assert "# Prompt Library Export" in text
    assert "## a" in text
    assert "Tags: t, w" in text
    assert "Variables: x" in text
    assert "```markdown" in text
    assert "hello {{x}}" in text
