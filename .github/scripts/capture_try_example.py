"""Capture a docs page after running its "Try it with JupyterLite" example.

Opens an API documentation page, activates the embedded JupyterLite widget,
runs all notebook cells, screenshots the result, and reports any problems
found (console errors, failed notebook loads, missing or blank renders).

Used by .github/workflows/capture-try-example.yml. Exit code 1 means
problems were detected; the full-page screenshot is always written.

Usage::

    python capture_try_example.py URL [--output PATH]
"""

# ruff: noqa: INP001, ANN401

import argparse
import json
import logging
import platform
import sys
import time
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

CANVAS_WAIT_SECONDS = 600
LITE_FRAME_WAIT_SECONDS = 120
HTTP_ERROR_MIN_STATUS = 400

# A rendered mesh produces more than one distinct color on the canvas;
# a blank (uniform) canvas produces exactly one.
MIN_DISTINCT_CANVAS_COLORS = 2


def _find_lite_frame(page: Any) -> Any:
    """Return the JupyterLite frame of *page*, polling until it appears."""
    deadline = time.monotonic() + LITE_FRAME_WAIT_SECONDS
    while time.monotonic() < deadline:
        for frame in page.frames:
            if "lite" in frame.url:
                return frame
        page.wait_for_timeout(2000)
    return None


def _on_response(failed_urls: list[str], response: Any) -> None:
    """Record HTTP errors, skipping optional files that may 404 by design."""
    if response.status >= HTTP_ERROR_MIN_STATUS and "try_examples.json" not in response.url:
        failed_urls.append(f"HTTP {response.status} loading {response.url.rsplit('/', 1)[-1]}")


def _on_console(js_errors: list[str], msg: Any) -> None:
    """Record console errors, skipping resource and theme noise with dedicated handlers."""
    if (
        msg.type == "error"
        and "Failed to load resource" not in msg.text
        # JupyterLite theme quirk, harmless and not our fault.
        and "Got invalid theme mode" not in msg.text
    ):
        js_errors.append(f"console.error: {msg.text}")


def capture(url: str, output: Path) -> list[str]:
    """Run the Try-it-with-JupyterLite example on *url* and capture it.

    Writes ``capture.png`` and ``problems.json`` into *output*.

    Returns the list of problems found. An empty list means the example
    ran and rendered successfully.
    """
    import playwright.sync_api  # noqa: PLC0415

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
                except Exception as exc:  # noqa: BLE001
                    problems.append(f"JupyterLite iframe never appeared: {exc}")

                lite = _find_lite_frame(page) if not problems else None
                if lite is None:
                    problems.append("JupyterLite frame never loaded.")
                else:
                    problems.extend(_run_example(lite))

            page.wait_for_timeout(5_000)
        except Exception as exc:  # noqa: BLE001
            problems.append(f"Capture failed with an unexpected error: {exc}")
        finally:
            try:
                page.screenshot(path=str(output / "capture.png"), full_page=True)
            except Exception as exc:  # noqa: BLE001
                problems.append(f"No screenshot could be taken: {exc}")
            browser.close()

    # Resource failures are tracked with URLs via responses; console errors
    # and page errors are collected with their messages.
    problems.extend(js_errors)
    problems.extend(failed_urls)
    _write_problems(problems, output, url)
    return problems


def _run_example(lite: Any) -> list[str]:
    """Run all cells in the JupyterLite notebook and check the result."""
    problems: list[str] = []
    try:
        lite.wait_for_selector(".jp-Notebook .jp-Cell", timeout=180_000)
    except Exception as exc:  # noqa: BLE001
        problems.append(f"Notebook UI never finished booting: {exc}")
        return problems

    # A "File Load Error" dialog means the generated example notebook is
    # missing from the deployed JupyterLite contents.
    file_load_error = lite.locator(".jp-Dialog", has_text="File Load Error")
    dialog_shown = True
    try:
        file_load_error.wait_for(timeout=5_000)
    except Exception as exc:  # noqa: BLE001
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
    except Exception as exc:  # noqa: BLE001
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
    except Exception as exc:  # noqa: BLE001
        problems.append(f"Could not inspect the render canvas: {exc}")

    return problems


def _canvas_renders_mesh(lite: Any) -> bool:
    """Report whether the example canvas shows more than a uniform color.

    Mirrors the distinct-color check used by the browser rendering tests:
    a uniform background (dark, light, or fully transparent) means nothing
    was drawn, while any rendered mesh yields multiple distinct colors.
    """
    import io  # noqa: PLC0415

    import numpy as np  # noqa: PLC0415
    from PIL import Image  # noqa: PLC0415

    screenshot = lite.locator(".jp-OutputArea-output canvas").first.screenshot()
    pixels = np.asarray(Image.open(io.BytesIO(screenshot)).convert("RGB"))
    colors = {tuple(color) for color in pixels.reshape(-1, 3).tolist()}
    return len(colors) >= MIN_DISTINCT_CANVAS_COLORS


def _write_problems(problems: list[str], output: Path, url: str) -> None:
    """Write ``problems.json`` with the detected problems."""
    (output / "problems.json").write_text(json.dumps({"url": url, "problems": problems}, indent=2))
    for problem in problems:
        logger.error("PROBLEM: %s", problem)
    if not problems:
        logger.info("Capture of %s succeeded with no problems.", url)


def build_issue_body(url: str, problems: list[str], run_url: str) -> str:
    """Build an issue body following the bug report template sections."""
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
- Operating System: {platform.system()} (GitHub Actions runner)

### Additional Context

The full-page screenshot is attached to the workflow run as the `capture` artifact.
""".strip()


def main() -> int:
    """Run the capture from the command line."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url", help="API documentation page URL to capture")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("capture-artifacts"),
        help="Directory for capture.png and problems.json",
    )
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)

    problems = capture(args.url, args.output)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
