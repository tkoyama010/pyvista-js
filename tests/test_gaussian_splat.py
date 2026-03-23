"""Test Gaussian splat reader module."""

from pathlib import Path

import numpy as np
import pytest

from pyvista_js import GaussianSplatReader

DATA_DIR = Path(__file__).parent / "data"
GAUSSIAN_SPLAT_TEST = DATA_DIR / "gaussian_splat_test.ply"


def test_gaussian_splat_reader_path() -> None:
    """Test that the reader exposes the path property."""
    reader = GaussianSplatReader(GAUSSIAN_SPLAT_TEST)
    assert reader.path == GAUSSIAN_SPLAT_TEST


def test_gaussian_splat_reader_read_points() -> None:
    """Test reading positions from a Gaussian splat file."""
    reader = GaussianSplatReader(GAUSSIAN_SPLAT_TEST)
    mesh = reader.read()

    assert mesh.n_points == 2
    expected = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]])
    assert np.allclose(mesh.points, expected)


def test_gaussian_splat_reader_string_path() -> None:
    """Test that string paths are accepted."""
    reader = GaussianSplatReader(str(GAUSSIAN_SPLAT_TEST))
    mesh = reader.read()
    assert mesh.n_points == 2


@pytest.mark.parametrize(
    ("method", "expected"),
    [
        ("generate_vtk_js_source", "parseGaussianSplatData"),
        ("generate_vtk_js_source", "source0"),
        ("get_mapper_setup", "setInputData"),
    ],
)
def test_gaussian_splat_reader_js_output(method: str, expected: str) -> None:
    """Test that generated JavaScript contains expected strings."""
    mesh = GaussianSplatReader(GAUSSIAN_SPLAT_TEST).read()
    result = getattr(mesh, method)(0)
    assert expected in result


@pytest.mark.parametrize(
    ("fixture_type", "match"),
    [
        ("not_found", "File not found"),
        ("wrong_ext", "Expected a .ply or .splat file"),
    ],
)
def test_gaussian_splat_reader_init_errors(
    tmp_path: Path,
    fixture_type: str,
    match: str,
) -> None:
    """Test initialization errors for various file issues."""
    if fixture_type == "not_found":
        bad_path = tmp_path / "missing.ply"
        with pytest.raises(FileNotFoundError, match=match):
            GaussianSplatReader(bad_path)
    elif fixture_type == "wrong_ext":
        bad_file = tmp_path / "test.txt"
        bad_file.write_text("dummy")
        with pytest.raises(ValueError, match=match):
            GaussianSplatReader(bad_file)


def test_gaussian_splat_reader_invalid_ply(tmp_path: Path) -> None:
    """Test reading an invalid PLY file."""
    bad_file = tmp_path / "bad.ply"
    bad_file.write_text("not a ply file\n")
    reader = GaussianSplatReader(bad_file)
    with pytest.raises(ValueError, match="missing 'ply' magic number"):
        reader.read()


def test_gaussian_splat_reader_missing_header(tmp_path: Path) -> None:
    """Test reading a PLY file without end_header."""
    bad_file = tmp_path / "no_header.ply"
    bad_file.write_text("ply\nformat ascii 1.0\n")
    reader = GaussianSplatReader(bad_file)
    with pytest.raises(ValueError, match="missing 'end_header'"):
        reader.read()


def test_gaussian_splat_reader_missing_position(tmp_path: Path) -> None:
    """Test reading a PLY file without position properties."""
    bad_file = tmp_path / "no_pos.ply"
    content = """ply
format ascii 1.0
element vertex 1
property float scale_0
end_header
1.0
"""
    bad_file.write_text(content)
    reader = GaussianSplatReader(bad_file)
    with pytest.raises(ValueError, match="missing x, y, or z position properties"):
        reader.read()
