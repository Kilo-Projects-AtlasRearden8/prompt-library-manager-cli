# STATUS — Prompt Library Manager CLI

**Project:** prompt-library-manager-cli
**Published by:** Asdale Dynamics, LLC (Indiana, formed October 2026)
**Version:** 0.1.0
**License:** MIT — Copyright (c) 2026 Asdale Dynamics, LLC

## What was built

A beginner-friendly, local-first Python CLI for keeping a personal library of
reusable AI prompts. Prompts are stored as plain Markdown files with YAML
frontmatter in `~/.prompt-library` (overridable via `PROMPT_LIB_DIR`). No cloud
account, no API key, and no network access are required unless you explicitly
send a prompt to a model.

Features:
- `prompt-lib init` — initialize the library directory
- `prompt-lib save` — save a prompt from `--body`, `--file`, or stdin, with
  repeatable `--tag` and `--variable`; `{{variables}}` in the body are
  auto-detected and declared
- `prompt-lib list` — list all prompts with tags and variables
- `prompt-lib search` — search by name/body text and/or `--tag`
- `prompt-lib tags` — list all tags used in the library
- `prompt-lib fill` — fill `{{variables}}` and print the result;
  `--allow-missing` leaves unset variables as-is
- `prompt-lib export` — export the whole library to JSON or Markdown
- `prompt-lib send` — fill a prompt and POST it to an OpenAI-compatible
  chat completions endpoint (default Ollama at `http://localhost:11434`);
  `--endpoint`, `--model`, `--system`, `--temperature`, `--var` supported
- `prompt-lib version`

Configuration via environment variables: `PROMPT_LIB_DIR`,
`PROMPT_LIB_ENDPOINT` (default `http://localhost:11434`),
`PROMPT_LIB_MODEL` (default `llama3`), `PROMPT_LIB_API_KEY`,
`PROMPT_LIB_TIMEOUT`.

Tests: pytest, 31 tests, no API keys or network access required.

## How to run

```bash
# Install
cd prompt-library-manager-cli
pip install -e .
pip install pytest        # for tests

# Initialize the library (default ~/.prompt-library)
prompt-lib init

# Save a prompt
prompt-lib save "email-draft" --body "Write a {{tone}} email to {{name}} about {{topic}}." --tag email --tag writing

# List, search, fill
prompt-lib list
prompt-lib search email --tag writing
prompt-lib fill "email-draft" --var tone=friendly --var name=Dylan --var topic="the new book"

# Export
prompt-lib export --format json --out my-prompts.json
prompt-lib export --format markdown --out my-prompts.md

# Send to a local model (Ollama default)
prompt-lib send "email-draft" --var tone=friendly --var name=Dylan --var topic="the new book"

# Run tests
pytest
```

Or run from source: `python3 -m prompt_lib.cli --help`

## Verification results

- `pip install -e .` succeeds (setuptools editable build, Python 3.13).
- `pytest`: **31 passed, 0 failed** (tests/test_cli.py, test_export.py,
  test_prompts.py, test_search.py, test_send.py, test_store.py).
- End-to-end smoke test of the installed CLI: init, save, list, fill (including
  missing-variable error path), search, tags, export (JSON), and version all
  behave as documented. `send` is covered by mocked tests (no network, no keys).

## Known gaps

- `prompt-lib send` requires a running endpoint (default Ollama); offline use
  for `send` is not possible by design, and no fake/model fallback is bundled.
- No `prompt-lib delete` command yet (store supports deletion internally).
- Variables are declared from `--variable` or auto-detected on save; editing a
  prompt's variables requires re-saving the prompt.
- Prompt file names are derived from the prompt name (unsafe characters become
  `-`); renaming a prompt leaves the old file behind unless deleted manually.
- Package is published as `prompt-library-manager`; the CLI command is
  `prompt-lib`.
