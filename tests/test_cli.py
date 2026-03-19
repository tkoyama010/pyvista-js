"""Tests for the pyvista-js CLI."""

import logging
import pickle
import warnings
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from pyvista_js._cli import (
    _rotate_canvas_with_mouse,
    capture_preview,
    cli_main,
)

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
        cli_main(
            [
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
            ],
        )

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
        cli_main(
            [
                "plot",
                str(VTK_FILE),
                str(PLY_FILE),
                "--pickle",
                str(pickle_file),
            ],
        )

    # Load and verify the plotter
    with pickle_file.open("rb") as f:
        plotter = pickle.load(f)  # noqa: S301

    assert len(plotter.actors) == 2


def test_rotate_canvas_with_mouse_performs_drag() -> None:
    """``_rotate_canvas_with_mouse`` performs mouse drag on canvas."""
    page = MagicMock()
    canvas = MagicMock()
    canvas.bounding_box.return_value = {"x": 100, "y": 100, "width": 600, "height": 400}
    page.query_selector.return_value = canvas

    _rotate_canvas_with_mouse(page)

    page.query_selector.assert_called_once_with("canvas")
    canvas.bounding_box.assert_called_once()
    page.mouse.move.assert_called()
    page.mouse.down.assert_called_once()
    page.mouse.up.assert_called_once()


def test_rotate_canvas_with_mouse_handles_missing_canvas() -> None:
    """``_rotate_canvas_with_mouse`` handles gracefully when canvas is not found."""
    page = MagicMock()
    page.query_selector.return_value = None

    _rotate_canvas_with_mouse(page)

    page.query_selector.assert_called_once_with("canvas")
    page.mouse.move.assert_not_called()


def test_rotate_canvas_with_mouse_handles_missing_bounding_box() -> None:
    """``_rotate_canvas_with_mouse`` handles gracefully when bounding box is unavailable."""
    page = MagicMock()
    canvas = MagicMock()
    canvas.bounding_box.return_value = None
    page.query_selector.return_value = canvas

    _rotate_canvas_with_mouse(page)

    page.query_selector.assert_called_once_with("canvas")
    canvas.bounding_box.assert_called_once()
    page.mouse.move.assert_not_called()


def test_capture_preview_no_rotate_emits_deprecation_warning(tmp_path) -> None:
    """``capture-preview`` without ``--rotate`` emits a DeprecationWarning."""
    with (
        warnings.catch_warnings(record=True) as w,
        patch("pyvista_js._cli._capture_screenshots") as mock_capture,
        patch("pyvista_js._cli._create_gif", return_value=True),
    ):
        warnings.simplefilter("always")
        mock_capture.return_value = tmp_path
        (tmp_path / "screenshot_01.png").write_bytes(b"fake")

        capture_preview(output=tmp_path / "out.gif", url="http://example.com")

        deprecation_warnings = [x for x in w if issubclass(x.category, DeprecationWarning)]
        assert len(deprecation_warnings) == 1
        assert "--rotate" in str(deprecation_warnings[0].message)
        assert mock_capture.call_args.kwargs["rotate"] is False


def test_capture_preview_with_rotate_no_warning(tmp_path) -> None:
    """``capture-preview --rotate`` does not emit a DeprecationWarning."""
    with (
        warnings.catch_warnings(record=True) as w,
        patch("pyvista_js._cli._capture_screenshots") as mock_capture,
        patch("pyvista_js._cli._create_gif", return_value=True),
    ):
        warnings.simplefilter("always")
        mock_capture.return_value = tmp_path
        (tmp_path / "screenshot_01.png").write_bytes(b"fake")

        capture_preview(output=tmp_path / "out.gif", url="http://example.com", rotate=True)

        deprecation_warnings = [x for x in w if issubclass(x.category, DeprecationWarning)]
        assert len(deprecation_warnings) == 0
        assert mock_capture.call_args.kwargs["rotate"] is True


def test_capture_preview_with_no_rotate_no_warning(tmp_path) -> None:
    """``capture-preview --no-rotate`` does not emit a DeprecationWarning."""
    with (
        warnings.catch_warnings(record=True) as w,
        patch("pyvista_js._cli._capture_screenshots") as mock_capture,
        patch("pyvista_js._cli._create_gif", return_value=True),
    ):
        warnings.simplefilter("always")
        mock_capture.return_value = tmp_path
        (tmp_path / "screenshot_01.png").write_bytes(b"fake")

        capture_preview(output=tmp_path / "out.gif", url="http://example.com", rotate=False)

        deprecation_warnings = [x for x in w if issubclass(x.category, DeprecationWarning)]
        assert len(deprecation_warnings) == 0
        assert mock_capture.call_args.kwargs["rotate"] is False
