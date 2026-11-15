"""Tests for the capture module backing ``capture-api-example``."""

import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import MagicMock

import pytest

import pyvista_js._capture as capture
from pyvista_js._capture import (
    MIN_DISTINCT_CANVAS_COLORS,
    _build_issue_body,
    _capture_try_example_page,
    _on_console,
    _on_response,
    _open_bug_report,
    run_capture,
)
from pyvista_js._cli import cli_main


def test_build_issue_body_includes_problems_and_url() -> None:
    """``_build_issue_body`` lists every problem and the page URL."""
    body = _build_issue_body(
        "https://example.com/api/page.html",
        ["The render canvas is blank", "HTTP 404 loading notebook"],
        "https://github.com/tkoyama010/pyvista-js/actions/runs/1",
    )
    assert "https://example.com/api/page.html" in body
    assert "- The render canvas is blank" in body
    assert "- HTTP 404 loading notebook" in body


def test_build_issue_body_without_problems() -> None:
    """``_build_issue_body`` falls back to a placeholder when there are none."""
    body = _build_issue_body("https://example.com/", [], "run-url")
    assert "Unknown problem." in body


def test_min_distinct_canvas_colors_requires_variation() -> None:
    """The blank-canvas check needs more than one distinct color."""
    assert MIN_DISTINCT_CANVAS_COLORS > 1


def test_on_response_records_http_errors_but_skips_optional_files() -> None:
    """``_on_response`` collects HTTP failures except optional artifacts."""
    failed: list[str] = []
    _on_response(failed, MagicMock(status=404, url="https://x/missing.ipynb"))
    _on_response(failed, MagicMock(status=404, url="https://x/try_examples.json"))
    _on_response(failed, MagicMock(status=200, url="https://x/ok.js"))
    assert failed == ["HTTP 404 loading missing.ipynb"]


def test_on_console_collects_errors_but_skips_noise() -> None:
    """``_on_console`` collects real errors and skips resource/theme noise."""
    errors: list[str] = []
    error = MagicMock(type="error", text="boom")
    resource = MagicMock(type="error", text="Failed to load resource: 404")
    theme = MagicMock(type="error", text="Got invalid theme mode: . Resetting to auto.")
    log = MagicMock(type="log", text="hello")
    _on_console(errors, error)
    _on_console(errors, resource)
    _on_console(errors, theme)
    _on_console(errors, log)
    assert errors == ["console.error: boom"]


def test_run_capture_clean_run_skips_issue(monkeypatch, tmp_path) -> None:
    """``run_capture`` reports success and opens no issue when clean."""
    calls: list[str] = []
    monkeypatch.setattr(
        capture,
        "_capture_try_example_page",
        lambda url, output: calls.append(url) or [],
    )
    opened: list[str] = []
    monkeypatch.setattr(
        capture,
        "_open_bug_report",
        lambda url, problems, output: opened.append(url) or True,
    )
    assert run_capture("https://example.com/", tmp_path, open_issue=True) is True
    assert calls == ["https://example.com/"]
    assert opened == []


def test_run_capture_opens_issue_on_problems(monkeypatch, tmp_path) -> None:
    """``run_capture`` opens an issue for the detected problems."""
    monkeypatch.setattr(capture, "_capture_try_example_page", lambda url, output: ["blank canvas"])
    opened: list[tuple[str, list[str]]] = []
    monkeypatch.setattr(
        capture,
        "_open_bug_report",
        lambda url, problems, output: opened.append((url, problems)) or True,
    )
    assert run_capture("https://example.com/", tmp_path, open_issue=True) is False
    assert opened == [("https://example.com/", ["blank canvas"])]


def test_open_bug_report_creates_issue(monkeypatch, tmp_path) -> None:
    """``_open_bug_report`` calls gh with the report and returns True."""
    created: dict[str, list[str]] = {}

    monkeypatch.setattr("pyvista_js._capture.shutil.which", lambda name: "/usr/bin/gh")

    def fake_run(argv, **kwargs):
        created["argv"] = argv
        return MagicMock(returncode=0, stdout="https://x/issues/1", stderr="")

    monkeypatch.setattr("pyvista_js._capture.subprocess.run", fake_run)
    assert _open_bug_report("https://example.com/", ["blank"], tmp_path) is True
    assert "issue" in " ".join(created["argv"])
    assert created["argv"][-1] == "bug"


def test_open_bug_report_failure_returns_false(monkeypatch, tmp_path) -> None:
    """``_open_bug_report`` returns False when gh exits non-zero."""
    monkeypatch.setattr("pyvista_js._capture.shutil.which", lambda name: "/usr/bin/gh")
    monkeypatch.setattr(
        "pyvista_js._capture.subprocess.run",
        lambda argv, **kwargs: MagicMock(returncode=1, stdout="", stderr="denied"),
    )
    assert _open_bug_report("https://example.com/", ["blank"], tmp_path) is False


def test_open_bug_report_without_gh_returns_false(monkeypatch, tmp_path) -> None:
    """``_open_bug_report`` returns False when the gh CLI is missing."""
    monkeypatch.setattr("pyvista_js._capture.shutil.which", lambda name: None)
    assert _open_bug_report("https://example.com/", ["blank"], tmp_path) is False


