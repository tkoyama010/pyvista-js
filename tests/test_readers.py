"""Test readers module."""

from pathlib import Path

import numpy as np
import pytest

from pyvista_js import OBJReader, PLYReader, PolyDataReader

DATA_DIR = Path(__file__).parent / "data"
TRIANGLE_VTK = DATA_DIR / "triangle.vtk"
TRIANGLE_PLY = DATA_DIR / "triangle.ply"
TRIANGLE_OBJ = DATA_DIR / "triangle.obj"


# --- PolyDataReader tests ---


def test_poly_data_reader_path() -> None:
    """Test that the reader exposes the path property."""
    reader = PolyDataReader(TRIANGLE_VTK)
    assert reader.path == TRIANGLE_VTK


def test_poly_data_reader_read_points() -> None:
    """Test reading points from a VTK file."""
    reader = PolyDataReader(TRIANGLE_VTK)
    mesh = reader.read()

    assert mesh.n_points == 3
    expected = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.5, 1.0, 0.0]])
    assert np.allclose(mesh.points, expected)


def test_poly_data_reader_string_path() -> None:
    """Test that string paths are accepted."""
    reader = PolyDataReader(str(TRIANGLE_VTK))
    mesh = reader.read()
    assert mesh.n_points == 3


@pytest.mark.parametrize(
    ("method", "expected"),
    [
        ("generate_vtk_js_source", "vtkPolyDataReader"),
        ("generate_vtk_js_source", "parseAsText"),
        ("generate_vtk_js_source", "source0"),
        ("get_mapper_setup", "setInputData"),
    ],
)
def test_poly_data_reader_js_output(method: str, expected: str) -> None:
    """Test that generated JavaScript contains expected strings."""
    mesh = PolyDataReader(TRIANGLE_VTK).read()
    result = getattr(mesh, method)(0)
    assert expected in result


@pytest.mark.parametrize(
    ("filename", "content", "error_type", "match"),
    [
        (
            "bad.vtk",
            "INVALID HEADER\nfoo\nASCII\nDATASET POLYDATA\n",
            ValueError,
            "missing version header",
        ),
        (
            "binary.vtk",
            "# vtk DataFile Version 3.0\ntitle\nBINARY\nDATASET POLYDATA\n",
            ValueError,
            "Only ASCII",
        ),
        ("short.vtk", "# vtk DataFile Version 3.0\ntitle\n", ValueError, "too few lines"),
    ],
)
def test_poly_data_reader_invalid_files(
    tmp_path: Path,
    filename: str,
    content: str,
    error_type: type,
    match: str,
) -> None:
    """Test ValueError for various invalid VTK files."""
    bad_file = tmp_path / filename
    bad_file.write_text(content)
    with pytest.raises(error_type, match=match):
        PolyDataReader(bad_file).read()


@pytest.mark.parametrize(
    ("fixture_type", "match"),
    [
        ("not_found", "File not found"),
        ("wrong_ext", "Expected a .vtk file"),
    ],
)
def test_poly_data_reader_init_errors(
    tmp_path: Path,
    fixture_type: str,
    match: str,
) -> None:
    """Test errors raised during reader initialization."""
    if fixture_type == "not_found":
        with pytest.raises(FileNotFoundError, match=match):
            PolyDataReader("nonexistent.vtk")
    else:
        bad_file = tmp_path / "data.txt"
        bad_file.write_text("hello")
        with pytest.raises(ValueError, match=match):
            PolyDataReader(bad_file)


def test_poly_data_reader_no_points(tmp_path: Path) -> None:
    """Test reading a VTK file with no POINTS section yields empty mesh."""
    vtk_file = tmp_path / "empty.vtk"
    vtk_file.write_text(
        "# vtk DataFile Version 3.0\ntitle\nASCII\nDATASET POLYDATA\n",
    )
    mesh = PolyDataReader(vtk_file).read()
    assert mesh.n_points == 0


# --- PLYReader tests ---


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


# --- OBJReader tests ---


def test_obj_reader_path() -> None:
    """Test that the reader exposes the path property."""
    reader = OBJReader(TRIANGLE_OBJ)
    assert reader.path == TRIANGLE_OBJ


def test_obj_reader_read_points() -> None:
    """Test reading points from an OBJ file."""
    reader = OBJReader(TRIANGLE_OBJ)
    mesh = reader.read()

    assert mesh.n_points == 3
    expected = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.5, 1.0, 0.0]])
    assert np.allclose(mesh.points, expected)


def test_obj_reader_string_path() -> None:
    """Test that string paths are accepted."""
    reader = OBJReader(str(TRIANGLE_OBJ))
    mesh = reader.read()
    assert mesh.n_points == 3


@pytest.mark.parametrize(
    ("method", "expected"),
    [
        ("generate_vtk_js_source", "vtkOBJReader"),
        ("generate_vtk_js_source", "parseAsArrayBuffer"),
        ("generate_vtk_js_source", "source0"),
        ("get_mapper_setup", "setInputData"),
    ],
)
def test_obj_reader_js_output(method: str, expected: str) -> None:
    """Test that generated JavaScript contains expected strings."""
    mesh = OBJReader(TRIANGLE_OBJ).read()
    result = getattr(mesh, method)(0)
    assert expected in result


@pytest.mark.parametrize(
    ("fixture_type", "match"),
    [
        ("not_found", "File not found"),
        ("wrong_ext", "Expected a .obj file"),
    ],
)
def test_obj_reader_init_errors(
    tmp_path: Path,
    fixture_type: str,
    match: str,
) -> None:
    """Test errors raised during reader initialization."""
    if fixture_type == "not_found":
        with pytest.raises(FileNotFoundError, match=match):
            OBJReader("nonexistent.obj")
    else:
        bad_file = tmp_path / "data.txt"
        bad_file.write_text("hello")
        with pytest.raises(ValueError, match=match):
            OBJReader(bad_file)


def test_obj_reader_no_vertices(tmp_path: Path) -> None:
    """Test reading an OBJ file with no vertices yields empty mesh."""
    obj_file = tmp_path / "empty.obj"
    obj_file.write_text("# empty obj file\n")
    mesh = OBJReader(obj_file).read()
    assert mesh.n_points == 0
