"""Test package initialization and metadata."""

import pytest

import pyvista_js


def test_import():
    """Test that package can be imported."""
    assert pyvista_js is not None


@pytest.mark.parametrize("attr,expected", [
    ("__version__", "0.1.2"),
    ("__author__", "Tetsuo Koyama"),
    ("__license__", "BSD-3-Clause"),
])
def test_metadata_attributes(attr, expected):
    """Test that metadata attributes exist and have correct values."""
    assert hasattr(pyvista_js, attr)
    assert getattr(pyvista_js, attr) == expected
    assert isinstance(getattr(pyvista_js, attr), str)


@pytest.mark.parametrize("name", [
    "Plotter",
    "Mesh",
    "Sphere",
    "Cube",
    "Cylinder",
])
def test_exports(name):
    """Test that main classes are exported."""
    assert hasattr(pyvista_js, name)


def test_all_attribute():
    """Test that __all__ is properly defined."""
    assert hasattr(pyvista_js, "__all__")
    assert isinstance(pyvista_js.__all__, list)

    expected_exports = ["__version__", "Plotter", "Mesh", "Sphere", "Cube", "Cylinder"]
    for name in expected_exports:
        assert name in pyvista_js.__all__
