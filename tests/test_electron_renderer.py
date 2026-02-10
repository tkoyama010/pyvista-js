"""Test Electron renderer functionality."""

import logging
import os
from unittest.mock import MagicMock, patch

from pyvista_js import Cube, ElectronRenderer, Sphere
from pyvista_js.rendering import MockRenderer, get_renderer


def test_electron_renderer_creation() -> None:
    """Test ElectronRenderer initialization."""
    renderer = ElectronRenderer()
    assert renderer is not None
    assert len(renderer.actors) == 0
    assert renderer.background == (0.2, 0.3, 0.4)


def test_electron_add_mesh(caplog) -> None:
    """Test adding mesh to ElectronRenderer."""
    with caplog.at_level(logging.INFO):
        renderer = ElectronRenderer()
        mesh = Sphere()

        actor = renderer.add_mesh_actor(mesh, color="red", opacity=0.8)

        assert len(renderer.actors) == 1
        assert actor["color"] == (1.0, 0.0, 0.0)  # red converted to RGB
        assert actor["opacity"] == 0.8

        assert "Added mesh with" in caplog.text


def test_electron_clear(caplog) -> None:
    """Test ElectronRenderer clear method."""
    with caplog.at_level(logging.INFO):
        renderer = ElectronRenderer()
        renderer.add_mesh_actor(Sphere())
        renderer.add_mesh_actor(Sphere())

        assert len(renderer.actors) == 2

        renderer.clear()

        assert len(renderer.actors) == 0
        assert "Cleared all actors" in caplog.text


def test_electron_create_container() -> None:
    """Test ElectronRenderer container creation."""
    renderer = ElectronRenderer()
    renderer.create_container("test-container")
    assert renderer.container_id == "test-container"


def test_electron_set_background() -> None:
    """Test setting background color."""
    renderer = ElectronRenderer()
    renderer.set_background((1.0, 1.0, 1.0))
    assert renderer.background == (1.0, 1.0, 1.0)


def test_electron_html_generation() -> None:
    """Test HTML generation for Electron renderer."""
    renderer = ElectronRenderer()
    sphere = Sphere(radius=2.0, center=(1, 2, 3))
    renderer.add_mesh_actor(sphere, color="blue", opacity=0.9)

    html = renderer._generate_html()

    # Verify HTML structure
    assert "<!DOCTYPE html>" in html
    assert "vtk.js" in html
    assert "vtkSphereSource" in html
    assert "radius: 2.0" in html
    assert "center: [1, 2, 3]" in html or "center: [1.0, 2.0, 3.0]" in html
    assert "PyVista-JS Viewer" in html


def test_electron_multiple_meshes() -> None:
    """Test Electron renderer with multiple meshes."""
    renderer = ElectronRenderer()

    sphere = Sphere(radius=1.0)
    cube = Cube(center=(3, 0, 0))
    renderer.add_mesh_actor(sphere, color="red")
    renderer.add_mesh_actor(cube, color="green")

    assert len(renderer.actors) == 2

    html = renderer._generate_html()

    # Verify both meshes are in HTML
    assert "vtkSphereSource" in html
    assert "vtkCubeSource" in html
    assert "source0" in html
    assert "source1" in html


@patch("subprocess.run")
def test_electron_check_node_available(mock_run) -> None:
    """Test checking if Node.js is available."""
    mock_run.return_value = MagicMock(returncode=0)

    renderer = ElectronRenderer()

    assert renderer._electron_available is True
    mock_run.assert_called_once()


@patch("subprocess.run")
def test_electron_check_node_not_available(mock_run) -> None:
    """Test when Node.js is not available."""
    mock_run.side_effect = FileNotFoundError()

    renderer = ElectronRenderer()

    assert renderer._electron_available is False


def test_get_renderer_with_electron_env() -> None:
    """Test get_renderer returns ElectronRenderer when env var is set."""
    # Save original env var
    original_env = os.environ.get("PYVISTA_JS_BACKEND")

    try:
        os.environ["PYVISTA_JS_BACKEND"] = "electron"
        renderer = get_renderer()
        assert isinstance(renderer, ElectronRenderer)
    finally:
        # Restore original env var
        if original_env is None:
            os.environ.pop("PYVISTA_JS_BACKEND", None)
        else:
            os.environ["PYVISTA_JS_BACKEND"] = original_env


def test_get_renderer_with_mock_env() -> None:
    """Test get_renderer returns MockRenderer when env var is set."""
    # Save original env var
    original_env = os.environ.get("PYVISTA_JS_BACKEND")

    try:
        os.environ["PYVISTA_JS_BACKEND"] = "mock"
        renderer = get_renderer()
        assert isinstance(renderer, MockRenderer)
    finally:
        # Restore original env var
        if original_env is None:
            os.environ.pop("PYVISTA_JS_BACKEND", None)
        else:
            os.environ["PYVISTA_JS_BACKEND"] = original_env


def test_electron_color_conversion() -> None:
    """Test color name to RGB conversion."""
    renderer = ElectronRenderer()

    assert renderer._color_name_to_rgb("red") == (1.0, 0.0, 0.0)
    assert renderer._color_name_to_rgb("green") == (0.0, 1.0, 0.0)
    assert renderer._color_name_to_rgb("blue") == (0.0, 0.0, 1.0)
    assert renderer._color_name_to_rgb("unknown") == (0.5, 0.5, 0.5)


@patch("subprocess.run")
@patch("subprocess.Popen")
def test_electron_render_with_electron_available(mock_popen, mock_run, tmp_path) -> None:
    """Test rendering when Electron is available."""
    # Mock successful Node.js check and npm install
    mock_run.return_value = MagicMock(returncode=0)
    mock_popen.return_value = MagicMock()

    renderer = ElectronRenderer()
    # Override temp_dir to use tmp_path
    renderer.temp_dir = tmp_path

    # Create fake node_modules/electron to skip installation
    (tmp_path / "node_modules" / "electron").mkdir(parents=True)

    renderer.add_mesh_actor(Sphere(), color="red")

    # This should create HTML and attempt to launch Electron
    renderer.render()

    # Check that HTML file was created
    html_file = tmp_path / "viewer.html"
    assert html_file.exists()

    # Check that main.js was created
    main_js_file = tmp_path / "main.js"
    assert main_js_file.exists()

    # Verify Electron was launched
    mock_popen.assert_called_once()


@patch("subprocess.run")
@patch("webbrowser.open")
def test_electron_render_fallback_to_browser(mock_browser_open, mock_run, tmp_path) -> None:
    """Test fallback to browser when Electron is not available."""
    # Mock Node.js not available
    mock_run.side_effect = FileNotFoundError()

    renderer = ElectronRenderer()
    # Override temp_dir to use tmp_path
    renderer.temp_dir = tmp_path

    renderer.add_mesh_actor(Sphere(), color="red")

    # This should create HTML and try to open in browser
    renderer.render()

    # Check that HTML file was created
    html_file = tmp_path / "viewer.html"
    assert html_file.exists()

    # Verify browser was opened
    mock_browser_open.assert_called_once()
