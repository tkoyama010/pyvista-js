"""Test vtk.js rendering backend."""

import logging

import pytest

from pyvista_js import Cube, Cylinder, Sphere, rendering
from pyvista_js.rendering import MockRenderer, get_renderer


def test_get_renderer_returns_mock() -> None:
    """Test that get_renderer returns MockRenderer in non-Pyodide env."""
    renderer = get_renderer()
    assert isinstance(renderer, MockRenderer)


def test_mock_renderer_creation() -> None:
    """Test MockRenderer initialization."""
    renderer = MockRenderer()
    assert renderer is not None
    assert len(renderer.actors) == 0


def test_mock_add_mesh(caplog) -> None:
    """Test adding mesh to MockRenderer."""
    with caplog.at_level(logging.INFO):
        renderer = MockRenderer()
        mesh = Sphere()

        actor = renderer.add_mesh_actor(mesh, color="red", opacity=0.8)

        assert len(renderer.actors) == 1
        assert actor["color"] == "red"
        assert actor["opacity"] == 0.8

        assert "Added mesh with" in caplog.text


def test_mock_render(caplog) -> None:
    """Test MockRenderer render method."""
    with caplog.at_level(logging.INFO):
        renderer = MockRenderer()
        renderer.add_mesh_actor(Sphere())

        renderer.render()

        assert "Rendering 1 actors" in caplog.text


def test_mock_clear(caplog) -> None:
    """Test MockRenderer clear method."""
    with caplog.at_level(logging.INFO):
        renderer = MockRenderer()
        renderer.add_mesh_actor(Sphere())
        renderer.add_mesh_actor(Sphere())

        assert len(renderer.actors) == 2

        renderer.clear()

        assert len(renderer.actors) == 0
        assert "Cleared all actors" in caplog.text


def test_mock_create_container(caplog) -> None:
    """Test MockRenderer container creation."""
    with caplog.at_level(logging.INFO):
        renderer = MockRenderer()

        container = renderer.create_container("test-container")

        assert container is None
        assert "Created container 'test-container'" in caplog.text


@pytest.mark.parametrize(
    ("mesh_factory", "mesh_type", "params"),
    [
        (
            lambda: Sphere(radius=2.0, center=(1, 2, 3), theta_resolution=40, phi_resolution=50),
            "Sphere",
            {"radius": 2.0, "center": (1, 2, 3), "theta_resolution": 40, "phi_resolution": 50},
        ),
        (
            lambda: Cube(center=(1, 1, 1), x_length=2.0, y_length=3.0, z_length=4.0),
            "Cube",
            {"center": (1, 1, 1), "x_length": 2.0, "y_length": 3.0, "z_length": 4.0},
        ),
        (
            lambda: Cylinder(center=(0, 0, 0), radius=1.5, height=3.0, resolution=50),
            "Cylinder",
            {"center": (0, 0, 0), "radius": 1.5, "height": 3.0, "resolution": 50},
        ),
    ],
)
def test_mesh_type_rendering(mesh_factory, mesh_type, params) -> None:
    """Test that different mesh types render with correct parameters."""
    renderer = MockRenderer()
    mesh = mesh_factory()

    actor = renderer.add_mesh_actor(mesh, color=(1, 0, 0), opacity=0.9)

    assert actor["mesh"] is mesh
    assert hasattr(mesh, "_mesh_type")
    assert mesh._mesh_type == mesh_type
    assert hasattr(mesh, "_params")

    for key, value in params.items():
        assert mesh._params[key] == value


def test_multiple_mesh_types_rendering() -> None:
    """Test rendering multiple different mesh types together."""
    renderer = MockRenderer()

    sphere = Sphere(radius=1.0, center=(0, 0, 0))
    cube = Cube(center=(3, 0, 0), x_length=1.5)
    cylinder = Cylinder(center=(6, 0, 0), radius=0.5, height=2.0)

    renderer.add_mesh_actor(sphere, color=(1, 0, 0))
    renderer.add_mesh_actor(cube, color=(0, 1, 0))
    renderer.add_mesh_actor(cylinder, color=(0, 0, 1))

    assert len(renderer.actors) == 3
    assert renderer.actors[0]["mesh"]._mesh_type == "Sphere"
    assert renderer.actors[1]["mesh"]._mesh_type == "Cube"
    assert renderer.actors[2]["mesh"]._mesh_type == "Cylinder"


@pytest.mark.parametrize(
    ("mesh_factory", "vtk_source_name"),
    [
        (lambda: Sphere(radius=1.0), "vtkSphereSource"),
        (lambda: Cube(x_length=2.0), "vtkCubeSource"),
        (lambda: Cylinder(radius=0.5, height=2.0), "vtkCylinderSource"),
    ],
)
def test_html_generation_mesh_sources(mesh_factory, vtk_source_name, monkeypatch) -> None:
    """Test that HTML generation includes correct vtk.js source types."""
    # Mock IPython availability
    monkeypatch.setattr(rendering, "IPYTHON_AVAILABLE", True)

    renderer = rendering.VTKJSRenderer()
    mesh = mesh_factory()
    renderer.add_mesh_actor(mesh, color="red")

    html = renderer._repr_html_()

    assert vtk_source_name in html
    assert "vtkMapper" in html
    assert "vtkActor" in html


