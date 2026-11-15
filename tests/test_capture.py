"""Tests for the capture module backing ``capture-api-example``."""

from unittest.mock import MagicMock

import pyvista_js._capture as capture
from pyvista_js._capture import (
    MIN_DISTINCT_CANVAS_COLORS,
    _build_issue_body,
    _on_console,
    _on_response,
    _open_bug_report,
    run_capture,
)


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