PAGE_TEMPLATE = """<!DOCTYPE html>
<html><head><style>body {{ background: #fff; }}</style></head>
<body>
<div class="try_examples_outer_container">
  <button class="try_examples_button">Try it with JupyterLite!</button>
  <div class="jupyterlite_sphinx_iframe_container">
    <iframe src="lite.html"></iframe>
  </div>
</div>
</body></html>
"""

LITE_TEMPLATE = """<!DOCTYPE html>
<html><head><style>body {{ background: #fff; }}</style></head>
<body>
<div class="lm-MenuBar"><span class="lm-MenuBar-itemLabel">File</span>
<span class="lm-MenuBar-itemLabel">Run</span></div>
<div class="lm-Menu"><span class="lm-Menu-itemLabel">Run All Cells</span></div>
<div class="jp-Notebook"><div class="jp-Cell">
  <div class="jp-OutputArea-output">
    <canvas width="60" height="40" style="width:60px;height:40px;display:block"></canvas>
  </div>
</div></div>
<script>
  // Draw a multi-color mesh stand-in when {draw} is requested.
  const canvas = document.querySelector("canvas");
  const ctx = canvas.getContext("2d");
  if ({draw}) {{
    ctx.fillStyle = "red"; ctx.fillRect(0, 0, 30, 40);
    ctx.fillStyle = "blue"; ctx.fillRect(30, 0, 30, 40);
  }} else {{
    ctx.fillStyle = "white"; ctx.fillRect(0, 0, 60, 40);
  }}
  document.title = "ready";
</script>
</body></html>
"""


def _write_fixture(tmp_path: Path, *, draw: bool, dialog: str = "") -> Path:
    """Write the fake docs page and JupyterLite frame into *tmp_path*."""
    tmp_path.joinpath("page.html").write_text(PAGE_TEMPLATE)
    lite = LITE_TEMPLATE.format(draw=str(draw).lower())
    if dialog:
        lite = lite.replace("<body>", f"<body><div class='jp-Dialog'>{dialog}</div>")
    tmp_path.joinpath("lite.html").write_text(lite)
    return tmp_path / "page.html"


@pytest.mark.playwright
def test_capture_reports_missing_widget(tmp_path: Path) -> None:
    """A page without the Try-examples button is reported as a problem."""
    page = tmp_path / "plain.html"
    page.write_text("<!DOCTYPE html><html><body>no widget</body></html>")
    out = tmp_path / "out"
    with ThreadPoolExecutor() as executor:
        problems = executor.submit(_capture_try_example_page, page.as_uri(), out).result()
    assert any("No 'Try it with JupyterLite!'" in problem for problem in problems)
    assert (out / "capture.png").exists()
    report = json.loads((out / "problems.json").read_text())
    assert report["problems"] == problems


@pytest.mark.playwright
def test_capture_reports_blank_canvas(tmp_path: Path) -> None:
    """A canvas that never renders is reported as a blank-canvas problem."""
    out = tmp_path / "out"
    with ThreadPoolExecutor() as executor:
        problems = executor.submit(
            _capture_try_example_page,
            _write_fixture(tmp_path, draw=False).as_uri(),
            out,
        ).result()
    assert any("blank" in problem for problem in problems)
    assert (out / "capture.png").exists()


@pytest.mark.playwright
def test_capture_clean_run(tmp_path: Path) -> None:
    """A drawn canvas produces no problems and a screenshot."""
    out = tmp_path / "out"
    with ThreadPoolExecutor() as executor:
        problems = executor.submit(
            _capture_try_example_page,
            _write_fixture(tmp_path, draw=True).as_uri(),
            out,
        ).result()
    assert problems == []
    assert (out / "capture.png").exists()


@pytest.mark.playwright
def test_capture_reports_file_load_error(tmp_path: Path) -> None:
    """A missing notebook is reported via the File Load Error dialog branch."""
    out = tmp_path / "out"
    out = tmp_path / "out"
    _write_fixture(tmp_path, draw=False, dialog="File Load Error for example.ipynb")
    page = tmp_path / "page.html"
    with ThreadPoolExecutor() as executor:
        problems = executor.submit(_capture_try_example_page, page.as_uri(), out).result()
    assert any("File Load Error" in problem for problem in problems)


def test_capture_command_exits_one_on_problems(monkeypatch) -> None:
    """``capture-api-example`` exits 1 when the capture reports problems."""
    monkeypatch.setattr(
        "pyvista_js._capture._capture_try_example_page",
        lambda url, output: ["blank canvas"],
    )
    with pytest.raises(SystemExit) as excinfo:
        cli_main(["capture-api-example", "https://example.com/"])
    assert excinfo.value.code == 1


def test_capture_command_succeeds_cleanly(monkeypatch) -> None:
    """``capture-api-example`` exits 0 when the capture is clean."""
    monkeypatch.setattr("pyvista_js._capture._capture_try_example_page", lambda url, output: [])
    cli_main(["capture-api-example", "https://example.com/"])
