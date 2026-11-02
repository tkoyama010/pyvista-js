"""Tests for ``PolyData.__add__`` (mesh combination with ``+``)."""

import numpy as np

from pyvista_js import Cube, PolyData


def test_add_polydata() -> None:
    """Test adding two meshes combines points and cells."""
    mesh1 = Cube()
    mesh2 = Cube(x_length=2.0)
    combined = mesh1 + mesh2
    assert combined.n_points == 48
    assert combined.n_faces == mesh1.n_faces + mesh2.n_faces


def test_add_polydata_reindexes_cells() -> None:
    """Test cells of the second mesh point into the second point block."""
    points1 = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
    points2 = np.array([[2.0, 2.0, 2.0], [3.0, 2.0, 2.0], [2.0, 3.0, 2.0]])
    faces = np.array([[0, 1, 2]])
    mesh1 = PolyData(points1, faces)
    mesh2 = PolyData(points2, faces)
    combined = mesh1 + mesh2
    assert combined.faces.tolist() == [[0, 1, 2], [3, 4, 5]]


def test_add_polydata_with_points_only() -> None:
    """Test adding a points-only mesh to a mesh with faces."""
    mesh1 = Cube()
    points = np.array([[5.0, 5.0, 5.0], [6.0, 6.0, 6.0]])
    mesh2 = PolyData(points)
    combined = mesh1 + mesh2
    assert combined.n_points == mesh1.n_points + 2
    assert combined.n_faces == mesh1.n_faces


def test_add_polydata_preserves_scalars() -> None:
    """Test scalars are concatenated and filled with NaN when missing."""
    mesh1 = Cube()
    mesh1.point_data["value"] = np.arange(mesh1.n_points, dtype=float)
    mesh2 = Cube()
    combined = mesh1 + mesh2
    assert "value" in combined.point_data
    values = combined.point_data["value"]
    assert values[: mesh1.n_points].tolist() == list(range(mesh1.n_points))
    assert np.isnan(values[mesh1.n_points :]).all()
