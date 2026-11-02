"""Tests for ``PolyData.warp_by_scalar``."""

import pytest

import pyvista_js as pv
from pyvista_js import Sphere


def test_warp_by_scalar() -> None:
    """Test warp_by_scalar stores the filter configuration."""
    sphere = Sphere()
    sphere.point_data["data"] = sphere.points[:, 2]
    warped = sphere.warp_by_scalar(scalars="data", factor=0.5)
    assert isinstance(warped, pv.PolyData)
    last = warped.to_scene_data()["filters"][-1]
    assert last["type"] == "warpByScalar"
    assert last["factor"] == 0.5
    assert last["scalarName"] == "data"


def test_warp_by_scalar_defaults() -> None:
    """Test warp_by_scalar default factor."""
    sphere = Sphere()
    sphere.point_data["data"] = sphere.points[:, 2]
    last = sphere.warp_by_scalar().to_scene_data()["filters"][-1]
    assert last["factor"] == 1.0


def test_warp_by_scalar_rejects_bad_sc_name() -> None:
    """Test warp_by_scalar raises for an unknown scalar-array name."""
    sphere = Sphere()
    sphere.point_data["data"] = sphere.points[:, 2]
    with pytest.raises(ValueError, match="No point data array"):
        sphere.warp_by_scalar(scalars="nope")


def test_warp_by_scalar_without_scalars_raises() -> None:
    """Test warp_by_scalar raises when no scalar data exists."""
    sphere = Sphere()
    with pytest.raises(ValueError, match="No scalar data"):
        sphere.warp_by_scalar()
