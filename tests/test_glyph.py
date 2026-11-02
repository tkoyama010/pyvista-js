"""Tests for ``PolyData.glyph`` and ``Plotter.add_arrows``."""

import numpy as np
import pytest

import pyvista_js as pv
from pyvista_js import PolyData


def test_glyph_scene() -> None:
    """Test glyph stores the configuration with the vectors array."""
    points = np.zeros((4, 3))
    vectors = np.ones((4, 3))
    mesh = PolyData(points)
    mesh.point_data["vectors"] = vectors
    glyphed = mesh.glyph(factor=2.0)
    assert glyphed.n_points == 4
    scene = glyphed.to_scene_data()
    assert scene["type"] == "glyph"
    assert scene["scaleFactor"] == 2.0
    assert scene["orientationArray"] == "vectors"
    assert len(scene["pointData"]) == 1  # the vectors array


def test_glyph_named_array() -> None:
    """Test glyph accepts a named orientation array."""
    points = np.zeros((4, 3))
    mesh = PolyData(points)
    mesh.point_data["vectors"] = np.ones((4, 3))
    glyphed = mesh.glyph(orient="vectors")
    scene = glyphed.to_scene_data()
    assert scene["orientationArray"] == "vectors"


def test_glyph_geometry_points() -> None:
    """Test glyph serializes custom geometry."""
    points = np.zeros((4, 3))
    mesh = PolyData(points)
    mesh.point_data["vectors"] = np.ones((4, 3))
    geometry = PolyData(np.zeros((2, 3)), np.concatenate([[2, 0, 1]]))
    glyphed = mesh.glyph(geometry=geometry)
    scene = glyphed.to_scene_data()
    assert len(scene["geometryPoints"]) == 6
    assert len(scene["geometryPolys"]) == 3


def test_glyph_rejects_missing_vectors() -> None:
    """Test glyph raises without a vectors array."""
    mesh = PolyData(np.zeros((4, 3)))
    with pytest.raises(ValueError, match="No point data array"):
        mesh.glyph()


def test_glyph_rejects_bad_factor() -> None:
    """Test glyph raises for a negative factor."""
    mesh = PolyData(np.zeros((4, 3)))
    mesh.point_data["vectors"] = np.ones((4, 3))
    with pytest.raises(ValueError, match="factor"):
        mesh.glyph(factor=-1.0)


def test_add_arrows() -> None:
    """Test add_arrows adds a glyph actor to the scene."""
    plotter = pv.Plotter()
    cent = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]])
    direction = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
    arrows = plotter.add_arrows(cent, direction, mag=2.0)
    assert isinstance(arrows, dict)
    assert len(plotter._actors) == 1


def test_add_arrows_rejects_shape_mismatch() -> None:
    """Test add_arrows raises for mismatched cent/direction shapes."""
    plotter = pv.Plotter()
    cent = np.zeros((2, 3))
    direction = np.zeros((3, 3))
    with pytest.raises(ValueError, match="same shape"):
        plotter.add_arrows(cent, direction)
