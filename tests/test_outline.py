"""Tests for ``PolyData.outline``."""

import numpy as np
import pytest

from pyvista_js import PolyData, Sphere


def test_outline_lines() -> None:
    """Test outline produces 8 corners and 12 box edges as lines."""
    outline = Sphere().outline()
    assert outline.n_points == 8
    flat = outline.faces.reshape(-1)
    assert len(flat) == 36  # 12 edges x (2 + 2 indices)
    assert flat[0::3].tolist() == [2] * 12


def test_outline_generate_faces() -> None:
    """Test generate_faces produces the filled box surface."""
    outline = Sphere().outline(generate_faces=True)
    assert outline.n_points == 8
    assert outline.faces.reshape(-1)[0::5].tolist().count(4) == 6


def test_outline_bounds_match_mesh() -> None:
    """Test the outline corners span the mesh bounding box."""
    mesh = PolyData(
        np.array([[0.0, 0.0, 0.0], [2.0, 4.0, 6.0], [1.0, 2.0, 3.0]]),
    )
    outline = mesh.outline(generate_faces=True)
    mins = outline.points.min(axis=0)
    maxs = outline.points.max(axis=0)
    assert mins.tolist() == [0.0, 0.0, 0.0]
    assert maxs.tolist() == [2.0, 4.0, 6.0]


def test_outline_empty_mesh_raises() -> None:
    """Test outline raises on a mesh without points."""
    mesh = PolyData(np.empty((0, 3)))
    with pytest.raises(ValueError, match="without points"):
        mesh.outline()


def test_outline_scene_data_is_flat_polys() -> None:
    """Test the outline scene data uses the flat VTK polys format."""
    outline = Sphere().outline(generate_faces=True)
    scene = outline.to_scene_data()
    assert scene["type"] == "mesh"
    polys = scene["polys"]
    assert polys[0] == 4
