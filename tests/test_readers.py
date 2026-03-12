"""Test readers module."""

from pathlib import Path

import numpy as np
import pytest

from pyvista_js import PLYReader

DATA_DIR = Path(__file__).parent / "data"
TRIANGLE_PLY = DATA_DIR / "triangle.ply"


def test_ply_reader_path() -> None:
    """Test that the reader exposes the path property."""
    reader = PLYReader(TRIANGLE_PLY)
    assert reader.path == TRIANGLE_PLY


def test_ply_reader_read_points() -> None:
    """Test reading points from a PLY file."""
    reader = PLYReader(TRIANGLE_PLY)
    mesh = reader.read()

    assert mesh.n_points == 3
    expected = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.5, 1.0, 0.0]])
    assert np.allclose(mesh.points, expected)


def test_ply_reader_string_path() -> None:
    """Test that string paths are accepted."""
    reader = PLYReader(str(TRIANGLE_PLY))
    mesh = reader.read()
    assert mesh.n_points == 3


@pytest.mark.parametrize(
    ("method", "expected"),
    [
        ("generate_vtk_js_source", "vtkPLYReader"),
        ("generate_vtk_js_source", "parseAsArrayBuffer"),
        ("generate_vtk_js_source", "source0"),
        ("get_mapper_setup", "setInputData"),
    ],
)
def test_ply_reader_js_output(method: str, expected: str) -> None:
    """Test that generated JavaScript contains expected strings."""
    mesh = PLYReader(TRIANGLE_PLY).read()
    result = getattr(mesh, method)(0)
    assert expected in result


@pytest.mark.parametrize(
    ("filename", "content", "error_type", "match"),
    [
        (
            "bad.ply",
            "NOT A PLY FILE\nformat ascii 1.0\nend_header\n",
            ValueError,
            "missing 'ply' magic number",
        ),
        (
            "no_header_end.ply",
            "ply\nformat ascii 1.0\nelement vertex 0\n",
            ValueError,
            "missing 'end_header'",
        ),
        (
            "binary.ply",
            "ply\nformat binary_little_endian 1.0\nelement vertex 0\nend_header\n",
            ValueError,
            "Only ASCII",
        ),
        (
            "no_format.ply",
            "ply\nelement vertex 0\nend_header\n",
            ValueError,
            "missing 'format' declaration",
        ),
    ],
)
def test_ply_reader_invalid_files(
    tmp_path: Path,
    filename: str,
    content: str,
    error_type: type,
    match: str,
) -> None:
    """Test ValueError for various invalid PLY files."""
    bad_file = tmp_path / filename
    bad_file.write_text(content)
    with pytest.raises(error_type, match=match):
        PLYReader(bad_file).read()


@pytest.mark.parametrize(
    ("fixture_type", "match"),
    [
        ("not_found", "File not found"),
        ("wrong_ext", "Expected a .ply file"),
    ],
)
def test_ply_reader_init_errors(
    tmp_path: Path,
    fixture_type: str,
    match: str,
) -> None:
    """Test errors raised during reader initialization."""
    if fixture_type == "not_found":
        with pytest.raises(FileNotFoundError, match=match):
            PLYReader("nonexistent.ply")
    else:
        bad_file = tmp_path / "data.txt"
        bad_file.write_text("hello")
        with pytest.raises(ValueError, match=match):
            PLYReader(bad_file)


def test_ply_reader_no_vertices(tmp_path: Path) -> None:
    """Test reading a PLY file with no vertices yields empty mesh."""
    ply_file = tmp_path / "empty.ply"
    ply_file.write_text(
        "ply\nformat ascii 1.0\nelement vertex 0\nend_header\n",
    )
    mesh = PLYReader(ply_file).read()
    assert mesh.n_points == 0
