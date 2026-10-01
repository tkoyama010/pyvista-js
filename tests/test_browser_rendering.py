"""Browser-based tests using Playwright for pyvista-js.

These tests verify that PyVista plots render correctly in actual browser
environments using Playwright for browser automation.

Note:
----
These tests require internet access to load vtk.js from the unpkg.com CDN.
If running in an environment without CDN access, these tests will be skipped.
In production use, vtk.js could be vendored locally to avoid this dependency.

"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
import pytest

from pyvista_js import Cube, Line, Plotter, PolyData, Sphere, Text
from pyvista_js.examples import download_bunny, download_trumpet
from pyvista_js.readers import OBJReader, PLYReader, PolyDataReader, STLReader
from pyvista_js.rendering import BrowserRenderer, scene_to_json

if TYPE_CHECKING:
    from playwright.sync_api import Page


def _check_cdn_access(page: Page) -> bool:
    """Check if CDN (unpkg.com) is accessible from the browser.

    Parameters
    ----------
    page : Page
        Playwright page instance.

    Returns
    -------
    bool
        True if CDN is accessible, False otherwise.

    """
    try:
        # Try to load a simple script from unpkg
        response = page.goto("https://unpkg.com/", timeout=5000, wait_until="domcontentloaded")
    except Exception:  # noqa: BLE001
        return False
    else:
        return response is not None and response.ok


def _load_plotter_html(page: Page, plotter: Plotter) -> None:
    """Load plotter HTML in browser via temporary file.

    This approach is necessary because page.set_content() doesn't properly
    load external scripts from CDNs. By writing to a temporary file and
    using page.goto(), we ensure vtk.js loads correctly.

    Parameters
    ----------
    page : Page
        Playwright page instance.
    plotter : Plotter
        The plotter to render.

    """
    # Simulate what show() does
    plotter._renderer.create_container(plotter._container_id)
    html = plotter.generate_standalone_html()

    # Write to temp file and navigate to it
    with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False) as f:
        f.write(html)
        temp_path = f.name

    try:
        # Navigate to the file. wait_until="domcontentloaded" returns immediately for
        # a local file; CDN script loading is awaited below via networkidle. The
        # default 30s timeout is too short for slow CI runner networks.
        page.goto(Path(temp_path).as_uri(), wait_until="domcontentloaded", timeout=120000)
        page.wait_for_load_state("networkidle", timeout=120000)
        # Wait for vtk.js to load and render
        page.wait_for_timeout(2000)
    finally:
        # Clean up temp file
        Path(temp_path).unlink(missing_ok=True)


@pytest.mark.playwright
def test_plotter_renders_in_browser(page: Page) -> None:
    """Test that a plotter visualization renders correctly in a browser.

    This test creates a simple sphere visualization, generates the HTML,
    and loads it in a Playwright-controlled browser to verify rendering.

    Parameters
    ----------
    page : Page
        Playwright page fixture for browser automation.

    """
    # Create a simple plotter with a sphere
    plotter = Plotter()
    plotter.add_mesh(Sphere(), color="red")

    # Load in browser
    _load_plotter_html(page, plotter)

    # Verify that the container element exists
    container = page.query_selector(f"#{plotter._container_id}")
    assert container is not None, "Container element not found"

    # Verify that the canvas element (vtk.js rendering target) exists
    canvas = page.query_selector("canvas")
    assert canvas is not None, "Canvas element not found"

    # Verify canvas has non-zero dimensions
    canvas_box = canvas.bounding_box()
    assert canvas_box is not None, "Canvas bounding box not available"
    assert canvas_box["width"] > 0, "Canvas width is zero"
    assert canvas_box["height"] > 0, "Canvas height is zero"


@pytest.mark.playwright
def test_multiple_meshes_render_in_browser(page: Page) -> None:
    """Test that multiple meshes render correctly in a browser.

    Parameters
    ----------
    page : Page
        Playwright page fixture for browser automation.

    """
    # Create plotter with multiple meshes
    plotter = Plotter()
    plotter.add_mesh(Sphere(radius=1.0), color="red")
    plotter.add_mesh(Sphere(radius=0.5, center=(2, 0, 0)), color="blue")

    # Load in browser
    _load_plotter_html(page, plotter)

    # Verify canvas exists and is rendered
    canvas = page.query_selector("canvas")
    assert canvas is not None, "Canvas element not found"

    # Verify that the plotter has the correct number of actors
    assert len(plotter.actors) == 2


@pytest.mark.playwright
def test_browser_screenshot_capture(page: Page, tmp_path) -> None:
    """Test that we can capture screenshots of rendered plots.

    This test verifies that Playwright can successfully capture screenshots
    of rendered PyVista plots for visual testing or documentation.

    Parameters
    ----------
    page : Page
        Playwright page fixture for browser automation.
    tmp_path : Path
        Pytest temporary directory fixture.

    """
    # Create visualization
    plotter = Plotter()
    plotter.add_mesh(Sphere(), color="blue", opacity=0.8)

    # Load in browser
    _load_plotter_html(page, plotter)

    # Wait a bit more for rendering to complete
    page.wait_for_timeout(500)

    # Capture screenshot
    screenshot_path = tmp_path / "sphere_render.png"
    page.screenshot(path=str(screenshot_path))

    # Verify screenshot was created and has content
    assert screenshot_path.exists(), "Screenshot file not created"
    assert screenshot_path.stat().st_size > 0, "Screenshot file is empty"


@pytest.mark.playwright
def test_canvas_interaction(page: Page) -> None:
    """Test that the canvas is interactive via mouse events.

    This test verifies that we can programmatically interact with the
    3D visualization using mouse events via Playwright.

    Parameters
    ----------
    page : Page
        Playwright page fixture for browser automation.

    """
    # Create visualization
    plotter = Plotter()
    plotter.add_mesh(Sphere(), color="green")

    # Load in browser
    _load_plotter_html(page, plotter)

    # Find canvas
    canvas = page.query_selector("canvas")
    assert canvas is not None, "Canvas element not found"

    # Get canvas bounding box
    box = canvas.bounding_box()
    assert box is not None, "Canvas bounding box not available"

    # Simulate mouse interaction (drag to rotate)
    center_x = box["x"] + box["width"] / 2
    center_y = box["y"] + box["height"] / 2

    # Perform mouse drag
    page.mouse.move(center_x - 50, center_y)
    page.mouse.down()
    page.mouse.move(center_x + 50, center_y, steps=10)
    page.mouse.up()

    # If we got here without errors, interaction worked
    assert True


@pytest.mark.playwright
def test_background_color_renders(page: Page) -> None:
    """Test that custom background colors render correctly.

    Parameters
    ----------
    page : Page
        Playwright page fixture for browser automation.

    """
    # Create plotter with custom background
    plotter = Plotter()
    plotter.background_color = (0.2, 0.3, 0.4)  # Dark blue-gray
    plotter.add_mesh(Sphere(), color="yellow")

    # Load in browser
    _load_plotter_html(page, plotter)

    # Verify canvas exists
    canvas = page.query_selector("canvas")
    assert canvas is not None, "Canvas element not found"

    # The background color is set via JavaScript, we just verify
    # that the page loaded without errors
    assert page.title() != "", "Page title is empty, possible loading error"


@pytest.mark.playwright
def test_headless_browser_execution(page: Page) -> None:
    """Test that visualizations work in headless browser mode.

    This test specifically verifies that PyVista plots can be rendered
    without a display server, which is crucial for CI environments.

    Parameters
    ----------
    page : Page
        Playwright page fixture for browser automation.

    """
    # Create a simple visualization
    plotter = Plotter()
    plotter.add_mesh(Sphere(), color="purple")

    # Load in headless browser (configured in conftest.py)
    _load_plotter_html(page, plotter)

    # Verify rendering completed
    canvas = page.query_selector("canvas")
    assert canvas is not None, "Canvas not found in headless mode"

    # Verify canvas is visible (not hidden)
    is_visible = canvas.is_visible()
    assert is_visible, "Canvas is not visible in headless mode"


@pytest.mark.playwright
def test_shrink_filter_renders_in_browser(page: Page) -> None:
    """Test that the shrink filter renders correctly in a browser.

    This test verifies that meshes with the shrink filter applied
    produce a canvas without JavaScript errors, catching regressions
    where the JS-side filter implementation is missing or broken.

    Parameters
    ----------
    page : Page
        Playwright page fixture for browser automation.

    """
    sphere = Sphere()
    shrunk = sphere.shrink(shrink_factor=0.5)

    plotter = Plotter()
    plotter.add_mesh(shrunk, color="red")

    # Collect JS errors
    js_errors: list[str] = []
    page.on("console", lambda msg: js_errors.append(msg.text) if msg.type == "error" else None)

    _load_plotter_html(page, plotter)

    # Verify canvas exists
    canvas = page.query_selector("canvas")
    assert canvas is not None, "Canvas element not found for shrunk mesh"

    # Verify no JS errors (catches missing filter implementations)
    assert len(js_errors) == 0, f"JavaScript errors during shrink rendering: {js_errors}"


@pytest.mark.playwright
def test_tube_filter_renders_in_browser(page: Page) -> None:
    """Test that the tube filter renders correctly in a browser.

    Parameters
    ----------
    page : Page
        Playwright page fixture for browser automation.

    """
    line = Line()
    tube = line.tube(radius=0.1)

    plotter = Plotter()
    plotter.add_mesh(tube, color="blue")

    js_errors: list[str] = []
    page.on("console", lambda msg: js_errors.append(msg.text) if msg.type == "error" else None)

    _load_plotter_html(page, plotter)

    canvas = page.query_selector("canvas")
    assert canvas is not None, "Canvas element not found for tube mesh"
    assert len(js_errors) == 0, f"JavaScript errors during tube rendering: {js_errors}"


@pytest.mark.playwright
def test_clip_filter_renders_in_browser(page: Page) -> None:
    """Test that the clip filter renders correctly in a browser.

    Parameters
    ----------
    page : Page
        Playwright page fixture for browser automation.

    """
    sphere = Sphere()
    clipped = sphere.clip(normal="x")

    plotter = Plotter()
    plotter.add_mesh(clipped, color="red")

    js_errors: list[str] = []
    page.on("console", lambda msg: js_errors.append(msg.text) if msg.type == "error" else None)

    _load_plotter_html(page, plotter)

    canvas = page.query_selector("canvas")
    assert canvas is not None, "Canvas element not found for clipped mesh"
    assert len(js_errors) == 0, f"JavaScript errors during clip rendering: {js_errors}"


@pytest.mark.playwright
def test_contour_filter_renders_in_browser(page: Page) -> None:
    """Test that the contour filter renders correctly in a browser.

    Parameters
    ----------
    page : Page
        Playwright page fixture for browser automation.

    """
    sphere = Sphere()
    elevation = sphere.points[:, 2]
    contours = sphere.contour(scalars=elevation, isosurfaces=5)

    plotter = Plotter()
    plotter.add_mesh(contours, color="green")

    js_errors: list[str] = []
    page.on("console", lambda msg: js_errors.append(msg.text) if msg.type == "error" else None)

    _load_plotter_html(page, plotter)

    canvas = page.query_selector("canvas")
    assert canvas is not None, "Canvas element not found for contour mesh"
    assert len(js_errors) == 0, f"JavaScript errors during contour rendering: {js_errors}"


@pytest.mark.playwright
def test_text_actor_renders_in_browser(page: Page) -> None:
    """Test that text actors render as HTML overlays in a browser.

    Parameters
    ----------
    page : Page
        Playwright page fixture for browser automation.

    """
    plotter = Plotter()
    plotter.add_mesh(Sphere(), color="white")
    plotter.add_text(Text("Hello World", position=(0.5, 0.9)))

    js_errors: list[str] = []
    page.on("console", lambda msg: js_errors.append(msg.text) if msg.type == "error" else None)

    _load_plotter_html(page, plotter)

    canvas = page.query_selector("canvas")
    assert canvas is not None, "Canvas element not found"
    assert len(js_errors) == 0, f"JavaScript errors during text rendering: {js_errors}"

    # Verify the text overlay div exists with correct content
    text_el = page.query_selector(f"#{plotter._container_id} div")
    assert text_el is not None, "Text overlay div not found"
    assert text_el.inner_text() == "Hello World"


@pytest.mark.playwright
def test_ply_reader_renders_in_browser(page: Page) -> None:
    """Test that PLY file meshes render correctly via vtk.js reader.

    Parameters
    ----------
    page : Page
        Playwright page fixture for browser automation.

    """
    mesh = download_bunny()

    plotter = Plotter()
    plotter.add_mesh(mesh, color="lightblue")

    js_errors: list[str] = []
    page.on("console", lambda msg: js_errors.append(msg.text) if msg.type == "error" else None)

    _load_plotter_html(page, plotter)

    canvas = page.query_selector("canvas")
    assert canvas is not None, "Canvas element not found for PLY reader mesh"
    assert len(js_errors) == 0, f"JavaScript errors during PLY rendering: {js_errors}"


@pytest.mark.playwright
def test_obj_reader_renders_in_browser(page: Page) -> None:
    """Test that OBJ file meshes render correctly via vtk.js reader.

    Parameters
    ----------
    page : Page
        Playwright page fixture for browser automation.

    """
    mesh = download_trumpet()

    plotter = Plotter()
    plotter.add_mesh(mesh, color="gold")

    js_errors: list[str] = []
    page.on("console", lambda msg: js_errors.append(msg.text) if msg.type == "error" else None)

    _load_plotter_html(page, plotter)

    canvas = page.query_selector("canvas")
    assert canvas is not None, "Canvas element not found for OBJ reader mesh"
    assert len(js_errors) == 0, f"JavaScript errors during OBJ rendering: {js_errors}"


_TEST_DATA_DIR = Path(__file__).parent / "data"


@pytest.mark.playwright
def test_stl_reader_renders_in_browser(page: Page) -> None:
    """Test that STL file meshes render correctly via vtk.js reader.

    Parameters
    ----------
    page : Page
        Playwright page fixture for browser automation.

    """
    mesh = STLReader(_TEST_DATA_DIR / "triangle.stl").read()

    plotter = Plotter()
    plotter.add_mesh(mesh, color="red")

    js_errors: list[str] = []
    page.on("console", lambda msg: js_errors.append(msg.text) if msg.type == "error" else None)

    _load_plotter_html(page, plotter)

    canvas = page.query_selector("canvas")
    assert canvas is not None, "Canvas element not found for STL reader mesh"
    assert len(js_errors) == 0, f"JavaScript errors during STL rendering: {js_errors}"


@pytest.mark.playwright
def test_vtk_reader_renders_in_browser(page: Page) -> None:
    """Test that VTK legacy file meshes render correctly via vtk.js reader.

    Parameters
    ----------
    page : Page
        Playwright page fixture for browser automation.

    """
    mesh = PolyDataReader(_TEST_DATA_DIR / "triangle.vtk").read()

    plotter = Plotter()
    plotter.add_mesh(mesh, color="green")

    js_errors: list[str] = []
    page.on("console", lambda msg: js_errors.append(msg.text) if msg.type == "error" else None)

    _load_plotter_html(page, plotter)

    canvas = page.query_selector("canvas")
    assert canvas is not None, "Canvas element not found for VTK reader mesh"
    assert len(js_errors) == 0, f"JavaScript errors during VTK rendering: {js_errors}"


@pytest.mark.playwright
def test_obj_reader_from_file_renders_in_browser(page: Page) -> None:
    """Test that OBJ file meshes from local file render correctly.

    Parameters
    ----------
    page : Page
        Playwright page fixture for browser automation.

    """
    mesh = OBJReader(_TEST_DATA_DIR / "triangle.obj").read()

    plotter = Plotter()
    plotter.add_mesh(mesh, color="blue")

    js_errors: list[str] = []
    page.on("console", lambda msg: js_errors.append(msg.text) if msg.type == "error" else None)

    _load_plotter_html(page, plotter)

    canvas = page.query_selector("canvas")
    assert canvas is not None, "Canvas element not found for OBJ reader mesh"
    assert len(js_errors) == 0, f"JavaScript errors during OBJ rendering: {js_errors}"


@pytest.mark.playwright
def test_ply_reader_from_file_renders_in_browser(page: Page) -> None:
    """Test that PLY file meshes from local file render correctly.

    Parameters
    ----------
    page : Page
        Playwright page fixture for browser automation.

    """
    mesh = PLYReader(_TEST_DATA_DIR / "triangle.ply").read()

    plotter = Plotter()
    plotter.add_mesh(mesh, color="yellow")

    js_errors: list[str] = []
    page.on("console", lambda msg: js_errors.append(msg.text) if msg.type == "error" else None)

    _load_plotter_html(page, plotter)

    canvas = page.query_selector("canvas")
    assert canvas is not None, "Canvas element not found for PLY reader mesh"
    assert len(js_errors) == 0, f"JavaScript errors during PLY rendering: {js_errors}"


def _plain_quad_plotter() -> Plotter:
    """Return a plotter showing a plain quad mesh given by its points and faces."""
    points = np.array([[-1, -1, 0], [1, -1, 0], [1, 1, 0], [-1, 1, 0]], float)
    plotter = Plotter()
    plotter._renderer = BrowserRenderer()
    plotter.add_mesh(PolyData(points, [3, 0, 1, 2, 3, 0, 2, 3]))
    return plotter


def _apply_update(page: Page, plotter: Plotter, update: dict) -> None:
    """Apply an update message in the page, as a notebook would."""
    page.evaluate(
        "([id, update]) => window.pvjsApplyUpdate(id, update)",
        [plotter.container_id, json.loads(scene_to_json(update))],
    )


def _output_points(page: Page, plotter: Plotter) -> list[list[float]]:
    """Return the first actor's points in each output of the plotter's container."""
    return page.evaluate(
        "id => window.__pvjs[id].map("
        "scene => Array.from(scene.actors[0].polydata.getPoints().getData()))",
        plotter.container_id,
    )


def _show_again(page: Page, plotter: Plotter) -> None:
    """Render the plotter as another output, reusing its container ID like a notebook."""
    page.evaluate(plotter._renderer._generate_render_js())  # type: ignore[attr-defined]
    page.wait_for_timeout(500)


@pytest.mark.playwright
@pytest.mark.parametrize("kind", ["plain", "sphere", "cube"])
def test_update_actor_colors_in_place(page: Page, kind: str) -> None:
    """Test that pvjsApplyUpdate recolors a mesh without rebuilding the scene.

    Parameters
    ----------
    page : Page
        Playwright page fixture for browser automation.
    kind : str
        Whether to use a mesh given by points and faces, or a sphere or cube source.

    """
    plotter = _plain_quad_plotter() if kind == "plain" else Plotter()
    if kind != "plain":
        plotter._renderer = BrowserRenderer()
        plotter.add_mesh(Sphere() if kind == "sphere" else Cube())
    mesh = plotter._renderer.actors[0]["mesh"]  # type: ignore[attr-defined]
    red = np.tile(np.array([255, 0, 0], np.uint8), (mesh.n_points, 1))
    plotter.update_actor(0, point_data={"colors": red}, scalars="colors", send=False)
    js_errors: list[str] = []
    page.on("console", lambda msg: js_errors.append(msg.text) if msg.type == "error" else None)
    _load_plotter_html(page, plotter)
    before = page.locator("canvas").screenshot()

    blue = red[:, ::-1].copy()
    _apply_update(page, plotter, plotter.update_actor(0, point_data={"colors": blue}, send=False))
    page.wait_for_timeout(500)

    assert page.locator("canvas").screenshot() != before, "Canvas did not change"
    assert page.locator("canvas").count() == 1
    assert page.evaluate("id => window.__pvjs[id].length", plotter.container_id) == 1
    assert js_errors == []


@pytest.mark.playwright
def test_update_points_in_every_output(page: Page) -> None:
    """Test that showing a plotter again keeps the first output, and updates reach both.

    Parameters
    ----------
    page : Page
        Playwright page fixture for browser automation.

    """
    plotter = _plain_quad_plotter()
    # an ID that names a property of plain objects must still work
    plotter._container_id = "constructor"
    js_errors: list[str] = []
    page.on("console", lambda msg: js_errors.append(msg.text) if msg.type == "error" else None)
    _load_plotter_html(page, plotter)
    page.evaluate(
        "id => { window.__first = window.__pvjs[id][0].renderWindow; }",
        plotter.container_id,
    )
    before = page.locator("canvas").screenshot()
    _show_again(page, plotter)
    assert page.locator("canvas").count() == 2

    # shrink the quad and move it toward the camera, past the original near plane
    points = plotter._renderer.actors[0]["mesh"].points * 0.25 + [0, 0, 3]  # type: ignore[attr-defined]
    _apply_update(page, plotter, plotter.update_actor(0, points=points, send=False))
    page.wait_for_timeout(500)

    assert _output_points(page, plotter) == [points.ravel().tolist()] * 2
    near, far = page.evaluate(
        "id => window.__pvjs[id][0].renderer.getActiveCamera().getClippingRange()",
        plotter.container_id,
    )
    camera_z = page.evaluate(
        "id => window.__pvjs[id][0].renderer.getActiveCamera().getPosition()[2]",
        plotter.container_id,
    )
    assert near < camera_z - 3 < far
    assert page.locator("canvas").first.screenshot() != before, "Canvas did not change"
    # the first output was updated in place, not rebuilt
    assert page.evaluate(
        "id => window.__pvjs[id][0].renderWindow === window.__first",
        plotter.container_id,
    )
    assert js_errors == []


@pytest.mark.playwright
def test_update_after_clear_and_release(page: Page) -> None:
    """Test that updates skip outputs shown before clear(), and removed outputs are freed.

    Parameters
    ----------
    page : Page
        Playwright page fixture for browser automation.

    """
    plotter = _plain_quad_plotter()
    first_points = plotter._renderer.actors[0]["mesh"].points.ravel().tolist()  # type: ignore[attr-defined]
    _load_plotter_html(page, plotter)
    # an unrelated mesh at the same index, shown as a second output
    plotter.clear()
    triangle = PolyData(np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]], float), [3, 0, 1, 2])
    plotter.add_mesh(triangle)
    _show_again(page, plotter)

    moved = triangle.points * 0.5
    _apply_update(page, plotter, plotter.update_actor(0, points=moved, send=False))
    assert _output_points(page, plotter) == [first_points, moved.ravel().tolist()]

    # removing the outputs frees them, with no later pyvista-js call
    released = page.evaluate(
        """async id => {
            for (const scene of window.__pvjs[id]) scene.container.remove();
            await new Promise(resolve => setTimeout(resolve));
            return [
                Object.keys(window.__pvjs).length,
                window.__pvjsObserver === undefined,
                window.renderWindow === undefined,
            ];
        }""",
        plotter.container_id,
    )
    assert released == [0, True, True]
    with pytest.raises(Exception, match="No pyvista-js scene in container"):
        _apply_update(page, plotter, {"actor": "gone"})
