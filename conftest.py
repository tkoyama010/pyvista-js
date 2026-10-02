"""Pytest configuration shared by the tests and the doctests in ``src/``."""

import webbrowser

import pytest


@pytest.fixture(autouse=True)
def _no_browser_windows(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep ``plotter.show()`` from opening real browser windows."""
    monkeypatch.setattr(webbrowser, "open", lambda *_args, **_kwargs: True)
