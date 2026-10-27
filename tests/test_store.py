"""Tests for the prompt store (Markdown + YAML frontmatter files)."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from prompt_lib.store import Prompt, PromptStore, extract_variables


def _write(path: Path, name: str, body: str, tags: list[str] | None = None) -> None:
    front = {
        "name": name,
        "tags": tags or [],
        "variables": [],
        "created": "2026-10-27T08:00:00Z",
        "updated": "2026-10-27T08:00:00Z",
    }
    text = "---\n" + yaml.safe_dump(front, sort_keys=False) + "---\n" + body + "\n"
    path.write_text(text, encoding="utf-8")


def test_save_and_round_trip(store: PromptStore) -> None:
    prompt = Prompt(
        name="hello",
        body="Say {{greeting}} to {{name}}.",
        tags=["greeting"],
        variables=["greeting", "name"],
    )
    saved = store.save(prompt)
    assert saved.exists()
    loaded = store.get("hello")
    assert loaded is not None
    assert loaded.name == "hello"
    assert loaded.body == "Say {{greeting}} to {{name}}.\n"
    assert loaded.tags == ["greeting"]
    assert loaded.variables == ["greeting", "name"]
    assert loaded.created is not None
    assert loaded.updated is not None


def test_list_empty_and_sorted(store: PromptStore) -> None:
    assert store.list() == []
    _write(store.library_dir / "zeta.md", "zeta", "body z")
    _write(store.library_dir / "alpha.md", "alpha", "body a")
    _write(store.library_dir / "Mid.md", "Mid", "body m")
    names = [p.name for p in store.list()]
    assert names == ["alpha", "Mid", "zeta"]


def test_get_missing_returns_none(store: PromptStore) -> None:
    assert store.get("nope") is None


def test_delete(store: PromptStore) -> None:
    _write(store.library_dir / "tmp.md", "tmp", "body")
    assert store.get("tmp") is not None
    assert store.delete("tmp") is True
    assert store.get("tmp") is None
    assert store.delete("tmp") is False


def test_extract_variables_ordered_deduped() -> None:
    assert extract_variables("Hi {{name}}, meet {{name}} and {{friend}}") == [
        "name",
        "friend",
    ]
    assert extract_variables("no vars here") == []
    assert extract_variables("spaced {{  x  }} and {{y}}") == ["x", "y"]


def test_frontmatter_without_name_uses_stem(store: PromptStore) -> None:
    path = store.library_dir / "weird name!.md"
    path.write_text("---\ntags: []\n---\njust a body\n", encoding="utf-8")
    loaded = Prompt.from_file(path)
    assert loaded.name == "weird name!"
