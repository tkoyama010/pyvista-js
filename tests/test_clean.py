"""Tests for ``PolyData.clean``."""

import numpy as np

import pyvista_js as pv
from pyvista_js import PolyData

rng = np.random.default_rng()


def test_clean() -> None:
    """Test clean merges duplicate points and rebuilds connectivity."""
    points = np.array(
        [
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 0.0],  # duplicate of index 0
        ],
    )
    faces = np.concatenate(
        [
            [3, 0, 1, 0],  # degenerate after merge (0 duplicated)
            [3, 0, 1, 2],
        ],
    )
    mesh = PolyData(points, faces)
    cleaned = mesh.clean()
    assert cleaned.n_points == 3
    assert cleaned.faces.tolist() == [3, 0, 1, 2]


def test_clean_preserves_point_data() -> None:
    """Test clean keeps point data arrays mapped to merged points."""
    points = np.array(
        [
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [0.0, 0.0, 0.0],
        ],
    )
    mesh = PolyData(points)
    mesh.point_data["value"] = np.array([1.0, 2.0, 3.0])
    cleaned = mesh.clean()
    assert cleaned.n_points == 2
    assert np.array_equal(cleaned.point_data["value"], [1.0, 2.0])


def test_clean_with_tolerance() -> None:
    """Test clean merges near-coincident points within point_tolerance."""
    points = np.array(
        [
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [1e-9, 0.0, 0.0],
        ],
    )
    mesh = PolyData(points)
    cleaned = mesh.clean(point_tolerance=1e-6)
    assert cleaned.n_points == 2


def test_clean_sphere() -> None:
    """Test clean on a real sphere source keeps the mesh consistent."""
    sphere = pv.Sphere()
    cleaned = sphere.clean()
    assert cleaned.n_points <= sphere.n_points


def test_clean_no_faces() -> None:
    """Test clean works on a points-only mesh."""
    points = np.array([[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [1.0, 1.0, 1.0]])
    mesh = PolyData(points)
    cleaned = mesh.clean()
    assert cleaned.n_points == 2
