"""Export prompts to JSON or Markdown files."""

from __future__ import annotations

import json
from pathlib import Path

from .store import PromptStore


def to_json_dict(prompts: list) -> list[dict]:
    return [
        {
            "name": p.name,
            "tags": p.tags,
            "variables": p.variables,
            "created": p.created,
            "updated": p.updated,
            "body": p.body,
        }
        for p in prompts
    ]


def export_json(store: PromptStore, output: Path) -> int:
    prompts = store.list()
    output = Path(output)
    output.write_text(json.dumps(to_json_dict(prompts), indent=2) + "\n", encoding="utf-8")
    return len(prompts)


def export_markdown(store: PromptStore, output: Path) -> int:
    prompts = store.list()
    lines = ["# Prompt Library Export", "", ""]
    for prompt in prompts:
        lines.append(f"## {prompt.name}")
        if prompt.tags:
            lines.append(f"Tags: {', '.join(prompt.tags)}")
        if prompt.variables:
            lines.append(f"Variables: {', '.join(prompt.variables)}")
        if prompt.created:
            lines.append(f"Created: {prompt.created}")
        if prompt.updated:
            lines.append(f"Updated: {prompt.updated}")
        lines.append("")
        lines.append("```markdown")
        lines.append(prompt.body.rstrip())
        lines.append("```")
        lines.append("")
    Path(output).write_text("\n".join(lines) + "\n", encoding="utf-8")
    return len(prompts)
