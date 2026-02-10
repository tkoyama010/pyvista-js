"""Test vtk.js rendering backend."""

import pytest

from pyvista_js import Cube, Cylinder, Sphere
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


@pytest.mark.parametrize("mesh_factory,mesh_type,params", [
    (
        lambda: Sphere(
            radius=2.0, center=(1, 2, 3),
            theta_resolution=40, phi_resolution=50
        ),
        'Sphere',
        {
            'radius': 2.0, 'center': (1, 2, 3),
            'theta_resolution': 40, 'phi_resolution': 50
        }
    ),
    (
        lambda: Cube(
            center=(1, 1, 1), x_length=2.0, y_length=3.0, z_length=4.0
        ),
        'Cube',
        {
            'center': (1, 1, 1), 'x_length': 2.0,
            'y_length': 3.0, 'z_length': 4.0
        }
    ),
    (
        lambda: Cylinder(
            center=(0, 0, 0), radius=1.5, height=3.0, resolution=50
        ),
        'Cylinder',
        {'center': (0, 0, 0), 'radius': 1.5, 'height': 3.0, 'resolution': 50}
    ),
])
def test_mesh_type_rendering(mesh_factory, mesh_type, params):
    """Test that different mesh types render with correct parameters."""
    renderer = MockRenderer()
    mesh = mesh_factory()

    actor = renderer.add_mesh_actor(mesh, color=(1, 0, 0), opacity=0.9)

    assert actor['mesh'] is mesh
    assert hasattr(mesh, '_mesh_type')
    assert mesh._mesh_type == mesh_type
    assert hasattr(mesh, '_params')

    for key, value in params.items():
        assert mesh._params[key] == value


def test_multiple_mesh_types_rendering():
    """Test rendering multiple different mesh types together."""
    renderer = MockRenderer()

    sphere = Sphere(radius=1.0, center=(0, 0, 0))
    cube = Cube(center=(3, 0, 0), x_length=1.5)
    cylinder = Cylinder(center=(6, 0, 0), radius=0.5, height=2.0)

    renderer.add_mesh_actor(sphere, color=(1, 0, 0))
    renderer.add_mesh_actor(cube, color=(0, 1, 0))
    renderer.add_mesh_actor(cylinder, color=(0, 0, 1))

    assert len(renderer.actors) == 3
    assert renderer.actors[0]['mesh']._mesh_type == 'Sphere'
    assert renderer.actors[1]['mesh']._mesh_type == 'Cube'
    assert renderer.actors[2]['mesh']._mesh_type == 'Cylinder'


@pytest.mark.parametrize("mesh_factory,vtk_source_name", [
    (lambda: Sphere(radius=1.0), 'vtkSphereSource'),
    (lambda: Cube(x_length=2.0), 'vtkCubeSource'),
    (lambda: Cylinder(radius=0.5, height=2.0), 'vtkCylinderSource'),
])
def test_html_generation_mesh_sources(mesh_factory, vtk_source_name, monkeypatch):
    """Test that HTML generation includes correct vtk.js source types."""
    from pyvista_js import rendering

    # Mock IPython availability
    monkeypatch.setattr(rendering, 'IPYTHON_AVAILABLE', True)

    renderer = rendering.VTKJSRenderer()
    mesh = mesh_factory()
    renderer.add_mesh_actor(mesh, color='red')

    html = renderer._repr_html_()

    assert vtk_source_name in html
    assert 'vtkMapper' in html
    assert 'vtkActor' in html


def test_mesh_parameters_in_html(monkeypatch):
    """Test that mesh parameters are correctly passed to HTML/JS."""
    from pyvista_js import rendering

    # Mock IPython availability
    monkeypatch.setattr(rendering, 'IPYTHON_AVAILABLE', True)

    renderer = rendering.VTKJSRenderer()
    sphere = Sphere(radius=2.5, center=(1, 2, 3), theta_resolution=60)
    renderer.add_mesh_actor(sphere, color='blue')

    html = renderer._repr_html_()

    # Verify parameters are in the generated HTML
    assert 'radius: 2.5' in html
    assert 'center: [1, 2, 3]' in html or 'center: [1.0, 2.0, 3.0]' in html
    assert 'thetaResolution: 60' in html


