"""Prompt model helpers: variable filling and validation."""

from __future__ import annotations

import re

VAR_RE = re.compile(r"{{\s*([A-Za-z_][A-Za-z0-9_]*)\s*}}")


def fill(template: str, values: dict[str, str], strict: bool = True) -> str:
    """Replace {{variable}} placeholders with values.

    Missing variables are left untouched unless strict=True, in which case a
    FillError listing the missing names is raised.
    """

    def replacer(match: re.Match) -> str:
        name = match.group(1)
        if name in values:
            return values[name]
        if strict:
            raise FillError(f"missing variable: {{{{{name}}}}}")
        return match.group(0)

    return VAR_RE.sub(replacer, template)


def missing_variables(template: str, values: dict[str, str]) -> list[str]:
    """Return {{variable}} names in template that have no value supplied."""
    missing: list[str] = []
    for match in VAR_RE.finditer(template):
        name = match.group(1)
        if name not in values and name not in missing:
            missing.append(name)
    return missing


class FillError(Exception):
    """Raised when a prompt cannot be filled because variables are missing."""
