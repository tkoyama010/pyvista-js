"""Tests for ``PolyData.smooth_taubin``."""

import pytest

import pyvista_js as pv
from pyvista_js import Cube, Sphere


def test_smooth_taubin() -> None:
    """Test smooth_taubin stores the filter configuration."""
    smoothed = Sphere().smooth_taubin(pass_band=0.01, n_iter=20)
    assert isinstance(smoothed, pv.PolyData)
    last = smoothed.to_scene_data()["filters"][-1]
    assert last["type"] == "smoothTaubin"
    assert last["passBand"] == 0.01
    assert last["nIterations"] == 20


def test_smooth_taubin_defaults() -> None:
    """Test smooth_taubin default parameters."""
    last = Cube().smooth_taubin().to_scene_data()["filters"][-1]
    assert last["passBand"] == 0.001
    assert last["nIterations"] == 15


def test_smooth_taubin_rejects_bad_n_iter() -> None:
    """Test smooth_taubin raises for a non-positive iteration count."""
    with pytest.raises(ValueError, match="n_iter"):
        Sphere().smooth_taubin(n_iter=0)
