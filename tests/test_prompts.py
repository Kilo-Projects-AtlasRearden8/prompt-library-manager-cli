"""Tests for prompt variable filling."""

from __future__ import annotations

import pytest

from prompt_lib.prompts import FillError, fill, missing_variables


def test_fill_replaces_all_variables() -> None:
    result = fill("Hi {{name}}, welcome to {{place}}.", {"name": "Dylan", "place": "Indiana"})
    assert result == "Hi Dylan, welcome to Indiana."


def test_fill_ignores_extra_values() -> None:
    assert fill("Hi {{name}}.", {"name": "Dylan", "extra": "ignored"}) == "Hi Dylan."


def test_fill_strict_raises_on_missing() -> None:
    with pytest.raises(FillError):
        fill("Hi {{name}} and {{friend}}.", {"name": "Dylan"})


def test_fill_non_strict_leaves_missing() -> None:
    result = fill("Hi {{name}} and {{friend}}.", {"name": "Dylan"}, strict=False)
    assert result == "Hi Dylan and {{friend}}."


def test_missing_variables_ordered_deduped() -> None:
    assert missing_variables("{{a}} {{b}} {{a}}", {"a": "1"}) == ["b"]
    assert missing_variables("nothing", {}) == []


def fill_handles_braces_with_spaces() -> None:
    assert fill("{{  x  }}", {"x": "v"}) == "v"
