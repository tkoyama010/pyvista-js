"""Command-line interface for pyvista-js.

Provides a ``pyvista-js`` command with subcommands modelled after the
PyVista CLI so that common tasks (plotting mesh files, printing package
information) can be done without writing any Python code.
"""

from __future__ import annotations

import json
import logging
import platform
import shutil
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Annotated

import typer

if TYPE_CHECKING:
    from collections.abc import Sequence

    from playwright.sync_api import ConsoleMessage, Frame, Page, Response

CANVAS_WAIT_SECONDS = 600
LITE_FRAME_WAIT_SECONDS = 120
HTTP_ERROR_MIN_STATUS = 400

# A rendered mesh produces more than one distinct color on the canvas;
# a blank (uniform) canvas produces exactly one.
MIN_DISTINCT_CANVAS_COLORS = 2

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


def _apply_camera_movement(
    plotter,  # noqa: ANN001
    azimuth: float | None,
    elevation: float | None,
    zoom: float | None,
    roll: float | None,
) -> None:
    """Apply relative camera movements to an existing plotter camera.

    All movements are relative to the current camera state.  Delegates
    to :class:`~pyvista_js.Camera` methods.

    Parameters
    ----------
    plotter : pyvista_js.Plotter
        The plotter whose camera will be modified.
    azimuth : float or None
        Horizontal rotation around the focal point in degrees.
    elevation : float or None
        Vertical rotation around the focal point in degrees.
    zoom : float or None
        Zoom factor (>1 zooms in, <1 zooms out).
    roll : float or None
        Roll rotation around the view axis in degrees.

    """
    from .camera import Camera  # noqa: PLC0415

    if plotter.camera is None:
        plotter.camera = Camera()

    cam = plotter.camera

    if azimuth is not None:
        cam.azimuth(azimuth)
    if elevation is not None:
        cam.orbit_elevation(elevation)
    if zoom is not None:
        if zoom <= 0:
            logger.error("zoom must be positive, got %s", zoom)
            sys.exit(1)
        cam.zoom(zoom)
    if roll is not None:
        cam.roll(roll)


# ---------------------------------------------------------------------------
# Subcommand implementations
# ---------------------------------------------------------------------------


def _build_plotter(  # noqa: ANN202
    files: list[Path] | None,
    color: str | None,
    background: str | None,
    opacity: float,
    load_pickle: Path | None,
):  # type: ignore[return]
    """Build a Plotter from mesh files or a pickle, returning it ready to display.

    Parameters
    ----------
    files : list of Path or None
        Mesh files to load.
    color : str or None
        Mesh colour.
    background : str or None
        Background colour override.
    opacity : float
        Mesh opacity.
    load_pickle : Path or None
        Path to a pickled Plotter to load instead.

    Returns
    -------
    pyvista_js.Plotter
        The configured plotter.

    """
    import pyvista_js as pv  # noqa: PLC0415

    if load_pickle is not None:
        plotter = _load_plotter_from_pickle(load_pickle)

        if files:
            for file_path in files:
                mesh = _read_mesh(file_path)
                plotter.add_mesh(mesh, color=color, opacity=opacity)

        if background is not None:
            plotter.background_color = background
    else:
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

    return plotter


def _save_pickle(plotter, pickle_path: Path) -> None:  # noqa: ANN001
    """Serialize a Plotter to a pickle file.

    Parameters
    ----------
    plotter : pyvista_js.Plotter
        The plotter to save.
    pickle_path : Path
        Destination file path.

    """
    import pickle as pickle_module  # noqa: PLC0415

    with pickle_path.open("wb") as f:
        pickle_module.dump(plotter, f)
    logger.info("Plotter saved to: %s", pickle_path)


