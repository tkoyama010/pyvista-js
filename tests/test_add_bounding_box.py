"""Tests for ``Plotter.add_bounding_box``."""

import numpy as np
import pytest

import pyvista_js as pv
from pyvista_js import Plotter, PolyData


def test_add_bounding_box() -> None:
    """Test add_bounding_box adds an outline mesh actor."""
    plotter = Plotter()
    plotter.add_mesh(pv.Sphere())
    outline = plotter.add_bounding_box()
    assert isinstance(outline, PolyData)
    assert outline.n_points == 8
    assert len(plotter._actors) == 2


def test_add_bounding_box_covers_all_meshes() -> None:
    """Test the bounding box spans both meshes in the scene."""
    plotter = Plotter()
    plotter.add_mesh(PolyData(np.array([[0.0, 0.0, 0.0]])))
    plotter.add_mesh(PolyData(np.array([[2.0, 4.0, 6.0]])))
    outline = plotter.add_bounding_box()
    mins = outline.points.min(axis=0)
    maxs = outline.points.max(axis=0)
    assert mins.tolist() == [0.0, 0.0, 0.0]
    assert maxs.tolist() == [2.0, 4.0, 6.0]


def test_add_bounding_box_without_meshes_raises() -> None:
    """Test add_bounding_box raises when the scene is empty."""
    plotter = Plotter()
    with pytest.raises(ValueError, match="No meshes"):
        plotter.add_bounding_box()
