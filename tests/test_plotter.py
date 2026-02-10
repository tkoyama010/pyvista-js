"""Test basic plotter functionality."""

from pyvista_js import Plotter, Sphere


def test_plotter_creation():
    """Test that a plotter can be created."""
    plotter = Plotter()
    assert plotter is not None
    assert len(plotter.actors) == 0


def test_add_mesh():
    """Test adding a mesh to the plotter."""
    plotter = Plotter()
    mesh = Sphere()

    plotter.add_mesh(mesh, color='red', opacity=0.8)

    assert len(plotter.actors) == 1
    assert plotter.actors[0]['color'] == 'red'
    assert plotter.actors[0]['opacity'] == 0.8


def test_clear():
    """Test clearing the plotter."""
    plotter = Plotter()
    plotter.add_mesh(Sphere())
    plotter.add_mesh(Sphere())

    assert len(plotter.actors) == 2

    plotter.clear()
    assert len(plotter.actors) == 0


def test_multiple_meshes():
    """Test adding multiple meshes."""
    plotter = Plotter()

    plotter.add_mesh(Sphere(radius=1.0), color='red')
    plotter.add_mesh(Sphere(radius=0.5, center=(2, 0, 0)), color='blue')

    assert len(plotter.actors) == 2


def test_show(capsys):
    """Test show method (with mock renderer)."""
    plotter = Plotter()
    plotter.add_mesh(Sphere())

    plotter.show()

    # In mock environment, should print rendering info
    captured = capsys.readouterr()
    assert "Mock:" in captured.out or captured.out == ""  # Either mock or no output