def _parse_window_size(size_str: str) -> tuple[int, int]:
    """Parse a ``'width,height'`` string into an integer pair.

    Parameters
    ----------
    size_str : str
        Window size string, e.g. ``'1920,1080'``.

    Returns
    -------
    tuple of int
        ``(width, height)``.

    Raises
    ------
    SystemExit
        When the format is invalid.

    """
    try:
        width_str, height_str = size_str.split(",")
        return (int(width_str.strip()), int(height_str.strip()))
    except (ValueError, AttributeError):
        logger.error(  # noqa: TRY400
            "Invalid window size format '%s'. Expected 'width,height' (e.g. '1920,1080')",
            size_str,
        )
        sys.exit(1)


def _take_screenshot(
    plotter,  # noqa: ANN001
    screenshot: Path,
    screenshot_transparent: bool,  # noqa: FBT001
    screenshot_scale: int | None,
    screenshot_window_size: str | None,
) -> None:
    """Save a screenshot of the plotter scene.

    Parameters
    ----------
    plotter : pyvista_js.Plotter
        The plotter to capture.
    screenshot : Path
        Output file path.
    screenshot_transparent : bool
        Whether to use a transparent background.
    screenshot_scale : int or None
        Resolution scale factor.
    screenshot_window_size : str or None
        Window size as ``'width,height'``.

    """
    window_size = None
    if screenshot_window_size is not None:
        window_size = _parse_window_size(screenshot_window_size)

    plotter.screenshot(
        filename=screenshot,
        transparent_background=screenshot_transparent or None,
        return_img=False,
        window_size=window_size,
        scale=screenshot_scale,
    )
    logger.info("Screenshot saved to: %s", screenshot)


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
            "--color",
            help="Mesh colour applied to all files (e.g. ``red``, ``#ff0000``).",
            metavar="COLOR",
        ),
    ] = None,
    background: Annotated[
        str | None,
        typer.Option(
            "--background",
            help="Background colour (e.g. ``white``, ``black``). Default: renderer default.",
            metavar="COLOR",
        ),
    ] = None,
    opacity: Annotated[
        float,
        typer.Option(
            "--opacity",
            help="Mesh opacity in the range [0, 1]. Default: 1.0.",
            metavar="FLOAT",
        ),
    ] = 1.0,
    pickle: Annotated[
        Path | None,
        typer.Option(
            "--pickle",
            help="Save the Plotter object to a pickle file for later reuse.",
            metavar="PATH",
        ),
    ] = None,
    load_pickle: Annotated[
        Path | None,
        typer.Option(
            "--load-pickle",
            help="Load a pickled Plotter object from file instead of creating a new one. "
            "WARNING: Only load pickle files from trusted sources.",
            metavar="PATH",
        ),
    ] = None,
    screenshot: Annotated[
        Path | None,
        typer.Option(
            "--screenshot",
            help="Save a screenshot to the specified file (PNG/JPEG). "
            "When provided, the browser window will not open.",
            metavar="PATH",
        ),
    ] = None,
    screenshot_transparent: Annotated[  # noqa: FBT002
        bool,
        typer.Option(
            "--screenshot-transparent/--no-screenshot-transparent",
            help="Use transparent background for screenshot. Default: False.",
        ),
    ] = False,
    screenshot_scale: Annotated[
        int | None,
        typer.Option(
            "--screenshot-scale",
            help="Scale factor for screenshot resolution (e.g. 2 for double resolution).",
            metavar="INT",
        ),
    ] = None,
    screenshot_window_size: Annotated[
        str | None,
        typer.Option(
            "--screenshot-window-size",
            help="Window size for screenshot as 'width,height' (e.g. '1920,1080').",
            metavar="SIZE",
        ),
    ] = None,
    azimuth: Annotated[
        float | None,
        typer.Option(
            "--azimuth",
            help="Rotate camera horizontally around the focal point by this many degrees.",
            metavar="DEGREES",
        ),
    ] = None,
    elevation: Annotated[
        float | None,
        typer.Option(
            "--elevation",
            help="Rotate camera vertically around the focal point by this many degrees.",
            metavar="DEGREES",
        ),
    ] = None,
    zoom: Annotated[
        float | None,
        typer.Option(
            "--zoom",
            help="Zoom factor relative to current distance (>1 zooms in, <1 zooms out).",
            metavar="FLOAT",
        ),
    ] = None,
    roll: Annotated[
        float | None,
        typer.Option(
            "--roll",
            help="Roll camera around its view axis by this many degrees.",
            metavar="DEGREES",
        ),
    ] = None,
) -> None:
    """Plot one or more mesh files in the browser.

    Open one or more mesh files (.vtk, .ply, .obj) and render them
    in the default web browser using vtk.js. Alternatively, load a
    previously saved Plotter object from a pickle file.

    If ``--screenshot`` is provided, a screenshot will be saved to the
    specified file instead of opening the browser window.
    """
    plotter = _build_plotter(files, color, background, opacity, load_pickle)

    if any(opt is not None for opt in (azimuth, elevation, zoom, roll)):
        _apply_camera_movement(plotter, azimuth, elevation, zoom, roll)

    if pickle is not None:
        _save_pickle(plotter, pickle)

    if screenshot is not None:
        _take_screenshot(
            plotter,
            screenshot,
            screenshot_transparent,
            screenshot_scale,
            screenshot_window_size,
        )
    else:
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
        "text=intro.ipynb",
        "[title*='intro']",
        ".jp-DirListing-itemText:has-text('intro')",
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


