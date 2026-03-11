"""File readers for pyvista-js.

Provides readers for loading VTK file formats into Mesh objects,
using vtk.js built-in readers for parsing on the JavaScript side.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

import numpy as np

from .mesh import Mesh

logger = logging.getLogger(__name__)

# Minimum number of lines in a valid VTK legacy file
# (version header, title, format, dataset declaration)
_MIN_VTK_LINES = 4

# Load JavaScript template
_JS_DIR = Path(__file__).parent / "js"
_VTK_READER_SOURCE_TEMPLATE = (_JS_DIR / "vtk_reader_source.js").read_text()


class _PolyDataMesh(Mesh):
    """Mesh loaded from a legacy VTK file, rendered via vtk.js reader."""

    def __init__(self, points: np.ndarray, vtk_text: str) -> None:
        """Initialize with points and raw VTK file content.

        Parameters
        ----------
        points : np.ndarray
            Vertex coordinates (N, 3) extracted for bounding sphere computation.
        vtk_text : str
            Raw content of the VTK file passed to vtk.js for rendering.

        """
        super().__init__(points)
        self._vtk_text = vtk_text

    def generate_vtk_js_source(self, idx: int) -> str:
        """Generate vtk.js source code using vtkPolyDataReader."""
        escaped = json.dumps(self._vtk_text)
        return _VTK_READER_SOURCE_TEMPLATE.replace(
            "{{INDEX}}",
            str(idx),
        ).replace("{{VTK_TEXT}}", escaped)

    def get_mapper_setup(self, idx: int) -> str:
        """Get the mapper setup code."""
        return f"mapper{idx}.setInputData(source{idx});"


class PolyDataReader:
    """Reader for legacy VTK PolyData files (``.vtk``).

    Reads a legacy VTK ASCII file and produces a :class:`Mesh` that
    delegates parsing to vtk.js's ``vtkPolyDataReader`` at render time.
    Python extracts only the point coordinates so that camera framing
    and bounding-sphere queries work before rendering.

    Parameters
    ----------
    path : str or Path
        Path to the ``.vtk`` file.

    Examples
    --------
    >>> import pyvista_js as pv
    >>> reader = pv.PolyDataReader("sphere.vtk")  # doctest: +SKIP
    >>> mesh = reader.read()  # doctest: +SKIP

    """

    def __init__(self, path: str | Path) -> None:
        """Initialize the reader with a file path."""
        self._path = Path(path)
        if not self._path.exists():
            msg = f"File not found: {self._path}"
            raise FileNotFoundError(msg)
        if self._path.suffix.lower() != ".vtk":
            msg = f"Expected a .vtk file, got: {self._path.suffix}"
            raise ValueError(msg)

    @property
    def path(self) -> Path:
        """Return the file path.

        Returns
        -------
        Path
            The path to the VTK file.

        """
        return self._path

    def read(self) -> _PolyDataMesh:
        """Read the VTK file and return a Mesh.

        The full file content is stored so that vtk.js can parse it at
        render time.  Point coordinates are extracted on the Python side
        for bounding-sphere and camera-framing calculations.

        Returns
        -------
        Mesh
            A mesh backed by the VTK file content.

        Raises
        ------
        ValueError
            If the file format is invalid or unsupported.

        """
        vtk_text = self._path.read_text()
        lines = vtk_text.splitlines()

        if len(lines) < _MIN_VTK_LINES:
            msg = "Invalid VTK file: too few lines"
            raise ValueError(msg)

        if "vtk" not in lines[0].lower():
            msg = "Invalid VTK file: missing version header"
            raise ValueError(msg)

        file_format = lines[2].strip().upper()
        if file_format != "ASCII":
            msg = f"Only ASCII VTK files are supported, got: {file_format}"
            raise ValueError(msg)

        points = self._extract_points(lines)
        logger.info("Read %d points from %s", len(points), self._path)
        return _PolyDataMesh(points=points, vtk_text=vtk_text)

    @staticmethod
    def _extract_points(lines: list[str]) -> np.ndarray:
        """Extract point coordinates from VTK ASCII lines.

        Only used for Python-side bounding-sphere computation.
        The actual geometry is parsed by vtk.js at render time.

        Parameters
        ----------
        lines : list[str]
            All lines of the VTK file.

        Returns
        -------
        np.ndarray
            Points array with shape (N, 3).

        """
        i = 3
        while i < len(lines):
            line = lines[i].strip()
            if line.upper().startswith("POINTS"):
                parts = line.split()
                n_points = int(parts[1])
                values: list[float] = []
                i += 1
                needed = n_points * 3
                while len(values) < needed and i < len(lines):
                    row = lines[i].strip()
                    if row:
                        values.extend(float(v) for v in row.split())
                    i += 1
                return np.array(values[: n_points * 3]).reshape(n_points, 3)
            i += 1
        return np.empty((0, 3))
