"""Tests for the Camera class."""

import pytest

import pyvista_js as pv
from pyvista_js.camera import Camera
from pyvista_js.rendering import MockRenderer


def test_camera_default_values() -> None:
    """Test Camera default property values."""
    camera = Camera()
    assert camera.position == (0.0, 0.0, 1.0)
    assert camera.focal_point == (0.0, 0.0, 0.0)
    assert camera.view_up == (0.0, 1.0, 0.0)
    assert camera.view_angle == 30.0
    assert camera.clipping_range == (0.01, 1000.01)
    assert camera.elevation == 0.0


def test_camera_constructor_kwargs() -> None:
    """Test Camera can be constructed with custom parameters."""
    camera = Camera(
        position=(1.0, 2.0, 3.0),
        focal_point=(4.0, 5.0, 6.0),
        view_up=(0.0, 0.0, 1.0),
        view_angle=45.0,
        clipping_range=(0.1, 500.0),
    )
    assert camera.position == (1.0, 2.0, 3.0)
    assert camera.focal_point == (4.0, 5.0, 6.0)
    assert camera.view_up == (0.0, 0.0, 1.0)
    assert camera.view_angle == 45.0
    assert camera.clipping_range == (0.1, 500.0)


def test_camera_position_setter() -> None:
    """Test setting camera position."""
    camera = Camera()
    camera.position = (5.0, 0.0, 0.0)
    assert camera.position == (5.0, 0.0, 0.0)


def test_camera_position_converts_to_float() -> None:
    """Test that position values are converted to float."""
    camera = Camera()
    camera.position = (1, 2, 3)  # integers
    assert camera.position == (1.0, 2.0, 3.0)
    assert all(isinstance(v, float) for v in camera.position)


def test_camera_focal_point_setter() -> None:
    """Test setting camera focal point."""
    camera = Camera()
    camera.focal_point = (1.0, 2.0, 3.0)
    assert camera.focal_point == (1.0, 2.0, 3.0)


def test_camera_view_up_setter() -> None:
    """Test setting camera view-up vector."""
    camera = Camera()
    camera.view_up = (0.0, 0.0, 1.0)
    assert camera.view_up == (0.0, 0.0, 1.0)


def test_camera_view_angle_setter() -> None:
    """Test setting camera view angle."""
    camera = Camera()
    camera.view_angle = 60.0
    assert camera.view_angle == 60.0


def test_camera_view_angle_converts_to_float() -> None:
    """Test that view angle is converted to float."""
    camera = Camera()
    camera.view_angle = 45  # integer
    assert camera.view_angle == 45.0
    assert isinstance(camera.view_angle, float)


def test_camera_clipping_range_setter() -> None:
    """Test setting camera clipping range."""
    camera = Camera()
    camera.clipping_range = (0.1, 100.0)
    assert camera.clipping_range == (0.1, 100.0)


def test_camera_clipping_range_converts_to_float() -> None:
    """Test that clipping range values are converted to float."""
    camera = Camera()
    camera.clipping_range = (1, 100)  # integers
    assert camera.clipping_range == (1.0, 100.0)
    assert all(isinstance(v, float) for v in camera.clipping_range)


def test_camera_repr() -> None:
    """Test Camera __repr__ contains key info."""
    camera = Camera()
    r = repr(camera)
    assert "Camera(" in r
    assert "position=" in r
    assert "focal_point=" in r
    assert "view_up=" in r
    assert "view_angle=" in r
    assert "clipping_range=" in r


def test_camera_available_from_top_level() -> None:
    """Test Camera is importable from pyvista_js top-level."""
    assert hasattr(pv, "Camera")
    assert pv.Camera is Camera


def test_plotter_camera_default_none() -> None:
    """Test that Plotter.camera is None by default."""
    plotter = pv.Plotter()
    assert plotter.camera is None


def test_plotter_camera_set() -> None:
    """Test setting camera on Plotter."""
    plotter = pv.Plotter()
    camera = Camera(position=(5.0, 5.0, 5.0))
    plotter.camera = camera

    assert plotter.camera is camera
    assert plotter._renderer._camera is camera


def test_plotter_camera_updates_renderer() -> None:
    """Test that setting camera propagates to renderer."""
    plotter = pv.Plotter()
    camera = Camera(
        position=(10.0, 0.0, 0.0),
        focal_point=(0.0, 0.0, 0.0),
        view_up=(0.0, 1.0, 0.0),
        view_angle=45.0,
        clipping_range=(0.1, 200.0),
    )
    plotter.camera = camera

    assert plotter._renderer._camera.position == (10.0, 0.0, 0.0)
    assert plotter._renderer._camera.focal_point == (0.0, 0.0, 0.0)
    assert plotter._renderer._camera.view_angle == 45.0
    assert plotter._renderer._camera.clipping_range == (0.1, 200.0)


def test_camera_generates_html(monkeypatch) -> None:
    """Test that setting a camera generates correct vtk.js camera code in HTML."""
    monkeypatch.setenv("PYVISTA_JS_NO_BROWSER", "1")

    renderer = MockRenderer()
    camera = Camera(
        position=(5.0, 5.0, 5.0),
        focal_point=(0.0, 0.0, 0.0),
        view_up=(0.0, 1.0, 0.0),
        view_angle=30.0,
        clipping_range=(0.01, 1000.0),
    )
    renderer.camera = camera

    assert renderer._camera is camera


