"""Tests for ``XMLPolyDataReader``."""

from pathlib import Path

import numpy as np
import pytest

import pyvista_js as pv

VTP_CONTENT = """<?xml version="1.0"?>
<VTKFile type="PolyData" version="0.1" byte_order="LittleEndian">
  <PolyData>
    <Piece NumberOfPoints="3" NumberOfPolys="1">
      <Points>
        <DataArray type="Float64" NumberOfComponents="3" format="ascii">
          0 0 0
          1 0 0
          0 1 0
        </DataArray>
      </Points>
      <Polys>
        <DataArray type="Int64" Name="connectivity" format="ascii">
          0 1 2
        </DataArray>
        <DataArray type="Int64" Name="offsets" format="ascii">
          3
        </DataArray>
      </Polys>
    </Piece>
  </PolyData>
</VTKFile>
"""


@pytest.fixture
def vtp_file(tmp_path: Path) -> Path:
    """Create a small ``.vtp`` file for testing."""
    path = tmp_path / "mesh.vtp"
    path.write_text(VTP_CONTENT)
    return path


def test_xml_poly_data_reader(vtp_file: Path) -> None:
    """Test reading a .vtp file yields points and the scene reader type."""
    reader = pv.XMLPolyDataReader(vtp_file)
    mesh = reader.read()
    assert isinstance(mesh, pv.PolyData)
    assert mesh.n_points == 3
    scene = mesh.to_scene_data()
    assert scene["type"] == "vtpReader"


def test_xml_poly_data_reader_points(vtp_file: Path) -> None:
    """Test parsed points match the file content."""
    reader = pv.XMLPolyDataReader(vtp_file)
    mesh = reader.read()
    assert np.allclose(mesh.points, [[0, 0, 0], [1, 0, 0], [0, 1, 0]])


def test_xml_poly_data_reader_rejects_suffix(tmp_path: Path) -> None:
    """Test the reader validates the file suffix."""
    path = tmp_path / "mesh.vtk"
    path.write_text(VTP_CONTENT)
    with pytest.raises(ValueError, match=r"Expected a \.vtp file"):
        pv.XMLPolyDataReader(path)


def test_xml_poly_data_reader_rejects_missing_file(tmp_path: Path) -> None:
    """Test the reader raises for a nonexistent path."""
    with pytest.raises(FileNotFoundError):
        pv.XMLPolyDataReader(tmp_path / "missing.vtp")
