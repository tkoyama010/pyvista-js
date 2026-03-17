"""Test basic plotter functionality."""

import webbrowser

import numpy as np
import pytest

from pyvista_js import Cube, Cylinder, Plotter, PolyData, Sphere


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


def test_show(monkeypatch) -> None:
    """Test show method opens browser with a file:// URL."""
    opened: list[str] = []

    def _capture(url: str) -> None:
        opened.append(url)

    monkeypatch.setattr(webbrowser, "open", _capture)

    plotter = Plotter()
    plotter.add_mesh(Sphere())
    plotter.show()

    assert len(opened) == 1
    assert opened[0].startswith("file://")


@pytest.mark.parametrize(
    ("mesh_factory", "expected_n_points"),
    [
        (lambda: Sphere(radius=2.0, center=(1, 2, 3), theta_resolution=50), 50 * 30),
        (lambda: Cube(center=(0, 0, 0), x_length=3.0, y_length=2.0, z_length=1.0), 8),
        (lambda: Cylinder(radius=1.5, height=4.0, resolution=80), 160),
    ],
)
def test_plotter_mesh_with_parameters(mesh_factory, expected_n_points) -> None:
    """Test plotter correctly handles different mesh types with parameters."""
    plotter = Plotter()
    mesh = mesh_factory()

    plotter.add_mesh(mesh, color="green", opacity=0.6)

    assert len(plotter.actors) == 1
    actor = plotter.actors[0]
    assert isinstance(actor["mesh"], PolyData)
    assert actor["mesh"].n_points == expected_n_points


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
    assert all(isinstance(actor["mesh"], PolyData) for actor in plotter.actors)


def test_background_color_default() -> None:
    """Test default background color."""
    plotter = Plotter()
    assert plotter.background_color == (1.0, 1.0, 1.0)


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


def test_multiple_plotters_have_unique_container_ids() -> None:
    """Test that each Plotter instance gets a unique container ID.

    Regression test for: second plotter.show() renders no output because
    both plotters share the same container ID, causing the second vtk.js
    renderer to attach to the first container instead of its own.
    """
    plotter1 = Plotter()
    plotter2 = Plotter()

    assert plotter1._container_id != plotter2._container_id


def test_show_twice_uses_same_container_id() -> None:
    """Test that calling show() twice on the same plotter reuses its container ID."""
    plotter = Plotter()
    container_id = plotter._container_id

    plotter.add_mesh(Sphere())
    plotter.show()
    plotter.show()

    assert plotter._container_id == container_id


def test_show_custom_container_id() -> None:
    """Test that show() respects an explicitly provided container ID."""
    plotter = Plotter()
    plotter.add_mesh(Sphere())
    plotter.show(container_id="my-custom-container")

    # The instance container_id should be unchanged
    assert plotter._container_id != "my-custom-container"


def test_view_vector_sets_renderer_state() -> None:
    """Test that view_vector stores the vector in the renderer."""
    plotter = Plotter()
    plotter.view_vector((1.0, 0.0, 0.0))

    assert plotter._renderer._view_vector == (1.0, 0.0, 0.0)


def test_view_vector_default_viewup() -> None:
    """Test that default viewup is (0, 1, 0) when not specified."""
    plotter = Plotter()
    plotter.view_vector((0.0, 0.0, 1.0))

    assert plotter._renderer._view_up == (0.0, 1.0, 0.0)


def test_view_vector_custom_viewup() -> None:
    """Test that a custom viewup is stored correctly."""
    plotter = Plotter()
    plotter.view_vector((1.0, 1.0, 0.0), viewup=(0.0, 0.0, 1.0))

    assert plotter._renderer._view_vector == (1.0, 1.0, 0.0)
    assert plotter._renderer._view_up == (0.0, 0.0, 1.0)


@pytest.mark.parametrize(
    "vector",
    [
        (1.0, 0.0, 0.0),  # +X (view from right)
        (-1.0, 0.0, 0.0),  # -X (view from left)
        (0.0, 1.0, 0.0),  # +Y (view from top)
        (0.0, 0.0, 1.0),  # +Z (view from front)
        (1.0, 1.0, 1.0),  # isometric
    ],
)
def test_view_vector_common_directions(vector) -> None:
    """Test view_vector with common viewing directions."""
    plotter = Plotter()
    plotter.add_mesh(Sphere())
    plotter.view_vector(vector)

    assert plotter._renderer._view_vector == tuple(float(v) for v in vector)


def test_add_points_numpy_array() -> None:
    """Test adding points from a numpy array."""
    plotter = Plotter()
    points = np.random.rand(100, 3)  # noqa: NPY002

    plotter.add_points(points, color="red", point_size=10)

    assert len(plotter.actors) == 1
    assert plotter.actors[0]["type"] == "points"
    assert plotter.actors[0]["color"] == "red"
    assert plotter.actors[0]["point_size"] == 10


