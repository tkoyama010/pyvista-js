"""Test mesh creation and properties."""

import webbrowser

import numpy as np
import pytest

from pyvista_js import Cube, Cylinder, Mesh, PolyData, Sphere


def test_mesh_creation() -> None:
    """Test basic mesh creation."""
    points = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]])
    mesh = PolyData(points)

    assert mesh.n_points == 3
    assert np.array_equal(mesh.points, points)


def test_mesh_deprecated() -> None:
    """Test that Mesh emits a DeprecationWarning."""
    points = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]])
    with pytest.warns(DeprecationWarning, match="Mesh is deprecated"):
        mesh = Mesh(points)
    assert isinstance(mesh, PolyData)
    assert mesh.n_points == 3


def test_sphere_creation() -> None:
    """Test sphere primitive creation."""
    sphere = Sphere(radius=1.0)

    assert sphere.n_points > 0
    assert isinstance(sphere.points, np.ndarray)
    assert sphere.points.shape[1] == 3  # 3D coordinates


def test_sphere_parameters() -> None:
    """Test sphere with custom parameters."""
    sphere = Sphere(radius=2.0, center=(1, 2, 3))

    # Check that points are roughly centered at (1, 2, 3)
    center = np.mean(sphere.points, axis=0)
    assert np.allclose(center, [1, 2, 3], atol=0.1)


def test_cube_creation() -> None:
    """Test cube primitive creation."""
    cube = Cube()

    assert cube.n_points == 8
    assert cube.n_faces == 6


def test_cube_size() -> None:
    """Test cube with custom size."""
    cube = Cube(x_length=2.0, y_length=2.0, z_length=2.0)

    # Check bounding box
    mins = np.min(cube.points, axis=0)
    maxs = np.max(cube.points, axis=0)

    assert np.allclose(maxs - mins, [2.0, 2.0, 2.0])


def test_cylinder_creation() -> None:
    """Test cylinder primitive creation."""
    cylinder = Cylinder(radius=1.0, height=2.0)

    assert cylinder.n_points > 0
    assert isinstance(cylinder.points, np.ndarray)


def test_bounding_sphere_empty_mesh() -> None:
    """Test bounding_sphere returns NaN values for a mesh with no points."""
    mesh = PolyData(points=np.empty((0, 3)))
    r, c = mesh.bounding_sphere

    assert np.isnan(r)
    assert all(np.isnan(x) for x in c)


@pytest.mark.parametrize(
    ("mesh_factory", "expected_radius", "expected_center"),
    [
        (lambda: Sphere(radius=1.5, center=(1.0, 2.0, 3.0)), 1.5, (1.0, 2.0, 3.0)),
        (lambda: Sphere(radius=0.5, center=(0.0, 0.0, 0.0)), 0.5, (0.0, 0.0, 0.0)),
        (
            lambda: Cube(center=(0.0, 0.0, 0.0), x_length=2.0, y_length=2.0, z_length=2.0),
            3**0.5,
            (0.0, 0.0, 0.0),
        ),
    ],
)
def test_bounding_sphere(mesh_factory, expected_radius, expected_center) -> None:
    """Test bounding_sphere radius and center for various meshes."""
    mesh = mesh_factory()
    r, c = mesh.bounding_sphere

    assert isinstance(r, float)
    assert isinstance(c, tuple)
    assert len(c) == 3
    assert all(isinstance(x, float) for x in c)
    assert np.isclose(r, expected_radius, atol=1e-3)
    assert np.allclose(c, expected_center, atol=1e-3)


def test_mesh_plot(monkeypatch) -> None:
    """Test that Mesh.plot() creates a plotter, adds the mesh, and shows it."""
    opened: list[str] = []
    monkeypatch.setattr(webbrowser, "open", opened.append)

    sphere = Sphere(radius=1.0)
    sphere.plot(color="red")

    assert len(opened) == 1
    assert opened[0].startswith("file://")


def test_mesh_plot_with_kwargs(monkeypatch) -> None:
    """Test that Mesh.plot() passes kwargs to add_mesh."""
    opened: list[str] = []
    monkeypatch.setattr(webbrowser, "open", opened.append)

    cube = Cube()
    cube.plot(color="blue", opacity=0.5)

    assert len(opened) == 1


def test_generic_mesh_plot(monkeypatch) -> None:
    """Test that generic PolyData instances can also use plot()."""
    opened: list[str] = []
    monkeypatch.setattr(webbrowser, "open", opened.append)

    points = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]])
    mesh = PolyData(points)
    mesh.plot()

    assert len(opened) == 1


def test_shrink_returns_polydata() -> None:
    """Test that shrink returns a PolyData instance."""
    sphere = Sphere()
    shrunk = sphere.shrink(shrink_factor=0.8)
    assert isinstance(shrunk, PolyData)
    assert shrunk.n_points == sphere.n_points


def test_shrink_default_factor() -> None:
    """Test that shrink works with default shrink_factor."""
    cube = Cube()
    shrunk = cube.shrink()
    assert isinstance(shrunk, PolyData)


def test_shrink_vtk_js_source_contains_shrink_logic() -> None:
    """Test that shrunk mesh generates JS with the custom shrink computation."""
    sphere = Sphere()
    shrunk = sphere.shrink(shrink_factor=0.5)
    js_source = shrunk.generate_vtk_js_source(0)
    assert "shrunkPD0" in js_source
    assert "0.5" in js_source
    assert "vtkPolyData" in js_source


def test_shrink_mapper_setup_uses_shrunk_pd() -> None:
    """Test that shrunk mesh mapper uses setInputData with the shrunk polydata."""
    sphere = Sphere()
    shrunk = sphere.shrink(shrink_factor=0.8)
    mapper_code = shrunk.get_mapper_setup(0)
    assert "shrunkPD0" in mapper_code
    assert "setInputData" in mapper_code


def test_shrink_invalid_factor() -> None:
    """Test that an invalid shrink_factor raises ValueError."""
    sphere = Sphere()
    with pytest.raises(ValueError, match="shrink_factor must be between 0 and 1"):
        sphere.shrink(shrink_factor=1.5)
    with pytest.raises(ValueError, match="shrink_factor must be between 0 and 1"):
        sphere.shrink(shrink_factor=-0.1)


def test_shrink_preserves_faces() -> None:
    """Test that shrink preserves face information."""
    cube = Cube()
    shrunk = cube.shrink(shrink_factor=0.8)
    assert shrunk.n_faces == cube.n_faces