def test_mesh_parameters_in_html(monkeypatch) -> None:
    """Test that mesh parameters are correctly passed to HTML/JS."""
    # Mock IPython availability
    monkeypatch.setattr(rendering, "IPYTHON_AVAILABLE", True)

    renderer = rendering.VTKJSRenderer()
    sphere = Sphere(radius=2.5, center=(1, 2, 3), theta_resolution=60)
    renderer.add_mesh_actor(sphere, color="blue")

    html = renderer._repr_html_()

    # Verify parameters are in the generated HTML
    assert "radius: 2.5" in html
    assert "center: [1, 2, 3]" in html or "center: [1.0, 2.0, 3.0]" in html
    assert "thetaResolution: 60" in html


def test_view_vector_in_html(monkeypatch) -> None:
    """Test that view_vector generates correct camera JS in HTML output."""
    monkeypatch.setattr(rendering, "IPYTHON_AVAILABLE", True)

    renderer = rendering.VTKJSRenderer()
    renderer.add_mesh_actor(Sphere(), color="red")
    renderer.view_vector((1.0, 2.0, 3.0))

    html = renderer._repr_html_()

    assert "getActiveCamera" in html
    assert "getFocalPoint" in html
    assert "getDistance" in html
    assert "cam.setPosition" in html
    assert "dist*1.0/vlen" in html
    assert "dist*2.0/vlen" in html
    assert "dist*3.0/vlen" in html
    assert "setViewUp" in html
    assert "resetCameraClippingRange" in html


def test_view_vector_default_viewup_in_html(monkeypatch) -> None:
    """Test that the default viewup (0, 1, 0) appears in HTML when not specified."""
    monkeypatch.setattr(rendering, "IPYTHON_AVAILABLE", True)

    renderer = rendering.VTKJSRenderer()
    renderer.add_mesh_actor(Sphere())
    renderer.view_vector((0.0, 0.0, 1.0))

    html = renderer._repr_html_()

    assert "setViewUp(0.0, 1.0, 0.0)" in html


def test_view_vector_custom_viewup_in_html(monkeypatch) -> None:
    """Test that a custom viewup appears correctly in HTML."""
    monkeypatch.setattr(rendering, "IPYTHON_AVAILABLE", True)

    renderer = rendering.VTKJSRenderer()
    renderer.add_mesh_actor(Sphere())
    renderer.view_vector((1.0, 0.0, 0.0), viewup=(0.0, 0.0, 1.0))

    html = renderer._repr_html_()

    assert "setViewUp(0.0, 0.0, 1.0)" in html


def test_no_view_vector_no_camera_code(monkeypatch) -> None:
    """Test that no camera override code is generated when view_vector is not called."""
    monkeypatch.setattr(rendering, "IPYTHON_AVAILABLE", True)

    renderer = rendering.VTKJSRenderer()
    renderer.add_mesh_actor(Sphere(), color="blue")

    html = renderer._repr_html_()

    assert "getActiveCamera" not in html
    assert "cam.setPosition" not in html
    assert "{{CAMERA_CODE}}" not in html


def test_mock_renderer_view_vector(caplog) -> None:
    """Test that MockRenderer.view_vector logs the call."""
    with caplog.at_level(logging.INFO):
        renderer = MockRenderer()
        renderer.view_vector((1.0, 0.0, 0.0))

        assert "Set view vector" in caplog.text
        assert "(1.0, 0.0, 0.0)" in caplog.text


def test_mock_renderer_view_vector_with_viewup(caplog) -> None:
    """Test that MockRenderer.view_vector logs vector and viewup."""
    with caplog.at_level(logging.INFO):
        renderer = MockRenderer()
        renderer.view_vector((0.0, 1.0, 0.0), viewup=(0.0, 0.0, 1.0))

        assert "Set view vector" in caplog.text


def test_multiple_meshes_unique_variables(monkeypatch) -> None:
    """Test that multiple meshes use unique variable names in generated JavaScript."""
    # Mock IPython availability
    monkeypatch.setattr(rendering, "IPYTHON_AVAILABLE", True)

    renderer = rendering.VTKJSRenderer()
    mesh1 = Sphere()
    mesh2 = Cube()
    renderer.add_mesh_actor(mesh1, color="red", opacity=0.8)
    renderer.add_mesh_actor(mesh2, color="blue", opacity=0.8)

    html = renderer._repr_html_()

    # Verify unique variable names for each mesh
    assert "source0" in html
    assert "mapper0" in html
    assert "actor0" in html
    assert "source1" in html
    assert "mapper1" in html
    assert "actor1" in html

    # Verify both actors are added to renderer
    assert html.count("renderer.addActor") == 2
    assert "vtkSphereSource" in html
    assert "vtkCubeSource" in html
