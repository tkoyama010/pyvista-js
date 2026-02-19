"""Test basic plotter functionality."""

import pytest

from pyvista_js import Cube, Cylinder, Plotter, Sphere


def test_plotter_creation() -> None:
    """Test that a plotter can be created."""
    plotter = Plotter()
    assert plotter is not None
    assert len(plotter.actors) == 0


def test_add_mesh() -> None:
    """Test adding a mesh to the plotter."""
    plotter = Plotter()
    mesh = Sphere()

    plotter.add_mesh(mesh, color="red", opacity=0.8)

    assert len(plotter.actors) == 1
    assert plotter.actors[0]["color"] == "red"
    assert plotter.actors[0]["opacity"] == 0.8


def test_clear() -> None:
    """Test clearing the plotter."""
    plotter = Plotter()
    plotter.add_mesh(Sphere())
    plotter.add_mesh(Sphere())

    assert len(plotter.actors) == 2

    plotter.clear()
    assert len(plotter.actors) == 0


def test_multiple_meshes() -> None:
    """Test adding multiple meshes."""
    plotter = Plotter()

    plotter.add_mesh(Sphere(radius=1.0), color="red")
    plotter.add_mesh(Sphere(radius=0.5, center=(2, 0, 0)), color="blue")

    assert len(plotter.actors) == 2


def test_show(capsys) -> None:
    """Test show method (with mock renderer)."""
    plotter = Plotter()
    plotter.add_mesh(Sphere())

    plotter.show()

    # In mock environment, should print rendering info
    captured = capsys.readouterr()
    assert "Mock:" in captured.out or captured.out == ""  # Either mock or no output


@pytest.mark.parametrize(
    ("mesh_factory", "expected_type", "params"),
    [
        (
            lambda: Sphere(radius=2.0, center=(1, 2, 3), theta_resolution=50),
            "Sphere",
            {"radius": 2.0, "center": (1, 2, 3), "theta_resolution": 50},
        ),
        (
            lambda: Cube(center=(0, 0, 0), x_length=3.0, y_length=2.0, z_length=1.0),
            "Cube",
            {"x_length": 3.0, "y_length": 2.0, "z_length": 1.0},
        ),
        (
            lambda: Cylinder(radius=1.5, height=4.0, resolution=80),
            "Cylinder",
            {"radius": 1.5, "height": 4.0, "resolution": 80},
        ),
    ],
)
def test_plotter_mesh_with_parameters(mesh_factory, expected_type, params) -> None:
    """Test plotter correctly handles different mesh types with parameters."""
    plotter = Plotter()
    mesh = mesh_factory()

    plotter.add_mesh(mesh, color="green", opacity=0.6)

    assert len(plotter.actors) == 1
    actor = plotter.actors[0]
    assert actor["mesh"]._mesh_type == expected_type

    # Check that key parameters are preserved
    for key, value in params.items():
        assert actor["mesh"]._params[key] == value


def test_plotter_all_mesh_types() -> None:
    """Test plotter with all mesh types in one scene."""
    plotter = Plotter()

    sphere = Sphere(radius=1.0)
    cube = Cube(center=(3, 0, 0))
    cylinder = Cylinder(center=(-3, 0, 0), radius=0.5)

    plotter.add_mesh(sphere, color="red")
    plotter.add_mesh(cube, color="green")
    plotter.add_mesh(cylinder, color="blue")

    assert len(plotter.actors) == 3

    # Verify each mesh type is correctly stored
    mesh_types = [actor["mesh"]._mesh_type for actor in plotter.actors]
    assert "Sphere" in mesh_types
    assert "Cube" in mesh_types
    assert "Cylinder" in mesh_types


def test_background_color_default() -> None:
    """Test default background color."""
    plotter = Plotter()
    assert plotter.background_color == (0.2, 0.3, 0.4)


