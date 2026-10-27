"""Search prompts by text (name/body) and/or tags."""

from __future__ import annotations

from .store import Prompt, PromptStore


def matches(prompt: Prompt, query: str) -> bool:
    """True if query appears in the prompt name or body (case-insensitive)."""
    haystack = f"{prompt.name}\n{prompt.body}".lower()
    return query.lower() in haystack


def by_tag(prompt: Prompt, tag: str) -> bool:
    """True if prompt carries the given tag (case-insensitive)."""
    return tag.lower() in {t.lower() for t in prompt.tags}


def search(store: PromptStore, query: str | None = None, tag: str | None = None) -> list[Prompt]:
    """Return prompts matching query (text) and/or tag, in store order."""
    results = []
    for prompt in store.list():
        if query is not None and not matches(prompt, query):
            continue
        if tag is not None and not by_tag(prompt, tag):
            continue
        results.append(prompt)
    return results
