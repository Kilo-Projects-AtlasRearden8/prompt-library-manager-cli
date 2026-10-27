"""Tests for the CLI using typer's CliRunner. No network, no keys."""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from prompt_lib.cli import app

runner = CliRunner()


def _run(args, tmp_path: Path):
    return runner.invoke(app, args, env={"PROMPT_LIB_DIR": str(tmp_path)})


def test_version(tmp_path: Path) -> None:
    result = _run(["version"], tmp_path)
    assert result.exit_code == 0
    assert "prompt-library-manager" in result.output


def test_init(tmp_path: Path) -> None:
    result = _run(["init"], tmp_path)
    assert result.exit_code == 0
    assert tmp_path.exists()


def test_save_list_fill(tmp_path: Path) -> None:
    result = _run(
        ["save", "greeting", "--body", "Hi {{name}}!", "--tag", "hello"],
        tmp_path,
    )
    assert result.exit_code == 0, result.output

    result = _run(["list"], tmp_path)
    assert result.exit_code == 0
    assert "greeting" in result.output
    assert "hello" in result.output

    result = _run(["fill", "greeting", "--var", "name=Dylan"], tmp_path)
    assert result.exit_code == 0
    assert result.output.strip() == "Hi Dylan!"


def test_fill_missing_variable_errors(tmp_path: Path) -> None:
    _run(["save", "greeting", "--body", "Hi {{name}}!"], tmp_path)
    result = _run(["fill", "greeting"], tmp_path)
    assert result.exit_code != 0
    assert "missing" in result.output.lower()


def test_fill_from_file(tmp_path: Path) -> None:
    body_file = tmp_path / "prompt.md"
    body_file.write_text("Read {{book}} today.", encoding="utf-8")
    result = _run(["save", "book-tip", "--file", str(body_file)], tmp_path)
    assert result.exit_code == 0
    result = _run(["fill", "book-tip", "--var", "book=The Massive AI Manual"], tmp_path)
    assert result.exit_code == 0
    assert "The Massive AI Manual" in result.output


def test_search_and_tags(tmp_path: Path) -> None:
    _run(["save", "work-email", "--body", "email body", "--tag", "work"], tmp_path)
    _run(["save", "cake", "--body", "bake cake", "--tag", "cooking"], tmp_path)

    result = _run(["search", "email"], tmp_path)
    assert result.exit_code == 0
    assert "work-email" in result.output

    result = _run(["search", "", "--tag", "cooking"], tmp_path)
    assert result.exit_code == 0
    assert "cake" in result.output
    assert "work-email" not in result.output

    result = _run(["tags"], tmp_path)
    assert result.exit_code == 0
    assert "work" in result.output
    assert "cooking" in result.output


def test_export_json_and_markdown(tmp_path: Path) -> None:
    _run(["save", "p1", "--body", "one {{x}}", "--tag", "t"], tmp_path)

    out_json = tmp_path / "e.json"
    result = _run(["export", "--format", "json", "--out", str(out_json)], tmp_path)
    assert result.exit_code == 0
    assert out_json.exists()

    out_md = tmp_path / "e.md"
    result = _run(["export", "--format", "markdown", "--out", str(out_md)], tmp_path)
    assert result.exit_code == 0
    text = out_md.read_text(encoding="utf-8")
    assert "## p1" in text


def test_send_uses_mocked_endpoint(tmp_path: Path, monkeypatch) -> None:
    _run(["save", "prompt", "--body", "Say {{word}}."], tmp_path)

    def fake_send(prompt_text, config=None, **kwargs):
        from prompt_lib.send import SendResult

        assert prompt_text.strip() == "Say hello."
        return SendResult(text="model says hi", model="llama3", endpoint="http://x")

    import prompt_lib.cli as cli_mod

    monkeypatch.setattr(cli_mod, "send_prompt", fake_send)
    result = _run(["send", "prompt", "--var", "word=hello"], tmp_path)
    assert result.exit_code == 0
    assert "model says hi" in result.output


def test_bad_format_errors(tmp_path: Path) -> None:
    result = _run(["export", "--format", "xml"], tmp_path)
    assert result.exit_code != 0
