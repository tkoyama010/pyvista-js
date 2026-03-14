"""Tests for the pyvista-js CLI."""

import logging
from pathlib import Path
from unittest.mock import patch

import pytest

from pyvista_js._cli import main

DATA_DIR = Path(__file__).parent / "data"
VTK_FILE = DATA_DIR / "triangle.vtk"
PLY_FILE = DATA_DIR / "triangle.ply"
OBJ_FILE = DATA_DIR / "triangle.obj"


def test_info_logs_version(caplog) -> None:
    """``pyvista-js info`` logs version, Python, and platform lines."""
    with caplog.at_level(logging.INFO, logger="pyvista_js._cli"):
        main(["info"])

    messages = "\n".join(caplog.messages)
    assert "pyvista-js" in messages
    assert "Python" in messages
    assert "Platform" in messages


def test_plot_vtk() -> None:
    """``pyvista-js plot`` runs without error on a .vtk file."""
    with patch("pyvista_js.Plotter.show"):
        main(["plot", str(VTK_FILE)])


def test_plot_ply() -> None:
    """``pyvista-js plot`` runs without error on a .ply file."""
    with patch("pyvista_js.Plotter.show"):
        main(["plot", str(PLY_FILE)])


def test_plot_obj() -> None:
    """``pyvista-js plot`` runs without error on a .obj file."""
    with patch("pyvista_js.Plotter.show"):
        main(["plot", str(OBJ_FILE)])


def test_plot_with_color_and_background() -> None:
    """``--color`` and ``--background`` options are forwarded to the plotter."""
    with patch("pyvista_js.Plotter.show"):
        main(["plot", str(VTK_FILE), "--color", "red", "--background", "white"])


def test_plot_missing_file_exits() -> None:
    """``pyvista-js plot`` exits with code 1 when the file does not exist."""
    with pytest.raises(SystemExit) as exc_info:
        main(["plot", "nonexistent.vtk"])
    assert exc_info.value.code == 1


def test_plot_unsupported_extension_exits(tmp_path) -> None:
    """``pyvista-js plot`` exits with code 1 for unsupported file formats."""
    bad_file = tmp_path / "mesh.stl"
    bad_file.write_text("solid\nendsolid\n")
    with pytest.raises(SystemExit) as exc_info:
        main(["plot", str(bad_file)])
    assert exc_info.value.code == 1
