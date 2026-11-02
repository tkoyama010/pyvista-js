"""Tests for the ``PlatonicSolid`` factory."""

import pytest

import pyvista_js as pv


def test_platonic_solid() -> None:
    """Test PlatonicSolid stores the scene configuration."""
    solid = pv.PlatonicSolid(kind="dodecahedron", radius=2.0, center=(1, 2, 3))
    scene = solid.to_scene_data()
    assert scene["type"] == "platonicSolid"
    assert scene["kind"] == "dodecahedron"
    assert scene["radius"] == 2.0
    assert scene["center"] == [1.0, 2.0, 3.0]


def test_platonic_solid_defaults() -> None:
    """Test PlatonicSolid default parameters."""
    solid = pv.PlatonicSolid()
    assert solid.to_scene_data()["kind"] == "octahedron"


@pytest.mark.parametrize(
    "kind",
    [
        "tetrahedron",
        "cube",
        "octahedron",
        "icosahedron",
        "dodecahedron",
    ],
)
def test_platonic_solid_all_kinds(kind: str) -> None:
    """Test all Platonic solid kinds are accepted."""
    solid = pv.PlatonicSolid(kind=kind)
    assert solid.to_scene_data()["kind"] == kind


def test_platonic_solid_rejects_bad_kind() -> None:
    """Test PlatonicSolid raises for an unknown kind."""
    with pytest.raises(ValueError, match="kind must be one of"):
        pv.PlatonicSolid(kind="hexahedron")


def test_platonic_solid_rejects_bad_radius() -> None:
    """Test PlatonicSolid raises for a non-positive radius."""
    with pytest.raises(ValueError, match="radius"):
        pv.PlatonicSolid(radius=-1.0)
