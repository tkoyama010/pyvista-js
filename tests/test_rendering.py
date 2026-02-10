"""Test vtk.js rendering backend."""

from pyvista_js import Sphere
from pyvista_js.rendering import MockRenderer, get_renderer


def test_get_renderer_returns_mock():
    """Test that get_renderer returns MockRenderer in non-Pyodide env."""
    renderer = get_renderer()
    assert isinstance(renderer, MockRenderer)


def test_mock_renderer_creation():
    """Test MockRenderer initialization."""
    renderer = MockRenderer()
    assert renderer is not None
    assert len(renderer.actors) == 0


def test_mock_add_mesh(capsys):
    """Test adding mesh to MockRenderer."""
    renderer = MockRenderer()
    mesh = Sphere()

    actor = renderer.add_mesh_actor(mesh, color='red', opacity=0.8)

    assert len(renderer.actors) == 1
    assert actor['color'] == 'red'
    assert actor['opacity'] == 0.8

    captured = capsys.readouterr()
    assert "Added mesh with" in captured.out


def test_mock_render(capsys):
    """Test MockRenderer render method."""
    renderer = MockRenderer()
    renderer.add_mesh_actor(Sphere())

    renderer.render()

    captured = capsys.readouterr()
    assert "Rendering 1 actors" in captured.out


def test_mock_clear(capsys):
    """Test MockRenderer clear method."""
    renderer = MockRenderer()
    renderer.add_mesh_actor(Sphere())
    renderer.add_mesh_actor(Sphere())

    assert len(renderer.actors) == 2

    renderer.clear()

    assert len(renderer.actors) == 0
    captured = capsys.readouterr()
    assert "Cleared all actors" in captured.out


def test_mock_create_container(capsys):
    """Test MockRenderer container creation."""
    renderer = MockRenderer()

    container = renderer.create_container("test-container")

    assert container is None
    captured = capsys.readouterr()
    assert "Created container 'test-container'" in captured.out
