"""Command-line interface for pyvista-js.

Provides a ``pyvista-js`` command with subcommands modelled after the
PyVista CLI so that common tasks (plotting mesh files, printing package
information) can be done without writing any Python code.
"""

from __future__ import annotations

import logging
import platform
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Annotated

import typer

if TYPE_CHECKING:
    from collections.abc import Sequence

logger = logging.getLogger(__name__)

# Supported file extensions and the reader class name they map to.
_READER_MAP: dict[str, str] = {
    ".vtk": "PolyDataReader",
    ".ply": "PLYReader",
    ".obj": "OBJReader",
}

# Create the main Typer app
app = typer.Typer(
    name="pyvista-js",
    help="PyVista-like CLI for browser-based 3-D visualization with vtk.js.",
    no_args_is_help=True,
)


def _version_callback(value: bool) -> None:  # noqa: FBT001
    """Show version information and exit."""
    if value:
        typer.echo(f"pyvista-js {_get_version()}")
        raise typer.Exit


@app.callback()
def main(
    version: Annotated[
        bool | None,
        typer.Option(
            "--version",
            callback=_version_callback,
            is_eager=True,
            help="Show version and exit.",
        ),
    ] = None,
) -> None:
    """PyVista-like CLI for browser-based 3-D visualization with vtk.js."""


def _get_version() -> str:
    """Return the pyvista_js version string."""
    from pyvista_js import __version__  # noqa: PLC0415

    return __version__


# ---------------------------------------------------------------------------
# Helper functions
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


def _load_plotter_from_pickle(pickle_path: Path):  # type: ignore[return]  # noqa: ANN202
    """Load a Plotter object from a pickle file.

    Parameters
    ----------
    pickle_path : Path
        Path to the pickle file containing a Plotter object.

    Returns
    -------
    pyvista_js.Plotter
        The loaded Plotter object.

    Raises
    ------
    SystemExit
        When the file does not exist, cannot be loaded, or does not
        contain a valid Plotter object.

    """
    import pickle  # noqa: PLC0415

    import pyvista_js as pv  # noqa: PLC0415

    if not pickle_path.exists():
        logger.error("pickle file not found: %s", pickle_path)
        sys.exit(1)

    # Security warning
    logger.warning(
        "WARNING: Loading pickle files can execute arbitrary code. "
        "Only load pickle files from trusted sources.",
    )

    try:
        with pickle_path.open("rb") as f:
            plotter = pickle.load(f)  # noqa: S301
    except Exception:
        logger.exception("failed to load pickle file")
        sys.exit(1)

    # Validate that we loaded a Plotter object
    if not isinstance(plotter, pv.Plotter):
        logger.error(
            "pickle file does not contain a Plotter object (got %s)",
            type(plotter).__name__,
        )
        sys.exit(1)

    return plotter


# ---------------------------------------------------------------------------
# Subcommand implementations
# ---------------------------------------------------------------------------


