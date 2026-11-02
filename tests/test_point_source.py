"""Tests for the ``PointSource`` factory."""

import pytest

import pyvista_js as pv


def test_point_source() -> None:
    """Test PointSource stores the scene configuration."""
    cloud = pv.PointSource(center=(1, 2, 3), n_points=50, radius=2.0)
    assert cloud.n_points == 50
    scene = cloud.to_scene_data()
    assert scene["type"] == "pointSource"
    assert scene["radius"] == 2.0
    assert scene["nPoints"] == 50
    assert scene["center"] == [1.0, 2.0, 3.0]


def test_point_source_defaults() -> None:
    """Test PointSource default parameters."""
    cloud = pv.PointSource()
    assert cloud.n_points == 100
    assert cloud.to_scene_data()["nPoints"] == 100


def test_point_source_rejects_bad_n_points() -> None:
    """Test PointSource raises for a non-positive number of points."""
    with pytest.raises(ValueError, match="n_points"):
        pv.PointSource(n_points=0)


def test_point_source_rejects_bad_radius() -> None:
    """Test PointSource raises for a non-positive radius."""
    with pytest.raises(ValueError, match="radius"):
        pv.PointSource(radius=-1.0)
