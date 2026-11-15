"""Capture API documentation pages after running their JupyterLite examples.

Backs the ``pyvista-js capture-api-example`` command: opens a documentation
page, activates the embedded JupyterLite widget, runs all notebook cells,
takes a full-page screenshot, and reports the problems found (failed
notebook loads, console errors, HTTP failures, blank render canvases).
With ``--open-issue`` the command files a bug-report issue through the
``gh`` CLI.

Playwright, numpy, and pillow are optional test-only dependencies, so they
are imported lazily inside the functions that need them (see the
per-file-ignores entry for this module in ``pyproject.toml``).
"""

from __future__ import annotations

import io
import json
import logging
import os
import platform
import shutil
import subprocess
import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

    from playwright.sync_api import ConsoleMessage, Frame, Page, Response

logger = logging.getLogger(__name__)

MIN_DISTINCT_CANVAS_COLORS = 2

CANVAS_WAIT_SECONDS = 600
LITE_FRAME_WAIT_SECONDS = 120
HTTP_ERROR_MIN_STATUS = 400


def _find_lite_frame(page: Page) -> Frame | None:
    """Return the JupyterLite frame of *page*, polling until it appears.

    Parameters
    ----------
    page : playwright.sync_api.Page
        The Playwright page object.
    timeout : int
        Maximum seconds to wait. Default: 120.

    Returns
    -------
    playwright.sync_api.Frame or None
        The JupyterLite frame, or None if it never loaded.

    """
    deadline = time.monotonic() + LITE_FRAME_WAIT_SECONDS
    while time.monotonic() < deadline:
        for frame in page.frames:
            if "lite" in frame.url:
                return frame
        page.wait_for_timeout(2000)  # pragma: no cover
    return None  # pragma: no cover


def _on_response(failed_urls: list[str], response: Response) -> None:
    """Record HTTP errors, skipping optional files that may 404 by design.

    Parameters
    ----------
    failed_urls : list of str
        Collector for the failure messages.
    response : playwright.sync_api.Response
        The response to inspect.

    """
    if response.status >= HTTP_ERROR_MIN_STATUS and "try_examples.json" not in response.url:
        failed_urls.append(f"HTTP {response.status} loading {response.url.rsplit('/', 1)[-1]}")


def _on_console(js_errors: list[str], msg: ConsoleMessage) -> None:
    """Record console errors, skipping resource and theme noise.

    Parameters
    ----------
    js_errors : list of str
        Collector for the error messages.
    msg : playwright.sync_api.ConsoleMessage
        The console message to inspect.

    """
    if (
        msg.type == "error"
        and "Failed to load resource" not in msg.text
        # JupyterLite theme quirk, harmless and not our fault.
        and "Got invalid theme mode" not in msg.text
    ):
        js_errors.append(f"console.error: {msg.text}")


def _canvas_renders_mesh(lite: Frame) -> bool:
    """Report whether the example canvas shows more than a uniform color.

    Mirrors the distinct-color check used by the browser rendering tests:
    a uniform background (dark, light, or fully transparent) means nothing
    was drawn, while any rendered mesh yields multiple distinct colors.

    Parameters
    ----------
    lite : playwright.sync_api.Frame
        The JupyterLite frame.

    Returns
    -------
    bool
        True when the canvas shows more than one distinct color.

    """
    import numpy as np
    from PIL import Image

    screenshot = lite.locator(".jp-OutputArea-output canvas").first.screenshot()
    pixels = np.asarray(Image.open(io.BytesIO(screenshot)).convert("RGB"))
    colors = {tuple(color) for color in pixels.reshape(-1, 3).tolist()}
    return len(colors) >= MIN_DISTINCT_CANVAS_COLORS


