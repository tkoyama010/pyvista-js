"""Tests for ``PolyData.threshold``."""

import pytest

import pyvista_js as pv
from pyvista_js import Sphere


def test_threshold() -> None:
    """Test threshold stores the filter configuration."""
    sphere = Sphere()
    sphere.point_data["data"] = sphere.points[:, 2]
    thresh = sphere.threshold(0.5, scalars="data")
    scene = thresh.to_scene_data()
    assert isinstance(thresh, pv.PolyData)
    filters = scene["filters"]
    last = filters[-1]
    assert last["type"] == "threshold"
    assert last["lowerValue"] == 0.5
    assert last["scalarName"] == "data"


def test_threshold_range() -> None:
    """Test threshold accepts an explicit range."""
    sphere = Sphere()
    sphere.point_data["data"] = sphere.points[:, 2]
    thresh = sphere.threshold([0.0, 0.5], scalars="data")
    last = thresh.to_scene_data()["filters"][-1]
    assert last["lowerValue"] == 0.0
    assert last["upperValue"] == 0.5


def test_threshold_invert() -> None:
    """Test threshold inversion swaps the range."""
    sphere = Sphere()
    sphere.point_data["data"] = sphere.points[:, 2]
    thresh = sphere.threshold([0.0, 0.5], scalars="data", invert=True)
    last = thresh.to_scene_data()["filters"][-1]
    assert last["lowerValue"] == 0.5
    assert last["upperValue"] == 0.0


def test_threshold_rejects_bad_sc_name() -> None:
    """Test threshold raises for an unknown scalar-array name."""
    sphere = Sphere()
    sphere.point_data["data"] = sphere.points[:, 2]
    with pytest.raises(ValueError, match="No point data array"):
        sphere.threshold(0.5, scalars="nope")


def test_threshold_rejects_bad_range_size() -> None:
    """Test threshold raises when the value tuple is not a pair."""
    sphere = Sphere()
    sphere.point_data["data"] = sphere.points[:, 2]
    with pytest.raises(ValueError, match="single float or a pair"):
        sphere.threshold([1.0, 2.0, 3.0], scalars="data")


def test_threshold_without_scalars_raises() -> None:
    """Test threshold raises when no scalar data exists."""
    sphere = Sphere()
    with pytest.raises(ValueError, match="No scalar data"):
        sphere.threshold(0.5)
