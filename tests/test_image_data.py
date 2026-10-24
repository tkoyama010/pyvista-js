"""Tests for ``ImageData`` and ``Plotter.add_image``."""

import numpy as np
import pytest

from pyvista_js import ImageData, Plotter


def test_image_data_properties() -> None:
    """Test ImageData dimensions, spacing, origin, and counts."""
    grid = ImageData(dimensions=(8, 6, 4), spacing=(0.5, 0.5, 0.5), origin=(10, 20, 30))
    assert grid.n_points == 192
    assert grid.n_cells == (8 - 1) * (6 - 1) * (4 - 1)
    assert grid.dimensions == (8, 6, 4)
    assert grid.spacing == (0.5, 0.5, 0.5)
    assert grid.origin == (10.0, 20.0, 30.0)


def test_image_data_scene_data() -> None:
    """Test ImageData serializes the scene source."""
    grid = ImageData(dimensions=(4, 4, 4))
    scene = grid.to_scene_data()
    assert scene["type"] == "image"
    assert scene["dimensions"] == [4, 4, 4]
    assert scene["spacing"] == [1.0, 1.0, 1.0]
    assert scene["origin"] == [0.0, 0.0, 0.0]


def test_image_data_point_data() -> None:
    """Test point data arrays flow into scene data."""
    grid = ImageData(dimensions=(2, 2, 2))
    grid.point_data["data"] = np.zeros(grid.n_points)
    scene = grid.to_scene_data()
    assert len(scene["pointData"]) == 1  # the data array


def test_image_data_rejects_bad_dimensions() -> None:
    """Test ImageData raises for non-positive dimensions."""
    with pytest.raises(ValueError, match="dimensions"):
        ImageData(dimensions=(0, 2, 2))


def test_add_image() -> None:
    """Test add_image adds the image actor."""
    plotter = Plotter()
    actor = plotter.add_image(ImageData(dimensions=(4, 4, 4)), color="red")
    assert isinstance(actor, dict)
    assert len(plotter._actors) == 1


def test_image_data_pickle_roundtrip() -> None:
    """Test pickling works."""
    import pickle  # noqa: PLC0415

    grid = ImageData(dimensions=(3, 3, 3))
    restored = pickle.loads(pickle.dumps(grid))  # noqa: S301
    assert restored.dimensions == grid.dimensions