@app.command()
def plot(  # noqa: PLR0913
    files: Annotated[
        list[Path] | None,
        typer.Argument(
            help="Mesh file(s) to plot. Supported formats: .vtk (ASCII), .ply (ASCII), .obj. "
            "Optional when --load-pickle is provided.",
            metavar="FILE",
        ),
    ] = None,
    color: Annotated[
        str | None,
        typer.Option(
            help="Mesh colour applied to all files (e.g. ``red``, ``#ff0000``).",
            metavar="COLOR",
        ),
    ] = None,
    background: Annotated[
        str | None,
        typer.Option(
            help="Background colour (e.g. ``white``, ``black``). Default: renderer default.",
            metavar="COLOR",
        ),
    ] = None,
    opacity: Annotated[
        float,
        typer.Option(
            help="Mesh opacity in the range [0, 1]. Default: 1.0.",
            metavar="FLOAT",
        ),
    ] = 1.0,
    pickle: Annotated[
        Path | None,
        typer.Option(
            help="Save the Plotter object to a pickle file for later reuse.",
            metavar="PATH",
        ),
    ] = None,
    load_pickle: Annotated[
        Path | None,
        typer.Option(
            help="Load a pickled Plotter object from file instead of creating a new one. "
            "WARNING: Only load pickle files from trusted sources.",
            metavar="PATH",
        ),
    ] = None,
) -> None:
    """Plot one or more mesh files in the browser.

    Open one or more mesh files (.vtk, .ply, .obj) and render them
    in the default web browser using vtk.js. Alternatively, load a
    previously saved Plotter object from a pickle file.
    """
    import pickle as pickle_module  # noqa: PLC0415

    import pyvista_js as pv  # noqa: PLC0415

    if load_pickle is not None:
        # Load plotter from pickle file
        plotter = _load_plotter_from_pickle(load_pickle)

        # If files are also provided with --load-pickle, add them to the loaded plotter
        if files:
            for file_path in files:
                mesh = _read_mesh(file_path)
                plotter.add_mesh(mesh, color=color, opacity=opacity)

        # If background is specified, override the loaded plotter's background
        if background is not None:
            plotter.background_color = background
    else:
        # Normal flow: create a new plotter from mesh files
        if not files:
            logger.error(
                "no mesh files provided. Either provide mesh files or use --load-pickle.",
            )
            sys.exit(1)

        plotter = pv.Plotter()

        if background is not None:
            plotter.background_color = background

        for file_path in files:
            mesh = _read_mesh(file_path)
            plotter.add_mesh(mesh, color=color, opacity=opacity)

    # Save to pickle file if requested
    if pickle is not None:
        with pickle.open("wb") as f:
            pickle_module.dump(plotter, f)
        logger.info("Plotter saved to: %s", pickle)

    plotter.show()


@app.command()
def info() -> None:
    """Show pyvista-js version and environment information.

    Print the pyvista-js version and basic Python environment details.
    """
    import pyvista_js as pv  # noqa: PLC0415

    logger.info("pyvista-js : %s", pv.__version__)
    logger.info("Python     : %s", sys.version)
    logger.info("Platform   : %s", platform.platform())


@app.command(name="generate-typescript")
def generate_typescript(
    files: Annotated[
        list[Path] | None,
        typer.Argument(
            help="Mesh file(s) to generate TypeScript for. Supported formats: .vtk (ASCII), .ply (ASCII), .obj. "
            "Optional when --load-pickle is provided.",
            metavar="FILE",
        ),
    ] = None,
    output: Annotated[
        Path,
        typer.Option(
            help="Output path for the TypeScript file. Default: visualization.ts.",
            metavar="PATH",
        ),
    ] = Path("visualization.ts"),
    color: Annotated[
        str | None,
        typer.Option(
            help="Mesh colour applied to all files (e.g. ``red``, ``#ff0000``).",
            metavar="COLOR",
        ),
    ] = None,
    background: Annotated[
        str | None,
        typer.Option(
            help="Background colour (e.g. ``white``, ``black``). Default: renderer default.",
            metavar="COLOR",
        ),
    ] = None,
    opacity: Annotated[
        float,
        typer.Option(
            help="Mesh opacity in the range [0, 1]. Default: 1.0.",
            metavar="FLOAT",
        ),
    ] = 1.0,
    load_pickle: Annotated[
        Path | None,
        typer.Option(
            help="Load a pickled Plotter object from file instead of creating a new one. "
            "WARNING: Only load pickle files from trusted sources.",
            metavar="PATH",
        ),
    ] = None,
) -> None:
    """Generate TypeScript code for vtk.js visualization.

    Generate TypeScript (.ts) code with type annotations for rendering
    mesh files using vtk.js. The generated code includes full type
    definitions for better IDE support and type checking.
    """
    import pyvista_js as pv  # noqa: PLC0415

    if load_pickle is not None:
        # Load plotter from pickle file
        plotter = _load_plotter_from_pickle(load_pickle)

        # If files are also provided with --load-pickle, add them to the loaded plotter
        if files:
            for file_path in files:
                mesh = _read_mesh(file_path)
                plotter.add_mesh(mesh, color=color, opacity=opacity)

        # If background is specified, override the loaded plotter's background
        if background is not None:
            plotter.background_color = background
    else:
        # Normal flow: create a new plotter from mesh files
        if not files:
            logger.error(
                "no mesh files provided. Either provide mesh files or use --load-pickle.",
            )
            sys.exit(1)

        plotter = pv.Plotter()

        if background is not None:
            plotter.background_color = background

        for file_path in files:
            mesh = _read_mesh(file_path)
            plotter.add_mesh(mesh, color=color, opacity=opacity)

    # Generate TypeScript code
    ts_code = plotter._renderer._generate_typescript()  # noqa: SLF001

    # Write to output file
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(ts_code, encoding="utf-8")

    logger.info("TypeScript code generated: %s", output)
    logger.info("To use this file, install vtk.js types: npm install --save-dev @kitware/vtk.js")


