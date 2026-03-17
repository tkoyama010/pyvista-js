"""Command-line interface for pyvista-js.

Provides a ``pyvista-js`` command with subcommands modelled after the
PyVista CLI so that common tasks (plotting mesh files, printing package
information) can be done without writing any Python code.
"""

from __future__ import annotations

import argparse
import logging
import platform
import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence

logger = logging.getLogger(__name__)

# Supported file extensions and the reader class name they map to.
_READER_MAP: dict[str, str] = {
    ".vtk": "PolyDataReader",
    ".ply": "PLYReader",
    ".obj": "OBJReader",
}


def _build_parser() -> argparse.ArgumentParser:
    """Build and return the top-level argument parser."""
    parser = argparse.ArgumentParser(
        prog="pyvista-js",
        description="PyVista-like CLI for browser-based 3-D visualization with vtk.js.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {_get_version()}",
    )

    subparsers = parser.add_subparsers(dest="command", metavar="COMMAND")
    subparsers.required = True

    _add_plot_subcommand(subparsers)
    _add_info_subcommand(subparsers)
    _add_capture_preview_subcommand(subparsers)

    return parser


def _get_version() -> str:
    """Return the pyvista_js version string."""
    from pyvista_js import __version__  # noqa: PLC0415

    return __version__


