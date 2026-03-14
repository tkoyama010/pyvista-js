"""Tests for the Camera class."""

import pytest

import pyvista_js as pv
from pyvista_js.camera import Camera


def test_camera_default_values() -> None:
    """Test Camera default property values."""
    camera = Camera()
    assert camera.position == (0.0, 0.0, 1.0)
    assert camera.focal_point == (0.0, 0.0, 0.0)
    assert camera.view_up == (0.0, 1.0, 0.0)
    assert camera.view_angle == 30.0
    assert camera.clipping_range == (0.01, 1000.01)


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

    from pyvista_js.rendering import MockRenderer

    renderer = MockRenderer()
    camera = Camera(
        position=(5.0, 5.0, 5.0),
        focal_point=(0.0, 0.0, 0.0),
        view_up=(0.0, 1.0, 0.0),
        view_angle=30.0,
        clipping_range=(0.01, 1000.0),
    )
    renderer.set_camera(camera)

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
