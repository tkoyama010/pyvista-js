"""Tests for the pyvista-js CLI."""

import logging
import pickle
from pathlib import Path
from unittest.mock import patch

import pytest

from pyvista_js._cli import cli_main

DATA_DIR = Path(__file__).parent / "data"
VTK_FILE = DATA_DIR / "triangle.vtk"
PLY_FILE = DATA_DIR / "triangle.ply"
OBJ_FILE = DATA_DIR / "triangle.obj"


def test_info_logs_version(caplog) -> None:
    """``pyvista-js info`` logs version, Python, and platform lines."""
    with caplog.at_level(logging.INFO, logger="pyvista_js._cli"):
        cli_main(["info"])

    messages = "\n".join(caplog.messages)
    assert "pyvista-js" in messages
    assert "Python" in messages
    assert "Platform" in messages


def test_plot_vtk() -> None:
    """``pyvista-js plot`` runs without error on a .vtk file."""
    with patch("pyvista_js.Plotter.show"):
        cli_main(["plot", str(VTK_FILE)])


def test_plot_ply() -> None:
    """``pyvista-js plot`` runs without error on a .ply file."""
    with patch("pyvista_js.Plotter.show"):
        cli_main(["plot", str(PLY_FILE)])


def test_plot_obj() -> None:
    """``pyvista-js plot`` runs without error on a .obj file."""
    with patch("pyvista_js.Plotter.show"):
        cli_main(["plot", str(OBJ_FILE)])


def test_plot_with_color_and_background() -> None:
    """``--color`` and ``--background`` options are forwarded to the plotter."""
    with patch("pyvista_js.Plotter.show"):
        cli_main(["plot", str(VTK_FILE), "--color", "red", "--background", "white"])


def test_plot_missing_file_exits() -> None:
    """``pyvista-js plot`` exits with code 1 when the file does not exist."""
    with pytest.raises(SystemExit) as exc_info:
        cli_main(["plot", "nonexistent.vtk"])
    assert exc_info.value.code == 1


def test_plot_unsupported_extension_exits(tmp_path) -> None:
    """``pyvista-js plot`` exits with code 1 for unsupported file formats."""
    bad_file = tmp_path / "mesh.stl"
    bad_file.write_text("solid\nendsolid\n")
    with pytest.raises(SystemExit) as exc_info:
        cli_main(["plot", str(bad_file)])
    assert exc_info.value.code == 1


def test_plot_with_pickle_option(tmp_path) -> None:
    """``--pickle`` option saves the Plotter object to a file."""
    pickle_file = tmp_path / "plotter.pkl"
    with patch("pyvista_js.Plotter.show"):
        cli_main(["plot", str(VTK_FILE), "--pickle", str(pickle_file)])

    # Verify pickle file was created
    assert pickle_file.exists()

    # Load and verify the plotter
    with pickle_file.open("rb") as f:
        plotter = pickle.load(f)  # noqa: S301

    assert len(plotter.actors) == 1
    assert plotter.actors[0]["mesh"].n_points == 3


def test_plot_with_pickle_and_options(tmp_path) -> None:
    """``--pickle`` option preserves color, background, and opacity settings."""
    pickle_file = tmp_path / "plotter_with_options.pkl"
    with patch("pyvista_js.Plotter.show"):
        cli_main([
            "plot",
            str(VTK_FILE),
            "--color",
            "red",
            "--background",
            "white",
            "--opacity",
            "0.5",
            "--pickle",
            str(pickle_file),
        ])

    # Load and verify the plotter
    with pickle_file.open("rb") as f:
        plotter = pickle.load(f)  # noqa: S301

    assert len(plotter.actors) == 1
    assert plotter.actors[0]["color"] == "red"
    assert plotter.actors[0]["opacity"] == 0.5
    assert plotter.background_color == (1.0, 1.0, 1.0)  # white


def test_plot_with_pickle_multiple_meshes(tmp_path) -> None:
    """``--pickle`` option works with multiple mesh files."""
    pickle_file = tmp_path / "plotter_multi.pkl"
    with patch("pyvista_js.Plotter.show"):
        cli_main([
            "plot",
            str(VTK_FILE),
            str(PLY_FILE),
            "--pickle",
            str(pickle_file),
        ])

    # Load and verify the plotter
    with pickle_file.open("rb") as f:
        plotter = pickle.load(f)  # noqa: S301

    assert len(plotter.actors) == 2