def _add_plot_subcommand(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Register the ``plot`` subcommand."""
    plot_parser = subparsers.add_parser(
        "plot",
        help="Plot one or more mesh files in the browser.",
        description=(
            "Open one or more mesh files (.vtk, .ply, .obj) and render them "
            "in the default web browser using vtk.js."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    plot_parser.add_argument(
        "files",
        nargs="+",
        metavar="FILE",
        help="Mesh file(s) to plot. Supported formats: .vtk (ASCII), .ply (ASCII), .obj.",
    )
    plot_parser.add_argument(
        "--color",
        default=None,
        metavar="COLOR",
        help="Mesh colour applied to all files (e.g. ``red``, ``#ff0000``).",
    )
    plot_parser.add_argument(
        "--background",
        default=None,
        metavar="COLOR",
        help="Background colour (e.g. ``white``, ``black``). Default: renderer default.",
    )
    plot_parser.add_argument(
        "--opacity",
        type=float,
        default=1.0,
        metavar="FLOAT",
        help="Mesh opacity in the range [0, 1]. Default: 1.0.",
    )
    plot_parser.set_defaults(func=_cmd_plot)


def _add_info_subcommand(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Register the ``info`` subcommand."""
    info_parser = subparsers.add_parser(
        "info",
        help="Show pyvista-js version and environment information.",
        description="Print the pyvista-js version and basic Python environment details.",
    )
    info_parser.set_defaults(func=_cmd_info)


# ---------------------------------------------------------------------------
# Subcommand implementations
# ---------------------------------------------------------------------------


def _read_mesh(path: Path):  # type: ignore[return]  # noqa: ANN202
    """Read a mesh file and return a PolyData object.

    Parameters
    ----------
    path : Path
        Path to the mesh file. Must have a supported extension
        (``.vtk``, ``.ply``, or ``.obj``).

    Returns
    -------
    pyvista_js.mesh.PolyData
        The loaded mesh.

    Raises
    ------
    SystemExit
        When the file does not exist or its extension is not supported.

    """
    import pyvista_js as pv  # noqa: PLC0415

    if not path.exists():
        logger.error("file not found: %s", path)
        sys.exit(1)

    suffix = path.suffix.lower()
    reader_name = _READER_MAP.get(suffix)
    if reader_name is None:
        supported = ", ".join(_READER_MAP)
        logger.error("unsupported file format '%s'. Supported: %s", suffix, supported)
        sys.exit(1)

    reader_cls = getattr(pv, reader_name)
    return reader_cls(path).read()


def _cmd_plot(args: argparse.Namespace) -> None:
    """Implement the ``plot`` subcommand.

    Parameters
    ----------
    args : argparse.Namespace
        Parsed command-line arguments.

    """
    import pyvista_js as pv  # noqa: PLC0415

    plotter = pv.Plotter()

    if args.background is not None:
        plotter.background_color = args.background

    for file_str in args.files:
        path = Path(file_str)
        mesh = _read_mesh(path)
        plotter.add_mesh(mesh, color=args.color, opacity=args.opacity)

    plotter.show()


def _add_capture_preview_subcommand(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Register the ``capture-preview`` subcommand."""
    capture_parser = subparsers.add_parser(
        "capture-preview",
        help="Capture a preview GIF of the JupyterLite demo.",
        description=(
            "Automate capturing a preview GIF showing pyvista-js rendering in JupyterLite. "
            "Requires: playwright, imageio[ffmpeg], pillow."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    capture_parser.add_argument(
        "--output",
        default="assets/preview.gif",
        metavar="PATH",
        help="Output path for the GIF. Default: assets/preview.gif.",
    )
    capture_parser.add_argument(
        "--url",
        default="https://tkoyama010.github.io/pyvista-js/",
        metavar="URL",
        help="URL of the JupyterLite demo.",
    )
    capture_parser.add_argument(
        "--fps",
        type=int,
        default=2,
        metavar="INT",
        help="Frames per second for the GIF. Default: 2.",
    )
    capture_parser.set_defaults(func=_cmd_capture_preview)


def _cmd_info(args: argparse.Namespace) -> None:  # noqa: ARG001
    """Implement the ``info`` subcommand.

    Parameters
    ----------
    args : argparse.Namespace
        Parsed command-line arguments (unused).

    """
    import pyvista_js as pv  # noqa: PLC0415

    logger.info("pyvista-js : %s", pv.__version__)
    logger.info("Python     : %s", sys.version)
    logger.info("Platform   : %s", platform.platform())


def _capture_screenshots(output_dir: Path, demo_url: str) -> Path:
    """Capture screenshots from the JupyterLite demo using Playwright.

    Parameters
    ----------
    output_dir : Path
        Directory to save temporary screenshots.
    demo_url : str
        URL of the JupyterLite demo.

    Returns
    -------
    Path
        Path to the directory containing screenshots.

    """
    from playwright.sync_api import sync_playwright  # noqa: PLC0415

    screenshots_dir = output_dir / "screenshots"
    screenshots_dir.mkdir(parents=True, exist_ok=True)

    logger.info("Capturing demo from: %s", demo_url)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1200, "height": 800})
        page = context.new_page()

        try:
            logger.info("Navigating to JupyterLite demo...")
            page.goto(demo_url, wait_until="domcontentloaded", timeout=60000)

            logger.info("Waiting for JupyterLite to load...")
            page.wait_for_timeout(15000)

            logger.info("Looking for simple_demo.ipynb...")
            page.wait_for_selector(".jp-DirListing-content", timeout=20000)

            notebook_selectors = [
                "text=simple_demo.ipynb",
                "[title*='simple_demo']",
                ".jp-DirListing-itemText:has-text('simple_demo')",
            ]

            notebook_found = False
            for selector in notebook_selectors:
                try:
                    page.wait_for_selector(selector, timeout=5000)
                    page.click(selector)
                    notebook_found = True
                    logger.info("Clicked on notebook using selector: %s", selector)
                    break
                except Exception:  # noqa: BLE001, PERF203
                    continue

            if not notebook_found:
                logger.warning("Could not find notebook, taking screenshot of main page")
                page.screenshot(path=str(screenshots_dir / "screenshot_01.png"))
                return screenshots_dir

            logger.info("Waiting for notebook to open...")
            page.wait_for_timeout(5000)

            page.screenshot(path=str(screenshots_dir / "screenshot_01.png"))

            logger.info("Attempting to run notebook cells...")
            page.wait_for_selector(".jp-Cell", timeout=10000)
            page.click(".jp-Cell")
            page.wait_for_timeout(1000)

            try:
                page.click("text=Run", timeout=5000)
                page.wait_for_timeout(500)
                page.click("text=Run All Cells", timeout=5000)
                logger.info("Clicked 'Run All Cells' from menu")
            except Exception:  # noqa: BLE001
                logger.info("Could not use menu, trying keyboard shortcuts")
                page.keyboard.press("Control+Shift+Enter")
                page.wait_for_timeout(1000)
                page.keyboard.press("Shift+Enter")
                page.wait_for_timeout(1000)
                page.keyboard.press("Shift+Enter")

            logger.info("Waiting for 3D rendering to appear...")
            page.wait_for_timeout(15000)

            logger.info("Capturing rendering screenshots...")
            for i in range(2, 15):
                page.screenshot(path=str(screenshots_dir / f"screenshot_{i:02d}.png"))
                page.wait_for_timeout(500)

            logger.info("Captured 14 screenshots successfully")

        except Exception:  # noqa: BLE001
            logger.exception("Error during demo capture")
            try:
                page.screenshot(path=str(screenshots_dir / "error_screenshot.png"))
            except Exception:  # noqa: BLE001
                pass
        finally:
            context.close()
            browser.close()

    return screenshots_dir


def _create_gif(screenshots_dir: Path, output_path: Path, fps: int = 2) -> bool:
    """Create a GIF from a directory of screenshot PNGs.

    Parameters
    ----------
    screenshots_dir : Path
        Directory containing ``screenshot_*.png`` files.
    output_path : Path
        Destination path for the GIF.
    fps : int
        Frames per second. Default: 2.

    Returns
    -------
    bool
        ``True`` if the GIF was created successfully.

    """
    import imageio.v3 as iio  # noqa: PLC0415

    screenshot_files = sorted(screenshots_dir.glob("screenshot_*.png"))
    if not screenshot_files:
        logger.error("No screenshots found!")
        return False

    logger.info("Found %d screenshots", len(screenshot_files))
    images = [iio.imread(f) for f in screenshot_files]

    duration_ms = int(1000 / fps)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    logger.info("Creating GIF at %s (%d fps)...", output_path, fps)
    iio.imwrite(output_path, images, duration=duration_ms, loop=0)

    logger.info("GIF created: %s (%.1f KB, %d frames)", output_path,
                output_path.stat().st_size / 1024, len(images))
    return True


def _cmd_capture_preview(args: argparse.Namespace) -> None:
    """Implement the ``capture-preview`` subcommand.

    Parameters
    ----------
    args : argparse.Namespace
        Parsed command-line arguments.

    """
    import tempfile  # noqa: PLC0415

    output_path = Path(args.output)

    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        screenshots_dir = _capture_screenshots(tmp_dir, args.url)

        screenshot_files = list(screenshots_dir.glob("screenshot_*.png"))
        if not screenshot_files:
            logger.error("No screenshots were captured")
            sys.exit(1)

        if not _create_gif(screenshots_dir, output_path, fps=args.fps):
            logger.error("Failed to create GIF")
            sys.exit(1)

    logger.info("Preview GIF saved to: %s", output_path)


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------


def main(argv: Sequence[str] | None = None) -> None:
    """Entry point for the ``pyvista-js`` command-line interface.

    Parameters
    ----------
    argv : sequence of str, optional
        Argument list to parse. Defaults to ``sys.argv[1:]``.

    """
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    parser = _build_parser()
    args = parser.parse_args(argv)
    args.func(args)
