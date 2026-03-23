"""Tests for the pyvista-js CLI."""

import logging
import pickle
import warnings
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

import pyvista_js as pv
from pyvista_js._cli import (
    _capture_stlite_screenshots,
    _rotate_canvas_with_mouse,
    capture_preview,
    capture_stlite_preview,
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


def test_plot_load_pickle_with_plotter(tmp_path) -> None:
    """``pyvista-js plot --load-pickle`` loads and displays a pickled Plotter."""
    # Create a simple plotter and pickle it
    plotter = pv.Plotter()
    plotter._background_color = (0.5, 0.5, 0.5)  # Set background directly
    pickle_file = tmp_path / "plotter.pkl"

    with pickle_file.open("wb") as f:
        pickle.dump(plotter, f)

    # Test loading the pickle file
    with patch("pyvista_js.Plotter.show"):
        cli_main(["plot", "--load-pickle", str(pickle_file)])


def test_plot_load_pickle_missing_file() -> None:
    """``pyvista-js plot --load-pickle`` exits when pickle file doesn't exist."""
    with pytest.raises(SystemExit) as exc_info:
        cli_main(["plot", "--load-pickle", "nonexistent.pkl"])
    assert exc_info.value.code == 1


def test_plot_load_pickle_invalid_content(tmp_path) -> None:
    """``pyvista-js plot --load-pickle`` exits when pickle contains non-Plotter object."""
    # Create a pickle file with a non-Plotter object
    pickle_file = tmp_path / "invalid.pkl"
    with pickle_file.open("wb") as f:
        pickle.dump({"not": "a plotter"}, f)

    with pytest.raises(SystemExit) as exc_info:
        cli_main(["plot", "--load-pickle", str(pickle_file)])
    assert exc_info.value.code == 1


def test_plot_load_pickle_with_additional_files(tmp_path) -> None:
    """``pyvista-js plot --load-pickle`` can add additional mesh files to loaded plotter."""
    # Create a simple plotter and pickle it
    plotter = pv.Plotter()
    pickle_file = tmp_path / "plotter.pkl"

    with pickle_file.open("wb") as f:
        pickle.dump(plotter, f)

    # Test loading the pickle file with additional mesh
    with patch("pyvista_js.Plotter.show"):
        cli_main(["plot", "--load-pickle", str(pickle_file), str(VTK_FILE)])


def test_plot_no_files_and_no_pickle_exits() -> None:
    """``pyvista-js plot`` exits when neither files nor --load-pickle are provided."""
    with pytest.raises(SystemExit) as exc_info:
        cli_main(["plot"])
    assert exc_info.value.code == 1


def test_plot_load_pickle_with_background_override(tmp_path) -> None:
    """``pyvista-js plot --load-pickle --background`` overrides loaded plotter background."""
    # Create a plotter with one background color
    plotter = pv.Plotter()
    plotter.background_color = "black"
    pickle_file = tmp_path / "plotter.pkl"

    with pickle_file.open("wb") as f:
        pickle.dump(plotter, f)

    # Load with different background color
    with patch("pyvista_js.Plotter.show") as mock_show:
        cli_main(["plot", "--load-pickle", str(pickle_file), "--background", "white"])
        mock_show.assert_called_once()


def test_capture_stlite_preview_with_rotate(tmp_path) -> None:
    """``capture-stlite-preview --rotate`` calls stlite capture with rotation."""
    with (
        patch("pyvista_js._cli._capture_stlite_screenshots") as mock_capture,
        patch("pyvista_js._cli._create_gif", return_value=True),
    ):
        mock_capture.return_value = tmp_path
        (tmp_path / "screenshot_01.png").write_bytes(b"fake")

        capture_stlite_preview(output=tmp_path / "out.gif", url="http://example.com", rotate=True)

        assert mock_capture.call_args.kwargs["rotate"] is True


def test_capture_stlite_preview_with_no_rotate(tmp_path) -> None:
    """``capture-stlite-preview --no-rotate`` calls stlite capture without rotation."""
    with (
        patch("pyvista_js._cli._capture_stlite_screenshots") as mock_capture,
        patch("pyvista_js._cli._create_gif", return_value=True),
    ):
        mock_capture.return_value = tmp_path
        (tmp_path / "screenshot_01.png").write_bytes(b"fake")

        capture_stlite_preview(output=tmp_path / "out.gif", url="http://example.com", rotate=False)

        assert mock_capture.call_args.kwargs["rotate"] is False


def _make_mock_playwright():
    """Create mock Playwright objects for testing screenshot capture."""
    mock_page = MagicMock()
    mock_context = MagicMock()
    mock_context.new_page.return_value = mock_page
    mock_browser = MagicMock()
    mock_browser.new_context.return_value = mock_context
    mock_pw = MagicMock()
    mock_pw.chromium.launch.return_value = mock_browser
    mock_pw_cm = MagicMock()
    mock_pw_cm.__enter__ = MagicMock(return_value=mock_pw)
    mock_pw_cm.__exit__ = MagicMock(return_value=False)
    return mock_pw_cm, mock_page, mock_context, mock_browser


def test_capture_stlite_screenshots_with_rotate(tmp_path) -> None:
    """_capture_stlite_screenshots creates screenshots with rotation."""
    mock_pw_cm, mock_page, mock_context, mock_browser = _make_mock_playwright()

    def fake_screenshot(path: str) -> None:
        Path(path).write_bytes(b"fake-png")

    mock_page.screenshot.side_effect = fake_screenshot

    with patch("playwright.sync_api.sync_playwright", return_value=mock_pw_cm):
        result = _capture_stlite_screenshots(tmp_path, "http://example.com", rotate=True)

    assert result == tmp_path / "screenshots"
    # 1 initial + 13 rotated = 14 screenshots
    assert mock_page.screenshot.call_count == 14
    mock_context.close.assert_called_once()
    mock_browser.close.assert_called_once()


def test_capture_stlite_screenshots_without_rotate(tmp_path) -> None:
    """_capture_stlite_screenshots creates screenshots without rotation."""
    mock_pw_cm, mock_page, mock_context, mock_browser = _make_mock_playwright()

    def fake_screenshot(path: str) -> None:
        Path(path).write_bytes(b"fake-png")

    mock_page.screenshot.side_effect = fake_screenshot

    with patch("playwright.sync_api.sync_playwright", return_value=mock_pw_cm):
        result = _capture_stlite_screenshots(tmp_path, "http://example.com", rotate=False)

    assert result == tmp_path / "screenshots"
    assert mock_page.screenshot.call_count == 14
    mock_context.close.assert_called_once()
    mock_browser.close.assert_called_once()


def test_capture_stlite_screenshots_handles_exception(tmp_path) -> None:
    """_capture_stlite_screenshots handles exceptions gracefully."""
    mock_pw_cm, mock_page, mock_context, mock_browser = _make_mock_playwright()
    mock_page.goto.side_effect = Exception("Connection refused")

    with patch("playwright.sync_api.sync_playwright", return_value=mock_pw_cm):
        result = _capture_stlite_screenshots(tmp_path, "http://example.com", rotate=True)

    assert result == tmp_path / "screenshots"
    mock_context.close.assert_called_once()
    mock_browser.close.assert_called_once()


def test_capture_stlite_preview_no_screenshots(tmp_path) -> None:
    """capture_stlite_preview exits when no screenshots are captured."""
    with patch("pyvista_js._cli._capture_stlite_screenshots") as mock_capture:
        mock_capture.return_value = tmp_path
        # No screenshot files created in tmp_path
        with pytest.raises(SystemExit, match="1"):
            capture_stlite_preview(output=tmp_path / "out.gif", url="http://example.com", rotate=True)


def test_capture_stlite_preview_gif_creation_fails(tmp_path) -> None:
    """capture_stlite_preview exits when GIF creation fails."""
    with (
        patch("pyvista_js._cli._capture_stlite_screenshots") as mock_capture,
        patch("pyvista_js._cli._create_gif", return_value=False),
    ):
        mock_capture.return_value = tmp_path
        (tmp_path / "screenshot_01.png").write_bytes(b"fake")
        with pytest.raises(SystemExit, match="1"):
            capture_stlite_preview(output=tmp_path / "out.gif", url="http://example.com", rotate=True)


def test_capture_stlite_preview_rotate_default(tmp_path) -> None:
    """capture_stlite_preview defaults to rotate=True when None."""
    with (
        patch("pyvista_js._cli._capture_stlite_screenshots") as mock_capture,
        patch("pyvista_js._cli._create_gif", return_value=True),
    ):
        mock_capture.return_value = tmp_path
        (tmp_path / "screenshot_01.png").write_bytes(b"fake")

        capture_stlite_preview(output=tmp_path / "out.gif", url="http://example.com")

        assert mock_capture.call_args.kwargs["rotate"] is True
