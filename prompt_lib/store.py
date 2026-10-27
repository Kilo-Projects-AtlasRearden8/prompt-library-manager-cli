"""Storage for prompts as Markdown files with YAML frontmatter.

Each prompt lives in its own file under the library directory:

    ---                              <- YAML frontmatter (metadata)
    name: summarize-article
    tags: [writing, summary]
    variables: [article, style]
    created: 2026-10-27T08:00:00Z
    updated: 2026-10-27T08:00:00Z
    ---                              <- end of frontmatter
    # Summarize an article           <- Markdown body (may contain {{variables}})

    Summarize {{article}} in {{style}} style.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

import yaml

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


class StoreError(Exception):
    """Raised when the prompt store cannot be read or written."""


@dataclass
class Prompt:
    name: str
    body: str
    tags: list[str] = field(default_factory=list)
    variables: list[str] = field(default_factory=list)
    created: str | None = None
    updated: str | None = None
    path: Path | None = None

    def to_frontmatter(self) -> dict:
        return {
            "name": self.name,
            "tags": self.tags,
            "variables": self.variables,
            "created": self.created,
            "updated": self.updated,
        }

    @classmethod
    def from_file(cls, path: Path) -> "Prompt":
        text = path.read_text(encoding="utf-8")
        match = FRONTMATTER_RE.match(text)
        if match:
            meta = yaml.safe_load(match.group(1)) or {}
            body = text[match.end() :]
        else:
            meta = {}
            body = text
        name = meta.get("name") or path.stem
        return cls(
            name=name,
            body=body,
            tags=list(meta.get("tags") or []),
            variables=list(meta.get("variables") or []),
            created=meta.get("created"),
            updated=meta.get("updated"),
            path=path,
        )

    def to_file_text(self) -> str:
        meta = self.to_frontmatter()
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        if not self.created:
            meta["created"] = now
        meta["updated"] = now
        front = yaml.safe_dump(meta, sort_keys=False, allow_unicode=True).rstrip()
        return f"---\n{front}\n---\n{self.body.rstrip()}\n"


class PromptStore:
    """Collection of prompts stored as individual Markdown/YAML files."""

    def __init__(self, library_dir: Path) -> None:
        self.library_dir = Path(library_dir)

    def ensure_dir(self) -> None:
        self.library_dir.mkdir(parents=True, exist_ok=True)

    def _path_for(self, name: str) -> Path:
        safe = re.sub(r"[^A-Za-z0-9._-]+", "-", name.strip()).strip("-") or "prompt"
        return self.library_dir / f"{safe}.md"

    def list(self) -> list[Prompt]:
        if not self.library_dir.exists():
            return []
        prompts = []
        for path in sorted(self.library_dir.glob("*.md")):
            try:
                prompts.append(Prompt.from_file(path))
            except (OSError, yaml.YAMLError):
                continue
        return sorted(prompts, key=lambda p: p.name.lower())

    def get(self, name: str) -> Prompt | None:
        for path in self.library_dir.glob("*.md") if self.library_dir.exists() else []:
            try:
                prompt = Prompt.from_file(path)
            except (OSError, yaml.YAMLError):
                continue
            if prompt.name == name:
                return prompt
        return None

    def save(self, prompt: Prompt) -> Path:
        self.ensure_dir()
        path = self._path_for(prompt.name)
        path.write_text(prompt.to_file_text(), encoding="utf-8")
        prompt.path = path
        return path

    def delete(self, name: str) -> bool:
        prompt = self.get(name)
        if prompt is None or prompt.path is None:
            return False
        try:
            prompt.path.unlink()
        except OSError:
            return False
        return True

    def variables_used(self) -> set[str]:
        found: set[str] = set()
        for prompt in self.list():
            found.update(extract_variables(prompt.body))
        return found


def extract_variables(text: str) -> list[str]:
    """Return ordered, de-duplicated {{variable}} names found in text."""
    seen: list[str] = []
    for match in re.finditer(r"{{\s*([A-Za-z_][A-Za-z0-9_]*)\s*}}", text):
        name = match.group(1)
        if name not in seen:
            seen.append(name)
    return seen
