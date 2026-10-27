"""Shared pytest fixtures."""

from __future__ import annotations

from pathlib import Path

import pytest

from prompt_lib.store import PromptStore


@pytest.fixture
def store(tmp_path: Path) -> PromptStore:
    return PromptStore(tmp_path)
