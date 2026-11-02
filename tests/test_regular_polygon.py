"""Tests for the ``RegularPolygon`` factory."""

import pytest

import pyvista_js as pv


def test_regular_polygon() -> None:
    """Test RegularPolygon stores the scene configuration."""
    polygon = pv.RegularPolygon(n_sides=8, radius=1.5, center=(1, 2, 3))
    scene = polygon.to_scene_data()
    assert scene["type"] == "regularPolygon"
    assert scene["nSides"] == 8
    assert scene["radius"] == 1.5
    assert scene["center"] == [1.0, 2.0, 3.0]


def test_regular_polygon_defaults() -> None:
    """Test RegularPolygon default parameters."""
    polygon = pv.RegularPolygon()
    assert polygon.n_points == 6
    assert polygon.to_scene_data()["nSides"] == 6


def test_regular_polygon_point_count() -> None:
    """Test RegularPolygon has one point per side."""
    assert pv.RegularPolygon(n_sides=9).n_points == 9


@pytest.mark.parametrize("bad_sides", [2, 0, -3])
def test_regular_polygon_rejects_bad_sides(bad_sides: int) -> None:
    """Test RegularPolygon raises for too few sides."""
    with pytest.raises(ValueError, match="n_sides"):
        pv.RegularPolygon(n_sides=bad_sides)


def test_regular_polygon_rejects_bad_radius() -> None:
    """Test RegularPolygon raises for a non-positive radius."""
    with pytest.raises(ValueError, match="radius"):
        pv.RegularPolygon(radius=-1.0)
