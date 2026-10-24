"""Tests for ``PolyData.slice``."""

import pytest

import pyvista_js as pv
from pyvista_js import Plane, Sphere


def test_slice() -> None:
    """Test slice stores the filter configuration."""
    sliced = Sphere().slice(normal="z")
    assert isinstance(sliced, pv.PolyData)
    last = sliced.to_scene_data()["filters"][-1]
    assert last["type"] == "slice"
    assert last["normal"] == [0.0, 0.0, 1.0]


def test_slice_default_origin_is_center() -> None:
    """Test slice defaults to the mesh bounding-box center."""
    sphere = Sphere()
    last = sphere.slice().to_scene_data()["filters"][-1]
    assert last["origin"] == [0.0, 0.0, 0.0]


def test_slice_custom_vector_and_origin() -> None:
    """Test slice with a vector normal and explicit origin."""
    last = (
        Sphere()
        .slice(
            normal=(1, 0, 1),
            origin=(0.5, 0.5, 0.5),
        )
        .to_scene_data()["filters"][-1]
    )
    assert last["normal"] == [1.0, 0.0, 1.0]
    assert last["origin"] == [0.5, 0.5, 0.5]


def test_slice_offset_plane() -> None:
    """Test slicing a plane mesh that does not include the origin."""
    sliced = Plane().slice(normal="z", origin=(0.0, 0.0, 0.0))
    last = sliced.to_scene_data()["filters"][-1]
    assert last["type"] == "slice"


def test_slice_rejects_bad_normal_string() -> None:
    """Test slice raises for an invalid normal string."""
    with pytest.raises(ValueError, match="Invalid normal string"):
        Sphere().slice(normal="w")


def test_slice_rejects_bad_vector_size() -> None:
    """Test slice raises when a normal tuple has the wrong size."""
    with pytest.raises(ValueError, match="components"):
        Sphere().slice(normal=(1, 0))  # type: ignore[arg-type]