def test_add_points_default_params() -> None:
    """Test adding points with default parameters."""
    plotter = Plotter()
    points = np.array([[0, 0, 0], [1, 1, 1], [2, 2, 2]])

    plotter.add_points(points)

    assert len(plotter.actors) == 1
    assert plotter.actors[0]["type"] == "points"
    assert plotter.actors[0]["opacity"] == 1.0
    assert plotter.actors[0]["point_size"] == 5.0
    assert plotter.actors[0]["render_points_as_spheres"] is False


def test_add_points_with_opacity() -> None:
    """Test adding points with custom opacity."""
    plotter = Plotter()
    points = np.random.rand(50, 3)  # noqa: NPY002

    plotter.add_points(points, color="blue", opacity=0.5, point_size=8)

    assert len(plotter.actors) == 1
    assert plotter.actors[0]["color"] == "blue"
    assert plotter.actors[0]["opacity"] == 0.5
    assert plotter.actors[0]["point_size"] == 8


def test_add_points_with_spheres() -> None:
    """Test adding points rendered as spheres."""
    plotter = Plotter()
    points = np.random.rand(30, 3)  # noqa: NPY002

    plotter.add_points(
        points,
        color="green",
        point_size=12,
        render_points_as_spheres=True,
    )

    assert len(plotter.actors) == 1
    assert plotter.actors[0]["render_points_as_spheres"] is True
    assert plotter.actors[0]["point_size"] == 12


def test_add_points_rgb_color() -> None:
    """Test adding points with RGB color tuple."""
    plotter = Plotter()
    points = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]])

    plotter.add_points(points, color=(0.8, 0.2, 0.5))

    assert len(plotter.actors) == 1
    assert plotter.actors[0]["color"] == (0.8, 0.2, 0.5)


def test_add_points_polydata() -> None:
    """Test adding points from a PolyData object."""
    plotter = Plotter()
    points_array = np.random.rand(20, 3)  # noqa: NPY002
    polydata = PolyData(points_array)

    plotter.add_points(polydata, color="yellow", point_size=6)

    assert len(plotter.actors) == 1
    assert plotter.actors[0]["type"] == "points"


def test_add_multiple_point_clouds() -> None:
    """Test adding multiple point clouds."""
    plotter = Plotter()

    points1 = np.random.rand(50, 3)  # noqa: NPY002
    points2 = np.random.rand(30, 3) + [2, 0, 0]  # noqa: NPY002, RUF005

    plotter.add_points(points1, color="red", point_size=5)
    plotter.add_points(points2, color="blue", point_size=8)

    assert len(plotter.actors) == 2
    assert plotter.actors[0]["color"] == "red"
    assert plotter.actors[1]["color"] == "blue"


def test_add_points_and_mesh() -> None:
    """Test adding both points and meshes to the same plotter."""
    plotter = Plotter()
    mesh = Sphere()
    points = np.random.rand(40, 3)  # noqa: NPY002

    plotter.add_mesh(mesh, color="white", opacity=0.5)
    plotter.add_points(points, color="red", point_size=10)

    assert len(plotter.actors) == 2
    assert plotter.actors[0].get("type", "mesh") == "mesh"
    assert plotter.actors[1]["type"] == "points"


def test_add_points_invalid_shape() -> None:
    """Test that invalid point array shape raises an error."""
    plotter = Plotter()
    # Wrong shape - should be (n, 3)
    points = np.random.rand(10, 2)  # noqa: NPY002

    with pytest.raises(ValueError, match="Points must be an \\(n, 3\\) array"):
        plotter.add_points(points)


def test_add_points_1d_array() -> None:
    """Test that 1D array raises an error."""
    plotter = Plotter()
    points = np.random.rand(10)  # noqa: NPY002

    with pytest.raises(ValueError, match="Points must be an \\(n, 3\\) array"):
        plotter.add_points(points)


@pytest.mark.parametrize(
    ("color_name", "expected_rgb"),
    [
        ("red", (1.0, 0.0, 0.0)),
        ("green", (0.0, 1.0, 0.0)),
        ("blue", (0.0, 0.0, 1.0)),
        ("yellow", (1.0, 1.0, 0.0)),
        ("cyan", (0.0, 1.0, 1.0)),
        ("magenta", (1.0, 0.0, 1.0)),
    ],
)
def test_add_points_color_names(color_name, expected_rgb) -> None:
    """Test adding points with different color names."""
    plotter = Plotter()
    points = np.random.rand(10, 3)  # noqa: NPY002

    plotter.add_points(points, color=color_name)

    # Check that the renderer converted the color
    actor = plotter.actors[0]["actor"]
    assert actor["color"] == expected_rgb


@pytest.mark.parametrize(
    "point_size",
    [1.0, 5.0, 10.0, 20.0, 50.0],
)
def test_add_points_various_sizes(point_size) -> None:
    """Test adding points with various sizes."""
    plotter = Plotter()
    points = np.random.rand(10, 3)  # noqa: NPY002

    plotter.add_points(points, point_size=point_size)

    assert plotter.actors[0]["point_size"] == point_size