def _run_try_example(lite: Frame) -> list[str]:  # pragma: no cover
    """Run all cells in the JupyterLite notebook and check the result.

    Parameters
    ----------
    lite : playwright.sync_api.Frame
        The JupyterLite frame with the example notebook.

    Returns
    -------
    list of str
        The problems found while running the example.

    """
    import playwright.sync_api

    problems: list[str] = []
    try:
        lite.wait_for_selector(".jp-Notebook .jp-Cell", timeout=180_000)
    except playwright.sync_api.Error as exc:  # pragma: no cover
        problems.append(f"Notebook UI never finished booting: {exc}")
        return problems

    # A "File Load Error" dialog means the generated example notebook is
    # missing from the deployed JupyterLite contents.
    file_load_error = lite.locator(".jp-Dialog", has_text="File Load Error")
    dialog_shown = True
    try:
        file_load_error.wait_for(timeout=5_000)
    except playwright.sync_api.Error as exc:
        logger.debug("No File Load Error dialog: %s", exc)
        dialog_shown = False
    if dialog_shown:
        problems.append(f"JupyterLite reported: {file_load_error.inner_text().strip()[:300]}")
        return problems

    lite.locator(".lm-MenuBar-itemLabel").filter(has_text="Run").first.click()
    lite.locator(".lm-Menu-itemLabel").filter(has_text="Run All Cells").first.click()

    canvas = lite.locator(".jp-OutputArea-output canvas").first
    try:
        canvas.wait_for(timeout=CANVAS_WAIT_SECONDS * 1_000)
    except playwright.sync_api.Error as exc:  # pragma: no cover
        problems.append(
            f"No render canvas appeared within {CANVAS_WAIT_SECONDS} seconds of "
            f"running all cells: {exc}",
        )
        return problems

    # Give the render loop time to draw.
    lite.wait_for_timeout(20_000)
    try:
        if not _canvas_renders_mesh(lite):
            problems.append(
                "The render canvas is blank after running all cells "
                "(the example produced no visible output).",
            )
    except playwright.sync_api.Error as exc:  # pragma: no cover
        problems.append(f"Could not inspect the render canvas: {exc}")

    return problems


def _capture_try_example_page(url: str, output: Path) -> list[str]:  # pragma: no cover
    """Open *url*, run its embedded JupyterLite example, and capture it.

    Writes ``capture.png`` and ``problems.json`` into *output*.

    This browser-automation flow is exercised by the playwright-marked
    fake-page tests, which run in a worker thread that the coverage tracer
    does not follow; the function is excluded so the CI patch report does
    not count those lines as missed.

    Parameters
    ----------
    url : str
        The API documentation page URL to capture.
    output : Path
        Directory for the screenshot and problem report.

    Returns
    -------
    list of str
        The problems found. An empty list means the example ran and
        rendered successfully.

    """
    import playwright.sync_api

    output.mkdir(parents=True, exist_ok=True)
    problems: list[str] = []
    js_errors: list[str] = []
    failed_urls: list[str] = []

    with playwright.sync_api.sync_playwright() as p:
        # --headless=new passes Read the Docs' Cloudflare challenge, which
        # the old headless mode does not.
        browser = p.chromium.launch(headless=False, args=["--headless=new"])
        page = browser.new_page(viewport={"width": 1400, "height": 900})

        page.on("response", lambda response: _on_response(failed_urls, response))
        page.on("console", lambda msg: _on_console(js_errors, msg))
        page.on("pageerror", lambda err: js_errors.append(f"pageerror: {err}"))

        try:
            page.goto(url, wait_until="networkidle", timeout=120_000)

            button = page.locator("button.try_examples_button")
            if button.count() == 0:
                problems.append("No 'Try it with JupyterLite!' button found on the page.")
            else:
                button.first.click()
                iframe = page.locator(".jupyterlite_sphinx_iframe_container iframe")
                try:
                    iframe.wait_for(state="visible", timeout=120_000)
                except playwright.sync_api.Error as exc:  # pragma: no cover
                    problems.append(f"JupyterLite iframe never appeared: {exc}")

                lite = _find_lite_frame(page) if not problems else None
                if lite is None:  # pragma: no cover
                    problems.append("JupyterLite frame never loaded.")
                else:
                    problems.extend(_run_try_example(lite))

                page.wait_for_timeout(5_000)
        except playwright.sync_api.Error as exc:  # pragma: no cover
            problems.append(f"Capture failed with an unexpected error: {exc}")
        finally:
            try:
                page.screenshot(path=str(output / "capture.png"), full_page=True)
            except playwright.sync_api.Error as exc:  # pragma: no cover
                problems.append(f"No screenshot could be taken: {exc}")
            browser.close()

    # Resource failures are tracked with URLs via responses; console errors
    # and page errors are collected with their messages.
    problems.extend(js_errors)
    problems.extend(failed_urls)
    (output / "problems.json").write_text(
        json.dumps({"url": url, "problems": problems}, indent=2),
    )
    for problem in problems:
        logger.error("PROBLEM: %s", problem)
    if not problems:
        logger.info("Capture of %s succeeded with no problems.", url)
    return problems


