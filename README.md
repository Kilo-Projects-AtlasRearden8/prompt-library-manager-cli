# Prompt Library Manager CLI

A friendly, local-first command-line tool for saving, tagging, searching,
filling in, exporting, and sending reusable AI prompts. Prompts live as plain
Markdown files with YAML frontmatter on your own computer — no cloud account,
no API key required unless you want to send prompts to a model.

Built and published by **Asdale Dynamics, LLC** (Indiana, formed October 2026),
the small business behind *The Massive AI Manual* and
[dylanasdale.github.io](https://dylanasdale.github.io). Plain English, step by
step, never condescending — written for anyone who wants to keep a personal
library of AI prompts that actually works offline.

## What it does

- **Save** prompts as local Markdown/YAML files (`prompt-lib save`)
- **Tag** prompts and filter by tag (`--tag`, `prompt-lib tags`)
- **Search** by name or body text (`prompt-lib search`)
- **Fill in** `{{variables}}` in your prompts (`prompt-lib fill`)
- **Export** your whole library to JSON or Markdown (`prompt-lib export`)
- **Send** a filled prompt to an OpenAI-compatible endpoint, default Ollama
  running locally (`prompt-lib send`)

Everything is stored locally by default in `~/.prompt-library`. Nothing is
uploaded anywhere unless you explicitly point `prompt-lib send` at an endpoint.

## Install

Copy this folder (or clone the repository), then install it:

```bash
cd prompt-library-manager-cli
pip install -e .
```

To run the tests, also install pytest:

```bash
pip install pytest
```

No API keys or network access are required to install, run, or test the tool.
Network is only used when you explicitly run `prompt-lib send` against an
endpoint.

Or just run from source:

```bash
python3 -m prompt_lib.cli --help
```

## Quick start

Initialize the library (default `~/.prompt-library`):

```bash
prompt-lib init
```

Save a prompt from a file:

```bash
prompt-lib save "blog-intro" --file my-prompt.md --tag writing --tag blog
```

Save a prompt from stdin:

```bash
echo "Write a {{tone}} email to {{name}} about {{topic}}." \
  | prompt-lib save "email-draft" --tag email
```

List your prompts:

```bash
prompt-lib list
```

Search:

```bash
prompt-lib search email --tag writing
```

Fill in variables:

```bash
prompt-lib fill "email-draft" --var tone=friendly --var name=Dylan --var topic="the new book"
```

Missing variables produce a clear error; use `--allow-missing` to leave them
as-is.

Export your library:

```bash
prompt-lib export --format json --out my-prompts.json
prompt-lib export --format markdown --out my-prompts.md
```

Send a prompt to a local model (Ollama default):

```bash
prompt-lib send "email-draft" --var tone=friendly --var name=Dylan --var topic="the new book"
```

This fills `{{variables}}` first, then POSTs to your endpoint. The default is
Ollama at `http://localhost:11434`. If Ollama isn't running, you'll get a clear
"cannot reach endpoint" error — nothing is sent and nothing is stored outside
your library.

Point at a different OpenAI-compatible endpoint:

```bash
prompt-lib send "email-draft" --endpoint http://localhost:11434 --model llama3
```

Configuration comes from environment variables:

| Variable | Default | Meaning |
|---|---|---|
| `PROMPT_LIB_DIR` | `~/.prompt-library` | Prompt library folder |
| `PROMPT_LIB_ENDPOINT` | `http://localhost:11434` | LLM API base URL |
| `PROMPT_LIB_MODEL` | `llama3` | Model to use with `send` |
| `PROMPT_LIB_API_KEY` | *(none)* | Bearer token, if your endpoint needs one |

## Prompt file format

Each prompt is one Markdown file with YAML frontmatter:

```markdown
---
name: email-draft
tags: [email, writing]
variables: [tone, name, topic]
created: 2026-10-27T08:00:00Z
updated: 2026-10-27T08:00:00Z
---
Write a {{tone}} email to {{name}} about {{topic}}.
```

`{{variable}}` placeholders anywhere in the body get filled in with
`prompt-lib fill` or `prompt-lib send --var key=value`.

## Tests

This project uses pytest and needs no API keys or network access to test:

```bash
pytest
```

## Troubleshooting

- **"cannot reach endpoint"** — `prompt-lib send` defaults to Ollama at
  `http://localhost:11434`. Start Ollama (or set `--endpoint` /
  `PROMPT_LIB_ENDPOINT` to another OpenAI-compatible server).
- **Prompt not found** — names must match exactly; use `prompt-lib list` to
  see saved names.
- **Missing variables** — `fill` and `send` error when a `{{variable}}` has no
  value. Add `--var key=value` or pass `--allow-missing` to leave it as-is.

## License

MIT. Copyright (c) 2026 Asdale Dynamics, LLC.

## About Asdale Dynamics, LLC

Asdale Dynamics, LLC is an Indiana LLC founded by Dylan Asdale, a registered
nurse turned AI author and founder of ASDALE DYNAMICS, LLC. His book *The
Massive AI Manual* and hub site dylanasdale.github.io explain AI "like a
friend would": plain English, step by step, never condescending. The LLC
publishes beginner-friendly AI education, books, guides, and practical tools
like this one — local-first, tested, and free of secrets or personal data.
