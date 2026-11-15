"""Tests for the capture-try-example CI script."""

import importlib.util
from pathlib import Path

_SCRIPT = Path(__file__).parent.parent / ".github" / "scripts" / "capture_try_example.py"


def _load_script():
    """Import the capture script as a module."""
    spec = importlib.util.spec_from_file_location("capture_try_example", _SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_build_issue_body_includes_problems_and_url() -> None:
    """Test build_issue_body lists every problem and the page URL."""
    module = _load_script()
    body = module.build_issue_body(
        "https://example.com/api/page.html",
        ["The render canvas is blank", "HTTP 404 loading notebook"],
        "https://github.com/tkoyama010/pyvista-js/actions/runs/1",
    )
    assert "https://example.com/api/page.html" in body
    assert "- The render canvas is blank" in body
    assert "- HTTP 404 loading notebook" in body


def test_build_issue_body_without_problems() -> None:
    """Test build_issue_body falls back to a placeholder when empty."""
    module = _load_script()
    body = module.build_issue_body("https://example.com/", [], "run-url")
    assert "Unknown problem." in body


def test_min_nonblank_pixels_threshold_is_positive() -> None:
    """Test the blank-canvas threshold requires at least some real pixels."""
    module = _load_script()
    assert module.MIN_NONBLANK_PIXELS > 0