def _find_canvas_in_frames(page) -> tuple:  # noqa: ANN001
    """Find a canvas element by searching through all frames (including nested iframes).

    Parameters
    ----------
    page : playwright.sync_api.Page
        The Playwright page object.

    Returns
    -------
    tuple
        A (frame, element_handle) pair, or (None, None) if not found.

    """
    logger.debug("Searching for canvas in %d frames", len(page.frames))
    for i, frame in enumerate(page.frames):
        try:
            # Check if frame is accessible
            frame_url = frame.url
            logger.debug("Checking frame %d: %s", i, frame_url[:100] if frame_url else "no url")

            # Try multiple canvas selectors
            selectors = ["canvas", "canvas[data-testid]", "[data-testid='stCanvas'] canvas"]
            for selector in selectors:
                canvas = frame.query_selector(selector)
                if canvas is not None:
                    logger.info("Found canvas element in frame %d using selector: %s", i, selector)
                    return frame, canvas
        except Exception as e:  # noqa: BLE001
            logger.debug("Failed to query canvas in frame %d: %s", i, e)
            continue

    logger.debug("No canvas found in any frame")
    return None, None


def _rotate_canvas_with_mouse(page) -> None:  # noqa: ANN001
    """Rotate the 3D model by dragging the mouse across the canvas.

    Parameters
    ----------
    page : playwright.sync_api.Page
        The Playwright page object.

    """
    try:
        _frame, canvas = _find_canvas_in_frames(page)
        if canvas is None:
            logger.warning("Canvas element not found in any frame, skipping rotation")
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
    except Exception:
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

    from .rendering import _launch_chromium  # noqa: PLC0415

    screenshots_dir = output_dir / "screenshots"
    screenshots_dir.mkdir(parents=True, exist_ok=True)

    logger.info("Capturing demo from: %s", demo_url)

    with sync_playwright() as p:
        browser = _launch_chromium(p)
        context = browser.new_context(viewport={"width": 1200, "height": 800})
        page = context.new_page()

        try:
            logger.info("Navigating to JupyterLite demo...")
            page.goto(demo_url, wait_until="domcontentloaded", timeout=60000)

            logger.info("Waiting for JupyterLite to load...")
            page.wait_for_timeout(15000)

            logger.info("Looking for intro.ipynb...")
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
            "--output",
            help="Output path for the GIF. Default: assets/preview.gif.",
            metavar="PATH",
        ),
    ] = Path("assets/preview.gif"),
    url: Annotated[
        str,
        typer.Option(
            "--url",
            help="URL of the JupyterLite demo.",
            metavar="URL",
        ),
    ] = "https://tkoyama010.github.io/pyvista-js/",
    fps: Annotated[
        int,
        typer.Option(
            "--fps",
            help="Frames per second for the GIF. Default: 2.",
            metavar="INT",
        ),
    ] = 2,
    rotate: Annotated[
        bool | None,
        typer.Option(
            "--rotate/--no-rotate",
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


def _wait_for_canvas_in_frames(page, timeout: int = 120) -> None:  # noqa: ANN001
    """Poll all frames until a canvas element appears or *timeout* seconds elapse.

    Parameters
    ----------
    page : playwright.sync_api.Page
        The Playwright page object.
    timeout : int
        Maximum seconds to wait.  Default: 120.

    Raises
    ------
    TimeoutError
        If no canvas is found within *timeout* seconds.

    """
    import time  # noqa: PLC0415

    deadline = time.monotonic() + timeout
    check_count = 0

    while time.monotonic() < deadline:
        check_count += 1
        _frame, canvas = _find_canvas_in_frames(page)
        if canvas is not None:
            logger.info("Found canvas element in iframe after %d checks", check_count)
            return

        # Log progress every 10 checks (20 seconds)
        if check_count % 10 == 0:  # pragma: no cover
            elapsed = int(time.monotonic() - (deadline - timeout))
            logger.info(
                "Still waiting for canvas... elapsed: %ds, frames: %d",
                elapsed,
                len(page.frames),
            )

        page.wait_for_timeout(2000)

    msg = (
        f"Canvas element not found in any frame within {timeout} seconds "
        f"(checked {check_count} times)"
    )
    raise TimeoutError(msg)


def _capture_stlite_screenshots(output_dir: Path, demo_url: str, *, rotate: bool = True) -> Path:
    """Capture screenshots from the stlite demo using Playwright.

    Parameters
    ----------
    output_dir : Path
        Directory to save temporary screenshots.
    demo_url : str
        URL of the stlite demo.
    rotate : bool
        If ``True``, rotate the 3D model by mouse drag between
        screenshots. Default: ``True``.

    Returns
    -------
    Path
        Path to the directory containing screenshots.

    """
    import contextlib  # noqa: PLC0415

    from playwright.sync_api import sync_playwright  # noqa: PLC0415

    from .rendering import _launch_chromium  # noqa: PLC0415

    screenshots_dir = output_dir / "screenshots"
    screenshots_dir.mkdir(parents=True, exist_ok=True)

    logger.info("Capturing stlite demo from: %s", demo_url)

    with sync_playwright() as p:
        browser = _launch_chromium(p)
        context = browser.new_context(viewport={"width": 1200, "height": 800})
        page = context.new_page()

        try:
            logger.info("Navigating to stlite demo...")
            page.goto(demo_url, wait_until="networkidle", timeout=120000)

            logger.info("Waiting for stlite to load and install dependencies...")
            # Wait for stlite to initialize Python and install pyvista-js
            # Increased from 60s to 90s as dependency installation can be slow
            page.wait_for_timeout(90000)

            # Log frame information for debugging
            logger.info("Page has %d frames after initial load", len(page.frames))
            for i, frame in enumerate(page.frames):
                try:
                    url = frame.url[:100] if frame.url else "no url"
                    logger.info("Frame %d: %s", i, url)
                except Exception as e:  # noqa: BLE001  # pragma: no cover
                    logger.debug("Could not get URL for frame %d: %s", i, e)

            logger.info("Waiting for 3D rendering to appear in iframes...")
            # stlite renders the Streamlit app in iframes, and
            # components.html() creates another nested iframe for the
            # Three.js canvas.  page.wait_for_selector only searches the
            # top-level document, so we poll all frames instead.
            _wait_for_canvas_in_frames(page)

            page.wait_for_timeout(5000)

            if rotate:
                logger.info("Capturing rendering screenshots with rotation...")
                # Capture first screenshot at initial position
                page.screenshot(path=str(screenshots_dir / "screenshot_01.png"))
                page.wait_for_timeout(300)

                # Capture remaining screenshots while rotating
                for i in range(2, 15):
                    _rotate_canvas_with_mouse(page)
                    page.wait_for_timeout(300)
                    page.screenshot(path=str(screenshots_dir / f"screenshot_{i:02d}.png"))
                    page.wait_for_timeout(300)
            else:
                logger.info("Capturing rendering screenshots...")
                for i in range(1, 15):
                    page.screenshot(path=str(screenshots_dir / f"screenshot_{i:02d}.png"))
                    page.wait_for_timeout(500)

            logger.info("Captured 14 screenshots successfully")

        except Exception:
            logger.exception("Error during stlite demo capture")
            with contextlib.suppress(Exception):
                page.screenshot(path=str(screenshots_dir / "error_screenshot.png"))
        finally:
            context.close()
            browser.close()

    return screenshots_dir


@app.command(name="capture-stlite-preview")
def capture_stlite_preview(
    output: Annotated[
        Path,
        typer.Option(
            "--output",
            help="Output path for the GIF. Default: assets/stlite-preview.gif.",
            metavar="PATH",
        ),
    ] = Path("assets/stlite-preview.gif"),
    url: Annotated[
        str,
        typer.Option(
            "--url",
            help="URL of the stlite demo.",
            metavar="URL",
        ),
    ] = "https://share.stlite.net/#!CgZhcHAucHkS0QQKBmFwcC5weRLGBArDBCIiIlN0cmVhbWxpdCBhcHAgZm9yIHRoZSBweXZpc3RhLWpzIHN0bGl0ZSBkZW1vLiIiIgoKaW1wb3J0IHN0cmVhbWxpdCBhcyBzdAppbXBvcnQgc3RyZWFtbGl0LmNvbXBvbmVudHMudjEgYXMgY29tcG9uZW50cwoKaW1wb3J0IHB5dmlzdGFfanMgYXMgcHYKZnJvbSBweXZpc3RhX2pzIGltcG9ydCBleGFtcGxlcwoKY29sb3IgPSBzdC5zZWxlY3Rib3goCiAgICAiQ29sb3IiLAogICAgWyJncmF5IiwgIndoaXRlIiwgInJlZCIsICJncmVlbiIsICJibHVlIiwgInllbGxvdyIsICJjeWFuIiwgIm1hZ2VudGEiXSwKKQoKb3BhY2l0eSA9IHN0LnNsaWRlcigiT3BhY2l0eSIsIG1pbl92YWx1ZT0wLjAsIG1heF92YWx1ZT0xLjAsIHZhbHVlPTAuOCwgc3RlcD0wLjEpCgpwbG90dGVyID0gcHYuUGxvdHRlcigpCgptZXNoID0gZXhhbXBsZXMuZG93bmxvYWRfYnVubnkoKQoKcGxvdHRlci5hZGRfbWVzaChtZXNoLCBjb2xvcj1jb2xvciwgb3BhY2l0eT1vcGFjaXR5KQoKaHRtbCA9IHBsb3R0ZXIuZ2VuZXJhdGVfc3RhbmRhbG9uZV9odG1sKCkgICMgbm9xYTogU0xGMDAxCmNvbXBvbmVudHMuaHRtbChodG1sLCBoZWlnaHQ9NjAwKRoKcHl2aXN0YS1qcw,=",
    fps: Annotated[
        int,
        typer.Option(
            "--fps",
            help="Frames per second for the GIF. Default: 2.",
            metavar="INT",
        ),
    ] = 2,
    rotate: Annotated[
        bool | None,
        typer.Option(
            "--rotate/--no-rotate",
            help="Rotate the 3D model by mouse drag while capturing screenshots. Default: True.",
        ),
    ] = None,
) -> None:
    """Capture a preview GIF of the stlite demo.

    Automate capturing a preview GIF showing pyvista-js rendering in stlite.
    Requires: playwright, imageio[ffmpeg], pillow.
    """
    import tempfile  # noqa: PLC0415

    if rotate is None:
        rotate = True

    output_path = output

    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        screenshots_dir = _capture_stlite_screenshots(tmp_dir, url, rotate=rotate)

        screenshot_files = list(screenshots_dir.glob("screenshot_*.png"))
        if not screenshot_files:
            logger.error("No screenshots were captured")
            sys.exit(1)

        if not _create_gif(screenshots_dir, output_path, fps=fps):
            logger.error("Failed to create GIF")
            sys.exit(1)

    logger.info("stlite preview GIF saved to: %s", output_path)


# ---------------------------------------------------------------------------
# Try-it-with-JupyterLite example capture
# ---------------------------------------------------------------------------

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
    import time  # noqa: PLC0415

    deadline = time.monotonic() + LITE_FRAME_WAIT_SECONDS
    while time.monotonic() < deadline:
        for frame in page.frames:
            if "lite" in frame.url:
                return frame
        page.wait_for_timeout(2000)
    return None


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
    import io  # noqa: PLC0415

    import numpy as np  # noqa: PLC0415
    from PIL import Image  # noqa: PLC0415

    screenshot = lite.locator(".jp-OutputArea-output canvas").first.screenshot()
    pixels = np.asarray(Image.open(io.BytesIO(screenshot)).convert("RGB"))
    colors = {tuple(color) for color in pixels.reshape(-1, 3).tolist()}
    return len(colors) >= MIN_DISTINCT_CANVAS_COLORS


def _run_try_example(lite: Frame) -> list[str]:
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
    import playwright.sync_api  # noqa: PLC0415

    problems: list[str] = []
    try:
        lite.wait_for_selector(".jp-Notebook .jp-Cell", timeout=180_000)
    except playwright.sync_api.Error as exc:
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
    except playwright.sync_api.Error as exc:
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
    except playwright.sync_api.Error as exc:
        problems.append(f"Could not inspect the render canvas: {exc}")

    return problems


def _capture_try_example_page(url: str, output: Path) -> list[str]:
    """Open *url*, run its embedded JupyterLite example, and capture it.

    Writes ``capture.png`` and ``problems.json`` into *output*.

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
                except playwright.sync_api.Error as exc:
                    problems.append(f"JupyterLite iframe never appeared: {exc}")

                lite = _find_lite_frame(page) if not problems else None
                if lite is None:
                    problems.append("JupyterLite frame never loaded.")
                else:
                    problems.extend(_run_try_example(lite))

                page.wait_for_timeout(5_000)
        except playwright.sync_api.Error as exc:
            problems.append(f"Capture failed with an unexpected error: {exc}")
        finally:
            try:
                page.screenshot(path=str(output / "capture.png"), full_page=True)
            except playwright.sync_api.Error as exc:
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
    import os  # noqa: PLC0415
    import subprocess  # noqa: PLC0415

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
    result = subprocess.run(  # noqa: S603
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


@app.command(name="capture-api-example")
def capture_api_example(
    url: Annotated[
        str,
        typer.Argument(
            help="API documentation page URL to capture.",
            metavar="URL",
        ),
    ],
    output: Annotated[
        Path,
        typer.Option(
            "--output",
            help="Directory for capture.png and problems.json. Default: capture-artifacts.",
            metavar="PATH",
        ),
    ] = Path("capture-artifacts"),
    open_issue: Annotated[
        bool | None,
        typer.Option(
            "--open-issue/--no-open-issue",
            help="Open a bug-report issue with the 'gh' CLI when problems are detected.",
        ),
    ] = None,
) -> None:
    """Capture an API doc page after running its "Try it with JupyterLite" example.

    Opens the documentation page, activates the embedded JupyterLite widget,
    runs all notebook cells, and writes a full-page screenshot
    (``capture.png``) plus a machine-readable problem report
    (``problems.json``). Detected problems include failed notebook loads,
    console errors, HTTP failures, and blank render canvases.

    Exits with status 1 when problems are detected. Requires: playwright,
    pillow, numpy (and the 'gh' CLI for --open-issue).
    """
    if open_issue is None:
        open_issue = False
    problems = _capture_try_example_page(url, output)
    if problems and open_issue:
        _open_bug_report(url, problems, output)
    if problems:
        sys.exit(1)


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
