"""Tests for ``PolyData.texture_map_to_sphere``."""

import pytest

import pyvista_js as pv
from pyvista_js import Sphere


def test_texture_map_to_sphere() -> None:
    """Test texture_map_to_sphere stores the filter configuration."""
    textured = Sphere().texture_map_to_sphere(center=(1, 2, 3))
    assert isinstance(textured, pv.PolyData)
    last = textured.to_scene_data()["filters"][-1]
    assert last["type"] == "textureSphere"
    assert last["center"] == [1.0, 2.0, 3.0]


def test_texture_map_to_sphere_defaults() -> None:
    """Test texture_map_to_sphere uses the bounding sphere by default."""
    sphere = Sphere()
    last = sphere.texture_map_to_sphere().to_scene_data()["filters"][-1]
    assert last["center"] == [0.0, 0.0, 0.0]
    assert last["radius"] == 1.0


def test_texture_map_to_sphere_rejects_bad_center() -> None:
    """Test texture_map_to_sphere raises for a wrong-size center."""
    with pytest.raises(ValueError, match="center"):
        Sphere().texture_map_to_sphere(center=(0, 0))  # type: ignore[arg-type]
