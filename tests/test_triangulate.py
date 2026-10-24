"""Tests for ``PolyData.triangulate``."""

import numpy as np

from pyvista_js import Cube, PolyData


def test_triangulate_quad() -> None:
    """Test a quad becomes two triangles."""
    points = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [1.0, 1.0, 0.0], [0.0, 1.0, 0.0]])
    mesh = PolyData(points, np.array([[0, 1, 2, 3]]))
    triangulated = mesh.triangulate()
    assert triangulated.n_faces == 2
    assert triangulated.faces.tolist() == [[0, 1, 2], [0, 2, 3]]


def test_triangulate_flat_format() -> None:
    """Test flat VTK face format is triangulated as well."""
    points = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [1.0, 1.0, 0.0], [0.0, 1.0, 0.0]])
    mesh = PolyData(points, np.concatenate([[4, 0, 1, 2, 3]]))
    triangulated = mesh.triangulate()
    assert triangulated.faces.tolist() == [[0, 1, 2], [0, 2, 3]]


def test_triangulate_keeps_triangles() -> None:
    """Test existing triangles are unchanged."""
    triangle = PolyData(
        np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]]),
        np.array([[0, 1, 2]]),
    )
    triangulated = triangle.triangulate()
    assert triangulated.faces.tolist() == [[0, 1, 2]]


def test_triangulate_keeps_lines() -> None:
    """Test line cells are not triangulated."""
    points = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]])
    mesh = PolyData(points, np.concatenate([[2, 0, 1]]))
    triangulated = mesh.triangulate()
    assert triangulated.faces.tolist() == [[0, 1]]


def test_triangulate_cube() -> None:
    """Test cube keeps n_points and number of faces doubles."""
    cube = Cube()
    triangulated = cube.triangulate()
    assert triangulated.n_points == cube.n_points
    assert triangulated.n_faces == 2 * cube.n_faces