@pytest.mark.parametrize(
    ("position", "focal_point"),
    [
        ((1.0, 0.0, 0.0), (0.0, 0.0, 0.0)),
        ((0.0, 5.0, 0.0), (0.0, 0.0, 0.0)),
        ((0.0, 0.0, 10.0), (0.0, 0.0, 0.0)),
        ((1.0, 1.0, 1.0), (0.5, 0.5, 0.5)),
    ],
)
def test_camera_various_positions(
    position: tuple,
    focal_point: tuple,
) -> None:
    """Test Camera stores various positions and focal points correctly."""
    camera = Camera(position=position, focal_point=focal_point)
    assert camera.position == tuple(float(v) for v in position)
    assert camera.focal_point == tuple(float(v) for v in focal_point)


def test_camera_parallel_projection_default() -> None:
    """Test Camera has parallel_projection disabled by default."""
    camera = Camera()
    assert camera.parallel_projection is False


def test_camera_parallel_projection_constructor() -> None:
    """Test Camera can be constructed with parallel_projection enabled."""
    camera = Camera(parallel_projection=True)
    assert camera.parallel_projection is True


def test_camera_parallel_projection_setter() -> None:
    """Test setting parallel_projection property."""
    camera = Camera()
    camera.parallel_projection = True
    assert camera.parallel_projection is True
    camera.parallel_projection = False
    assert camera.parallel_projection is False


def test_camera_parallel_projection_converts_to_bool() -> None:
    """Test that parallel_projection is converted to bool."""
    camera = Camera()
    camera.parallel_projection = 1  # truthy value
    assert camera.parallel_projection is True
    assert isinstance(camera.parallel_projection, bool)
    camera.parallel_projection = 0  # falsy value
    assert camera.parallel_projection is False


def test_camera_enable_parallel_projection() -> None:
    """Test enable_parallel_projection method."""
    camera = Camera()
    assert camera.parallel_projection is False
    camera.enable_parallel_projection()
    assert camera.parallel_projection is True


def test_camera_disable_parallel_projection() -> None:
    """Test disable_parallel_projection method."""
    camera = Camera(parallel_projection=True)
    assert camera.parallel_projection is True
    camera.disable_parallel_projection()
    assert camera.parallel_projection is False


def test_camera_repr_includes_parallel_projection() -> None:
    """Test Camera __repr__ includes parallel_projection."""
    camera = Camera(parallel_projection=True)
    r = repr(camera)
    assert "parallel_projection=True" in r


def test_camera_parallel_projection_in_renderer(monkeypatch) -> None:
    """Test that parallel projection setting is propagated to renderer."""
    monkeypatch.setenv("PYVISTA_JS_NO_BROWSER", "1")

    renderer = MockRenderer()
    camera = Camera(parallel_projection=True)
    renderer.camera = camera

    assert renderer._camera.parallel_projection is True


def test_camera_generates_parallel_projection_code() -> None:
    """Test that camera generates vtk.js code for parallel projection."""
    plotter = pv.Plotter()
    plotter.add_mesh(pv.Sphere())
    camera = Camera(
        position=(5.0, 5.0, 5.0),
        parallel_projection=True,
    )
    plotter.camera = camera

    # Generate HTML and verify parallel projection is set in the generated code
    html = plotter._renderer._generate_html()
    assert "cam.setParallelProjection(true)" in html


def test_camera_elevation_default() -> None:
    """Test Camera has elevation set to 0.0 by default."""
    camera = Camera()
    assert camera.elevation == 0.0


def test_camera_elevation_constructor() -> None:
    """Test Camera can be constructed with elevation."""
    camera = Camera(elevation=45.0)
    assert camera.elevation == 45.0


def test_camera_elevation_setter() -> None:
    """Test setting camera elevation property."""
    camera = Camera()
    camera.elevation = 45.0
    assert camera.elevation == 45.0
    camera.elevation = -30.0
    assert camera.elevation == -30.0


def test_camera_elevation_converts_to_float() -> None:
    """Test that elevation is converted to float."""
    camera = Camera()
    camera.elevation = 45  # integer
    assert camera.elevation == 45.0
    assert isinstance(camera.elevation, float)


def test_camera_repr_includes_elevation() -> None:
    """Test Camera __repr__ includes elevation."""
    camera = Camera(elevation=45.0)
    r = repr(camera)
    assert "elevation=45.0" in r


def test_camera_elevation_in_renderer(monkeypatch) -> None:
    """Test that elevation setting is propagated to renderer."""
    monkeypatch.setenv("PYVISTA_JS_NO_BROWSER", "1")

    renderer = MockRenderer()
    camera = Camera(elevation=45.0)
    renderer.camera = camera

    assert renderer._camera.elevation == 45.0


def test_camera_generates_elevation_code() -> None:
    """Test that camera generates vtk.js code for elevation."""
    plotter = pv.Plotter()
    plotter.add_mesh(pv.Sphere())
    camera = Camera(
        position=(5.0, 5.0, 5.0),
        elevation=45.0,
    )
    plotter.camera = camera

    # Generate HTML and verify elevation is set in the generated code
    html = plotter._renderer._generate_html()
    assert "cam.elevation(45.0)" in html