def _open_notebook(page, screenshots_dir: Path) -> bool:  # noqa: ANN001
    """Find and open the demo notebook in the JupyterLite file browser.

    Parameters
    ----------
    page : playwright.sync_api.Page
        The Playwright page object.
    screenshots_dir : Path
        Directory to save fallback screenshots.

    Returns
    -------
    bool
        ``True`` if the notebook was opened successfully.

    """
    notebook_selectors = [
        "text=simple_demo.ipynb",
        "[title*='simple_demo']",
        ".jp-DirListing-itemText:has-text('simple_demo')",
    ]

    for selector in notebook_selectors:
        element = page.query_selector(selector)
        if element is not None:
            element.dblclick()
            logger.info("Double-clicked on notebook using selector: %s", selector)
            return True

    logger.warning("Could not find notebook, taking screenshot of main page")
    page.screenshot(path=str(screenshots_dir / "screenshot_01.png"))
    return False


def _run_notebook_cells(page) -> None:  # noqa: ANN001
    """Execute all cells in the currently open notebook.

    Parameters
    ----------
    page : playwright.sync_api.Page
        The Playwright page object.

    """
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


def _rotate_canvas_with_mouse(page, canvas_selector: str = "canvas") -> None:  # noqa: ANN001
    """Rotate the 3D model by dragging the mouse across the canvas.

    Parameters
    ----------
    page : playwright.sync_api.Page
        The Playwright page object.
    canvas_selector : str
        CSS selector for the canvas element. Default: "canvas".

    """
    try:
        canvas = page.query_selector(canvas_selector)
        if canvas is None:
            logger.warning("Canvas element not found, skipping rotation")
            return

        box = canvas.bounding_box()
        if box is None:
            logger.warning("Canvas bounding box not available, skipping rotation")
            return

        # Calculate center and drag path
        center_x = box["x"] + box["width"] / 2
        center_y = box["y"] + box["height"] / 2
        drag_distance = box["width"] / 3  # Drag 1/3 of canvas width

        # Perform mouse drag: click + move to simulate rotation
        page.mouse.move(center_x - drag_distance / 2, center_y)
        page.mouse.down()
        page.mouse.move(center_x + drag_distance / 2, center_y, steps=20)
        page.mouse.up()

        logger.info("Performed mouse drag rotation on canvas")
    except Exception:  # noqa: BLE001
        logger.warning("Failed to perform mouse drag rotation", exc_info=True)


