"""Tests for search by text and tag."""

from __future__ import annotations

from prompt_lib.search import search
from prompt_lib.store import Prompt, PromptStore


def _mk(name: str, body: str, tags: list[str]) -> Prompt:
    return Prompt(name=name, body=body, tags=tags)


def test_search_by_text(store: PromptStore) -> None:
    store.save(_mk("email", "Write an email to the boss.", ["work"]))
    store.save(_mk("recipe", "Bake a chocolate cake.", ["cooking"]))
    results = search(store, "email")
    assert [p.name for p in results] == ["email"]


def test_search_case_insensitive(store: PromptStore) -> None:
    store.save(_mk("Email Draft", "hello world", []))
    assert [p.name for p in search(store, "EMAIL")] == ["Email Draft"]


def test_search_by_tag(store: PromptStore) -> None:
    store.save(_mk("one", "alpha", ["work", "writing"]))
    store.save(_mk("two", "beta", ["cooking"]))
    results = search(store, tag="writing")
    assert [p.name for p in results] == ["one"]


def test_search_text_and_tag(store: PromptStore) -> None:
    store.save(_mk("work-email", "email to boss", ["work"]))
    store.save(_mk("work-note", "note about the project", ["work"]))
    store.save(_mk("personal-email", "email to mom", ["personal"]))
    results = search(store, "email", tag="work")
    assert [p.name for p in results] == ["work-email"]


def test_search_no_match(store: PromptStore) -> None:
    store.save(_mk("a", "aaa", []))
    assert search(store, "zzz") == []
    assert search(store, tag="zzz") == []
