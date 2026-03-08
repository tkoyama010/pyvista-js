"""Test mesh creation and properties."""

import numpy as np
import pytest

from pyvista_js import Cube, Cylinder, Mesh, Sphere


def test_mesh_creation() -> None:
    """Test basic mesh creation."""
    points = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]])
    mesh = Mesh(points)

    assert mesh.n_points == 3
    assert np.array_equal(mesh.points, points)


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
    mesh = Mesh(points=np.empty((0, 3)))
    r, c = mesh.bounding_sphere

    assert np.isnan(r)
    assert all(np.isnan(x) for x in c)


@pytest.mark.parametrize(
    ("mesh_factory", "expected_radius", "expected_center"),
    [
        (lambda: Sphere(radius=1.5, center=(1.0, 2.0, 3.0)), 1.5, (1.0, 2.0, 3.0)),
        (lambda: Sphere(radius=0.5, center=(0.0, 0.0, 0.0)), 0.5, (0.0, 0.0, 0.0)),
        (lambda: Cube(center=(0.0, 0.0, 0.0), x_length=2.0, y_length=2.0, z_length=2.0),
         3**0.5, (0.0, 0.0, 0.0)),
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