def _capture_screenshots(output_dir: Path, demo_url: str, *, rotate: bool = False) -> Path:
    """Capture screenshots from the JupyterLite demo using Playwright.

    Parameters
    ----------
    output_dir : Path
        Directory to save temporary screenshots.
    demo_url : str
        URL of the JupyterLite demo.
    rotate : bool
        If ``True``, rotate the 3D model by mouse drag between
        screenshots. Default: ``False``.

    Returns
    -------
    Path
        Path to the directory containing screenshots.

    """
    import contextlib  # noqa: PLC0415

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

            if not _open_notebook(page, screenshots_dir):
                return screenshots_dir

            logger.info("Waiting for notebook to open...")
            page.wait_for_timeout(5000)
            page.screenshot(path=str(screenshots_dir / "screenshot_01.png"))

            logger.info("Attempting to run notebook cells...")
            _run_notebook_cells(page)

            logger.info("Waiting for 3D rendering to appear...")
            page.wait_for_timeout(15000)

            if rotate:
                logger.info("Capturing rendering screenshots with rotation...")
                # Capture first screenshot at initial position
                page.screenshot(path=str(screenshots_dir / "screenshot_02.png"))
                page.wait_for_timeout(300)

                # Capture remaining screenshots while rotating
                for i in range(3, 15):
                    _rotate_canvas_with_mouse(page)
                    page.wait_for_timeout(300)
                    page.screenshot(path=str(screenshots_dir / f"screenshot_{i:02d}.png"))
                    page.wait_for_timeout(300)
            else:
                logger.info("Capturing rendering screenshots...")
                for i in range(2, 15):
                    page.screenshot(path=str(screenshots_dir / f"screenshot_{i:02d}.png"))
                    page.wait_for_timeout(500)

            logger.info("Captured 14 screenshots successfully")

        except Exception:
            logger.exception("Error during demo capture")
            with contextlib.suppress(Exception):
                page.screenshot(path=str(screenshots_dir / "error_screenshot.png"))
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

    logger.info(
        "GIF created: %s (%.1f KB, %d frames)",
        output_path,
        output_path.stat().st_size / 1024,
        len(images),
    )
    return True


@app.command(name="capture-preview")
def capture_preview(
    output: Annotated[
        Path,
        typer.Option(
            help="Output path for the GIF. Default: assets/preview.gif.",
            metavar="PATH",
        ),
    ] = Path("assets/preview.gif"),
    url: Annotated[
        str,
        typer.Option(
            help="URL of the JupyterLite demo.",
            metavar="URL",
        ),
    ] = "https://tkoyama010.github.io/pyvista-js/",
    fps: Annotated[
        int,
        typer.Option(
            help="Frames per second for the GIF. Default: 2.",
            metavar="INT",
        ),
    ] = 2,
    rotate: Annotated[
        bool | None,
        typer.Option(
            help="Rotate the 3D model by mouse drag while capturing screenshots. "
            "Will become the default in a future version.",
        ),
    ] = None,
) -> None:
    """Capture a preview GIF of the JupyterLite demo.

    Automate capturing a preview GIF showing pyvista-js rendering in JupyterLite.
    Requires: playwright, imageio[ffmpeg], pillow.
    """
    import tempfile  # noqa: PLC0415
    import warnings  # noqa: PLC0415

    if rotate is None:
        warnings.warn(
            "The default behavior of 'capture-preview' will change in a future "
            "version to rotate the 3D model during capture. "
            "Pass '--rotate' to enable the new behavior now, or "
            "'--no-rotate' to silence this warning and keep the current behavior.",
            DeprecationWarning,
            stacklevel=1,
        )
        rotate = False

    output_path = output

    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        screenshots_dir = _capture_screenshots(tmp_dir, url, rotate=rotate)

        screenshot_files = list(screenshots_dir.glob("screenshot_*.png"))
        if not screenshot_files:
            logger.error("No screenshots were captured")
            sys.exit(1)

        if not _create_gif(screenshots_dir, output_path, fps=fps):
            logger.error("Failed to create GIF")
            sys.exit(1)

    logger.info("Preview GIF saved to: %s", output_path)


# ---------------------------------------------------------------------------
# CLI entry point wrapper for backwards compatibility
# ---------------------------------------------------------------------------


def cli_main(argv: Sequence[str] | None = None) -> None:
    """Entry point for the ``pyvista-js`` command-line interface.

    Parameters
    ----------
    argv : sequence of str, optional
        Argument list to parse. Defaults to ``sys.argv[1:]``.

    """
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    # Use standalone_mode=False to prevent sys.exit(0) in tests
    app(argv, standalone_mode=False)
