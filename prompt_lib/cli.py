"""Command-line interface for the Prompt Library Manager."""

from __future__ import annotations

import sys
from pathlib import Path

import typer
import yaml

from . import __version__
from .config import Config, DEFAULT_LIBRARY_DIR, DEFAULT_ENDPOINT, DEFAULT_MODEL
from .export import export_json, export_markdown
from .prompts import FillError, fill as fill_prompt, missing_variables
from .search import search as search_prompts
from .send import SendError, send_prompt
from .store import Prompt, PromptStore, StoreError, extract_variables

app = typer.Typer(
    name="prompt-lib",
    help="Save, tag, search, fill, export, and send reusable AI prompts "
    "stored as local Markdown/YAML files.",
    no_args_is_help=True,
)


def _store() -> PromptStore:
    return PromptStore(Config.load().library_dir)


def _read_body(*, file: Path | None, body: str | None) -> str:
    if file is not None:
        return file.read_text(encoding="utf-8")
    if body is not None:
        return body
    if sys.stdin.isatty():
        typer.echo("Enter prompt body (Ctrl-D to finish):", err=True)
    return sys.stdin.read()


def _parse_vars(var_values: list[str]) -> dict[str, str]:
    values: dict[str, str] = {}
    for item in var_values:
        if "=" not in item:
            raise typer.BadParameter(f"--var must be key=value, got: {item}")
        key, value = item.split("=", 1)
        values[key.strip()] = value
    return values


@app.command()
def init(
    library_dir: Path = typer.Option(
        None, "--dir", help="Library directory (default ~/.prompt-library)"
    ),
) -> None:
    """Initialize the prompt library directory."""
    config = Config.load()
    target = Path(library_dir) if library_dir else config.library_dir
    target.mkdir(parents=True, exist_ok=True)
    typer.echo(f"Prompt library ready at: {target}")


@app.command(name="list")
def list_prompts() -> None:
    """List all stored prompts."""
    store = _store()
    prompts = store.list()
    if not prompts:
        typer.echo("No prompts found. Use 'prompt-lib save' to add one.")
        return
    for p in prompts:
        tags = f" [{', '.join(p.tags)}]" if p.tags else ""
        vars_ = f" ({{{', '.join(p.variables)}}})" if p.variables else ""
        typer.echo(f"- {p.name}{tags}{vars_}")


@app.command()
def save(
    name: str = typer.Argument(..., help="Prompt name"),
    file: Path | None = typer.Option(
        None, "--file", "-f", help="Markdown file to read the prompt body from"
    ),
    body: str | None = typer.Option(
        None, "--body", "-b", help="Prompt body as a string"
    ),
    tag: list[str] = typer.Option([], "--tag", "-t", help="Tag (repeatable)"),
    variable: list[str] = typer.Option(
        [], "--variable", "-v", help="Declare variable name (repeatable)"
    ),
) -> None:
    """Save a prompt to the library."""
    store = _store()
    prompt_body = _read_body(file=file, body=body)
    if not prompt_body.strip():
        typer.echo("Error: prompt body is empty", err=True)
        raise typer.Exit(code=1)
    declared = list(variable) or extract_variables(prompt_body)
    prompt = Prompt(
        name=name, body=prompt_body, tags=list(tag), variables=declared
    )
    try:
        path = store.save(prompt)
    except StoreError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=1)
    typer.echo(f"Saved: {path}")


@app.command()
def search(
    query: str = typer.Argument("", help="Text to match in name or body"),
    tag: str | None = typer.Option(None, "--tag", "-t", help="Filter by tag"),
) -> None:
    """Search prompts by text and/or tag."""
    store = _store()
    results = search_prompts(store, query or None, tag)
    if not results:
        typer.echo("No matching prompts.")
        return
    for p in results:
        tags = f" [{', '.join(p.tags)}]" if p.tags else ""
        typer.echo(f"- {p.name}{tags}")


@app.command()
def fill(
    name: str = typer.Argument(..., help="Prompt name"),
    var: list[str] = typer.Option(
        [], "--var", help="Variable as key=value (repeatable)"
    ),
    allow_missing: bool = typer.Option(
        False, "--allow-missing", help="Leave unset variables as-is instead of failing"
    ),
) -> None:
    """Fill {{variables}} in a prompt and print the result."""
    store = _store()
    prompt = store.get(name)
    if prompt is None:
        typer.echo(f"Error: prompt not found: {name}", err=True)
        raise typer.Exit(code=1)
    values = _parse_vars(var)
    missing = missing_variables(prompt.body, values)
    if missing and not allow_missing:
        typer.echo(
            f"Error: missing variables for '{name}': {', '.join(missing)}", err=True
        )
        raise typer.Exit(code=1)
    try:
        result = fill_prompt(prompt.body, values, strict=not allow_missing)
    except FillError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=1)
    typer.echo(result)


@app.command()
def export(
    format: str = typer.Option("json", "--format", "-F", help="json or markdown"),
    out: Path = typer.Option("prompts-export.json", "--out", "-o", help="Output file"),
) -> None:
    """Export all prompts to a JSON or Markdown file."""
    store = _store()
    fmt = format.lower()
    try:
        if fmt == "json":
            count = export_json(store, out)
        elif fmt == "markdown":
            count = export_markdown(store, out)
        else:
            typer.echo(f"Error: unknown format '{format}' (use json or markdown)", err=True)
            raise typer.Exit(code=1)
    except OSError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=1)
    typer.echo(f"Exported {count} prompt(s) to {out}")


@app.command()
def send(
    name: str = typer.Argument(..., help="Prompt name"),
    var: list[str] = typer.Option([], "--var", help="Variable as key=value (repeatable)"),
    endpoint: str | None = typer.Option(None, "--endpoint", help="API base URL"),
    model: str | None = typer.Option(None, "--model", help="Model name"),
    system: str | None = typer.Option(None, "--system", help="System message"),
    temperature: float | None = typer.Option(None, "--temperature", help="Sampling temperature"),
    allow_missing: bool = typer.Option(False, "--allow-missing"),
) -> None:
    """Fill a prompt and send it to an OpenAI-compatible endpoint (default Ollama)."""
    store = _store()
    prompt = store.get(name)
    if prompt is None:
        typer.echo(f"Error: prompt not found: {name}", err=True)
        raise typer.Exit(code=1)
    values = _parse_vars(var)
    missing = missing_variables(prompt.body, values)
    if missing and not allow_missing:
        typer.echo(
            f"Error: missing variables for '{name}': {', '.join(missing)}", err=True
        )
        raise typer.Exit(code=1)
    filled = fill_prompt(prompt.body, values, strict=not allow_missing)
    try:
        result = send_prompt(
            filled,
            endpoint=endpoint,
            model=model,
            system=system,
            temperature=temperature,
        )
    except SendError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=1)
    typer.echo(result.text)


@app.command()
def tags() -> None:
    """List all tags used in the library."""
    store = _store()
    found: dict[str, None] = {}
    for p in store.list():
        for t in p.tags:
            found.setdefault(t)
    if not found:
        typer.echo("No tags found.")
        return
    for tag in sorted(found, key=str.lower):
        typer.echo(f"- {tag}")


@app.command()
def version() -> None:
    """Show the version."""
    typer.echo(f"prompt-library-manager {__version__}")


if __name__ == "__main__":
    app()
