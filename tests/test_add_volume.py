"""Tests for ``Plotter.add_volume``."""

import numpy as np
import pytest

from pyvista_js import ImageData, Plotter


@pytest.fixture
def grid() -> ImageData:
    """Create a small image with scalar data."""
    image = ImageData(dimensions=(4, 4, 4))
    image.point_data["data"] = np.linspace(0.0, 1.0, image.n_points)
    return image


def test_add_volume(grid: ImageData) -> None:
    """Test add_volume builds the volume scene configuration."""
    plotter = Plotter()
    actor = plotter.add_volume(grid, scalars="data", cmap="coolwarm")
    assert isinstance(actor, dict)
    assert len(plotter._actors) == 1


def test_add_volume_scene_type(grid: ImageData) -> None:
    """Test the volume mesh serializes as an imageVolume source."""
    plotter = Plotter()
    _ = plotter.add_volume(grid, scalars="data")
    scene = plotter._actors[0]["mesh"].to_scene_data()
    assert scene["type"] == "imageVolume"
    assert scene["scalars"]["arrayName"] == "data"
    assert scene["scalars"]["range"] == [0.0, 1.0]


def test_add_volume_first_array_default(grid: ImageData) -> None:
    """Test add_volume defaults to the first point data array."""
    plotter = Plotter()
    _ = plotter.add_volume(grid)
    scene = plotter._actors[0]["mesh"].to_scene_data()
    assert scene["scalars"]["arrayName"] == "data"


def test_add_volume_passes_array() -> None:
    """Test add_volume accepts a raw scalar array."""
    plotter = Plotter()
    other = ImageData(dimensions=(4, 4, 4))
    _ = plotter.add_volume(other, scalars=np.linspace(0.0, 1.0, other.n_points))
    scene = plotter._actors[0]["mesh"].to_scene_data()
    assert scene["scalars"]["arrayName"] == "scalars"


def test_add_volume_rejects_unknown_name(grid: ImageData) -> None:
    """Test add_volume raises for an unknown scalar-array name."""
    plotter = Plotter()
    with pytest.raises(ValueError, match="No point data array"):
        plotter.add_volume(grid, scalars="nope")


def test_add_volume_rejects_no_scalars() -> None:
    """Test add_volume raises when the image has no point data."""
    plotter = Plotter()
    with pytest.raises(ValueError, match="No scalar data"):
        plotter.add_volume(ImageData(dimensions=(4, 4, 4)))