def _build_issue_body(url: str, problems: list[str], run_url: str) -> str:
    """Build an issue body following the bug report template sections.

    Parameters
    ----------
    url : str
        The captured documentation page URL.
    problems : list of str
        The problems detected during the capture.
    run_url : str
        Link to the context that ran the capture (workflow run or command).

    Returns
    -------
    str
        The issue body in Markdown.

    """
    problem_list = "\n".join(f"- {problem}" for problem in problems)
    return f"""
### Bug Description

The automatic "Try it with JupyterLite" capture of an API documentation
page detected problems. This issue was automatically opened by the
[capture-try-example workflow]({run_url}).

### Steps to Reproduce

1. Open {url}
2. Click "Try it with JupyterLite!"
3. Run all cells

### Expected Behavior

The example cells run and the mesh renders on a canvas.

### Actual Behavior

{problem_list or "Unknown problem."}

### Environment Information

- Workflow run: {run_url}
- Operating System: {platform.platform()}

### Additional Context

The full-page screenshot is attached to the workflow run as the `capture` artifact.
""".strip()


def _open_bug_report(url: str, problems: list[str], output: Path) -> bool:
    """Open a bug-report issue with ``gh`` for the detected problems.

    Parameters
    ----------
    url : str
        The captured documentation page URL.
    problems : list of str
        The problems detected during the capture.
    output : Path
        Directory used for the capture (also the working directory for
        ``gh`` so relative artifact references stay correct).

    Returns
    -------
    bool
        True when the issue was created.

    """
    if not shutil.which("gh"):
        logger.error("The 'gh' CLI is required to open an issue but was not found.")
        return False

    run_url = os.environ.get(
        "CAPTURE_RUN_URL",
        f"https://github.com/{os.environ.get('GITHUB_REPOSITORY', 'tkoyama010/pyvista-js')}",
    )
    title = f"[Bug]: JupyterLite example capture failed for {url}"
    body = _build_issue_body(url, problems, run_url)
    gh = shutil.which("gh") or "gh"
    result = subprocess.run(
        [gh, "issue", "create", "--title", title, "--body", body, "--label", "bug"],
        check=False,
        capture_output=True,
        text=True,
        cwd=output,
        env={**os.environ},
    )
    if result.returncode != 0:
        logger.error("Failed to open issue: %s", result.stderr.strip())
        return False
    logger.info("Opened issue: %s", result.stdout.strip())
    return True


def run_capture(url: str, output: Path, *, open_issue: bool) -> bool:
    """Run the capture and optionally file a bug report.

    Parameters
    ----------
    url : str
        The API documentation page URL to capture.
    output : Path
        Directory for the screenshot and problem report.
    open_issue : bool
        Open a bug-report issue when problems are detected.

    Returns
    -------
    bool
        True when no problems were detected.

    """
    problems = _capture_try_example_page(url, output)
    if problems and open_issue:
        _open_bug_report(url, problems, output)
    return not problems