def test_background_color_set_rgb() -> None:
    """Test setting background color with RGB tuple."""
    plotter = Plotter()
    plotter.background_color = (1.0, 1.0, 1.0)
    assert plotter.background_color == (1.0, 1.0, 1.0)
    assert plotter._renderer.background == (1.0, 1.0, 1.0)


def test_background_color_set_string() -> None:
    """Test setting background color with color name."""
    plotter = Plotter()
    plotter.background_color = "white"
    assert plotter.background_color == (1.0, 1.0, 1.0)
    assert plotter._renderer.background == (1.0, 1.0, 1.0)

    plotter.background_color = "black"
    assert plotter.background_color == (0.0, 0.0, 0.0)
    assert plotter._renderer.background == (0.0, 0.0, 0.0)

    plotter.background_color = "red"
    assert plotter.background_color == (1.0, 0.0, 0.0)
    assert plotter._renderer.background == (1.0, 0.0, 0.0)


@pytest.mark.parametrize(
    ("color_name", "expected_rgb"),
    [
        ("white", (1.0, 1.0, 1.0)),
        ("black", (0.0, 0.0, 0.0)),
        ("red", (1.0, 0.0, 0.0)),
        ("green", (0.0, 1.0, 0.0)),
        ("blue", (0.0, 0.0, 1.0)),
        ("yellow", (1.0, 1.0, 0.0)),
        ("cyan", (0.0, 1.0, 1.0)),
        ("magenta", (1.0, 0.0, 1.0)),
        ("gray", (0.5, 0.5, 0.5)),
        ("grey", (0.5, 0.5, 0.5)),
        ("orange", (1.0, 0.647, 0.0)),
        ("purple", (0.5, 0.0, 0.5)),
        ("pink", (1.0, 0.753, 0.796)),
        ("brown", (0.647, 0.165, 0.165)),
    ],
)
def test_background_color_names(color_name, expected_rgb) -> None:
    """Test all supported color names."""
    plotter = Plotter()
    plotter.background_color = color_name
    assert plotter.background_color == expected_rgb
    assert plotter._renderer.background == expected_rgb


def test_background_color_invalid_name() -> None:
    """Test setting background color with invalid color name."""
    plotter = Plotter()
    with pytest.raises(ValueError, match="Unknown color name"):
        plotter.background_color = "invalid_color"


def test_background_color_invalid_rgb_length() -> None:
    """Test setting background color with wrong RGB tuple length."""
    plotter = Plotter()
    with pytest.raises(ValueError, match="RGB color must have 3 values"):
        plotter.background_color = (1.0, 1.0)


def test_background_color_invalid_rgb_range() -> None:
    """Test setting background color with RGB values out of range."""
    plotter = Plotter()
    with pytest.raises(ValueError, match="RGB values must be between 0 and 1"):
        plotter.background_color = (1.5, 0.5, 0.5)

    with pytest.raises(ValueError, match="RGB values must be between 0 and 1"):
        plotter.background_color = (-0.1, 0.5, 0.5)


def test_background_color_invalid_type() -> None:
    """Test setting background color with invalid type."""
    plotter = Plotter()
    with pytest.raises(TypeError, match="Color must be a string or RGB tuple"):
        plotter.background_color = 123


def test_background_color_updates_renderer() -> None:
    """Test that background color updates the renderer."""
    plotter = Plotter()
    plotter.background_color = "white"

    # Check that renderer was updated
    assert plotter._renderer.background == (1.0, 1.0, 1.0)


def test_double_render() -> None:
    """Test that rendering twice does not cause conflicts.

    Regression test for bug where calling show() twice would break rendering
    due to vtk.js renderer conflicts on the same container.
    """
    # First rendering
    plotter = Plotter()
    mesh = Sphere()
    plotter.add_mesh(mesh, color="red", opacity=0.8)
    plotter.show()

    # Second rendering - should not cause errors
    plotter = Plotter()
    mesh = Sphere()
    plotter.add_mesh(mesh, color="red", opacity=0.8)
    plotter.show()

    # If we get here without errors, the test passes
    assert True
