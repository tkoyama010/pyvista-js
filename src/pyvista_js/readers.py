"""File readers for pyvista-js.

Provides readers for loading mesh file formats into Mesh objects,
using vtk.js built-in readers for parsing on the JavaScript side.
"""

from __future__ import annotations

import base64
import json
import logging
import re
import struct
from pathlib import Path

import numpy as np
from jinja2 import Environment, StrictUndefined

from .mesh import PolyData

_jinja_env = Environment(undefined=StrictUndefined, autoescape=False)


def _render(template_str: str, **kwargs: object) -> str:
    rendered = _jinja_env.from_string(template_str).render(**kwargs)
    # Strip <script> wrapper added for prettier formatting
    rendered = re.sub(r"^\s*<script>\s*\n?", "", rendered)
    return re.sub(r"\n?\s*</script>\s*$", "", rendered)


logger = logging.getLogger(__name__)

# Minimum number of lines in a valid VTK legacy file
# (version header, title, format, dataset declaration)
_MIN_VTK_LINES = 4

# Number of coordinate components per vertex (x, y, z)
_N_COORDS = 3

# Load JavaScript templates
_TEMPLATES_DIR = Path(__file__).parent / "templates"
_VTK_READER_SOURCE_TEMPLATE = (_TEMPLATES_DIR / "vtk_reader_source.html").read_text()
_PLY_READER_SOURCE_TEMPLATE = (_TEMPLATES_DIR / "ply_reader_source.html").read_text()
_OBJ_READER_SOURCE_TEMPLATE = (_TEMPLATES_DIR / "obj_reader_source.html").read_text()
_STL_READER_SOURCE_TEMPLATE = (_TEMPLATES_DIR / "stl_reader_source.html").read_text()


class _OBJMesh(PolyData):
    """Mesh loaded from an OBJ file, rendered via vtk.js OBJ reader."""

    def __init__(self, points: np.ndarray, obj_base64: str) -> None:
        """Initialize with points and base64-encoded OBJ file content.

        Parameters
        ----------
        points : np.ndarray
            Vertex coordinates (N, 3) extracted for bounding sphere computation.
        obj_base64 : str
            Base64-encoded content of the OBJ file passed to vtk.js for rendering.

        """
        super().__init__(points)
        self._obj_base64 = obj_base64

    def generate_vtk_js_source(self, idx: int) -> str:
        """Generate vtk.js source code using vtkOBJReader."""
        escaped = json.dumps(self._obj_base64)
        return _render(
            _OBJ_READER_SOURCE_TEMPLATE,
            SOURCE=f"source{idx}",
            OBJ_READER=f"objReader{idx}",
            OBJ_BASE64=escaped,
        )

    def get_mapper_setup(self, idx: int) -> str:
        """Get the mapper setup code."""
        return f"mapper{idx}.setInputData(source{idx});"


class _PolyDataMesh(PolyData):
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
        return _render(
            _VTK_READER_SOURCE_TEMPLATE,
            SOURCE=f"source{idx}",
            VTK_READER=f"reader{idx}",
            VTK_TEXT=escaped,
        )

    def get_mapper_setup(self, idx: int) -> str:
        """Get the mapper setup code."""
        return f"mapper{idx}.setInputData(source{idx});"


class _PLYMesh(PolyData):
    """Mesh loaded from a PLY file, rendered via vtk.js PLY reader."""

    def __init__(self, points: np.ndarray, ply_base64: str) -> None:
        """Initialize with points and base64-encoded PLY file content.

        Parameters
        ----------
        points : np.ndarray
            Vertex coordinates (N, 3) extracted for bounding sphere computation.
        ply_base64 : str
            Base64-encoded content of the PLY file passed to vtk.js for rendering.

        """
        super().__init__(points)
        self._ply_base64 = ply_base64

    def generate_vtk_js_source(self, idx: int) -> str:
        """Generate vtk.js source code using vtkPLYReader."""
        escaped = json.dumps(self._ply_base64)
        return _render(
            _PLY_READER_SOURCE_TEMPLATE,
            SOURCE=f"source{idx}",
            PLY_READER=f"plyReader{idx}",
            PLY_BASE64=escaped,
        )

    def get_mapper_setup(self, idx: int) -> str:
        """Get the mapper setup code."""
        return f"mapper{idx}.setInputData(source{idx});"


class _STLMesh(PolyData):
    """Mesh loaded from an STL file, rendered via vtk.js STL reader."""

    def __init__(self, points: np.ndarray, stl_base64: str) -> None:
        """Initialize with points and base64-encoded STL file content.

        Parameters
        ----------
        points : np.ndarray
            Vertex coordinates (N, 3) extracted for bounding sphere computation.
        stl_base64 : str
            Base64-encoded content of the STL file passed to vtk.js for rendering.

        """
        super().__init__(points)
        self._stl_base64 = stl_base64

    def generate_vtk_js_source(self, idx: int) -> str:
        """Generate vtk.js source code using vtkSTLReader."""
        escaped = json.dumps(self._stl_base64)
        return _render(
            _STL_READER_SOURCE_TEMPLATE,
            SOURCE=f"source{idx}",
            STL_READER=f"stlReader{idx}",
            STL_BASE64=escaped,
        )

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


class PLYReader:
    """Reader for PLY (Polygon File Format) files (``.ply``).

    Reads a PLY ASCII file and produces a :class:`Mesh` that delegates
    parsing to vtk.js's ``vtkPLYReader`` at render time. Python extracts
    only the vertex coordinates so that camera framing and bounding-sphere
    queries work before rendering.

    Parameters
    ----------
    path : str or Path
        Path to the ``.ply`` file.

    Examples
    --------
    >>> import pyvista_js as pv
    >>> reader = pv.PLYReader("model.ply")  # doctest: +SKIP
    >>> mesh = reader.read()  # doctest: +SKIP

    """

    def __init__(self, path: str | Path) -> None:
        """Initialize the reader with a file path."""
        self._path = Path(path)
        if not self._path.exists():
            msg = f"File not found: {self._path}"
            raise FileNotFoundError(msg)
        if self._path.suffix.lower() != ".ply":
            msg = f"Expected a .ply file, got: {self._path.suffix}"
            raise ValueError(msg)

    @property
    def path(self) -> Path:
        """Return the file path.

        Returns
        -------
        Path
            The path to the PLY file.

        """
        return self._path

    def read(self) -> _PLYMesh:
        """Read the PLY file and return a Mesh.

        The full file content is base64-encoded and stored so that vtk.js
        can parse it at render time.  Vertex coordinates are extracted on
        the Python side for bounding-sphere and camera-framing calculations.

        Returns
        -------
        Mesh
            A mesh backed by the PLY file content.

        Raises
        ------
        ValueError
            If the file format is invalid or unsupported.

        """
        raw = self._path.read_bytes()
        text = raw.decode("ascii", errors="replace")
        lines = text.splitlines()

        if not lines or lines[0].strip() != "ply":
            msg = "Invalid PLY file: missing 'ply' magic number"
            raise ValueError(msg)

        header_end = None
        for i, line in enumerate(lines):
            if line.strip() == "end_header":
                header_end = i
                break

        if header_end is None:
            msg = "Invalid PLY file: missing 'end_header'"
            raise ValueError(msg)

        fmt = self._parse_format(lines[1 : header_end + 1])
        if fmt != "ascii":
            msg = f"Only ASCII PLY files are supported, got: {fmt}"
            raise ValueError(msg)

        points = self._extract_points(lines, header_end)
        ply_base64 = base64.b64encode(raw).decode("ascii")
        logger.info("Read %d points from %s", len(points), self._path)
        return _PLYMesh(points=points, ply_base64=ply_base64)

    @staticmethod
    def _parse_format(header_lines: list[str]) -> str:
        """Extract the format from PLY header lines.

        Parameters
        ----------
        header_lines : list[str]
            Header lines between 'ply' and 'end_header'.

        Returns
        -------
        str
            The format string (e.g. ``'ascii'``, ``'binary_little_endian'``).

        Raises
        ------
        ValueError
            If no format line is found.

        """
        for line in header_lines:
            parts = line.strip().split()
            if parts and parts[0] == "format":
                return parts[1]
        msg = "Invalid PLY file: missing 'format' declaration"
        raise ValueError(msg)

    @staticmethod
    def _extract_points(lines: list[str], header_end: int) -> np.ndarray:
        """Extract vertex coordinates from PLY ASCII data.

        Only used for Python-side bounding-sphere computation.
        The actual geometry is parsed by vtk.js at render time.

        Parameters
        ----------
        lines : list[str]
            All lines of the PLY file.
        header_end : int
            Index of the 'end_header' line.

        Returns
        -------
        np.ndarray
            Points array with shape (N, 3).

        """
        # Find vertex count from header
        n_vertices = 0
        for line in lines[1 : header_end + 1]:
            parts = line.strip().split()
            if len(parts) >= _N_COORDS and parts[0] == "element" and parts[1] == "vertex":
                n_vertices = int(parts[2])
                break

        if n_vertices == 0:
            return np.empty((0, 3))

        data_start = header_end + 1
        points = []
        for i in range(n_vertices):
            if data_start + i >= len(lines):
                break
            parts = lines[data_start + i].strip().split()
            if len(parts) >= _N_COORDS:
                points.append([float(parts[0]), float(parts[1]), float(parts[2])])

        if not points:
            return np.empty((0, 3))
        return np.array(points)


class OBJReader:
    """Reader for Wavefront OBJ files (``.obj``).

    Reads an OBJ ASCII file and produces a :class:`Mesh` that delegates
    parsing to vtk.js's ``vtkOBJReader`` at render time. Python extracts
    only the vertex coordinates so that camera framing and bounding-sphere
    queries work before rendering.

    Parameters
    ----------
    path : str or Path
        Path to the ``.obj`` file.

    Examples
    --------
    >>> import pyvista_js as pv
    >>> reader = pv.OBJReader("model.obj")  # doctest: +SKIP
    >>> mesh = reader.read()  # doctest: +SKIP

    """

    def __init__(self, path: str | Path) -> None:
        """Initialize the reader with a file path."""
        self._path = Path(path)
        if not self._path.exists():
            msg = f"File not found: {self._path}"
            raise FileNotFoundError(msg)
        if self._path.suffix.lower() != ".obj":
            msg = f"Expected a .obj file, got: {self._path.suffix}"
            raise ValueError(msg)

    @property
    def path(self) -> Path:
        """Return the file path.

        Returns
        -------
        Path
            The path to the OBJ file.

        """
        return self._path

    def read(self) -> _OBJMesh:
        """Read the OBJ file and return a Mesh.

        The full file content is base64-encoded and stored so that vtk.js
        can parse it at render time.  Vertex coordinates are extracted on
        the Python side for bounding-sphere and camera-framing calculations.

        Returns
        -------
        Mesh
            A mesh backed by the OBJ file content.

        Raises
        ------
        ValueError
            If the file contains no vertex data.

        """
        raw = self._path.read_bytes()
        text = raw.decode("ascii", errors="replace")
        lines = text.splitlines()

        points = self._extract_points(lines)
        obj_base64 = base64.b64encode(raw).decode("ascii")
        logger.info("Read %d points from %s", len(points), self._path)
        return _OBJMesh(points=points, obj_base64=obj_base64)

    @staticmethod
    def _extract_points(lines: list[str]) -> np.ndarray:
        """Extract vertex coordinates from OBJ lines.

        Only used for Python-side bounding-sphere computation.
        The actual geometry is parsed by vtk.js at render time.

        Parameters
        ----------
        lines : list[str]
            All lines of the OBJ file.

        Returns
        -------
        np.ndarray
            Points array with shape (N, 3).

        """
        points = []
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("v "):
                parts = stripped.split()
                if len(parts) >= _N_COORDS + 1:
                    points.append(
                        [float(parts[1]), float(parts[2]), float(parts[3])],
                    )
        if not points:
            return np.empty((0, 3))
        return np.array(points)


class STLReader:
    """Reader for STL (STereoLithography) files (``.stl``).

    Reads an STL file (ASCII or binary) and produces a :class:`Mesh` that
    delegates parsing to vtk.js's ``vtkSTLReader`` at render time. Python
    extracts only the vertex coordinates so that camera framing and
    bounding-sphere queries work before rendering.

    Parameters
    ----------
    path : str or Path
        Path to the ``.stl`` file.

    Examples
    --------
    >>> from pyvista_js import examples
    >>> mesh = examples.download_cad_model()  # doctest: +SKIP
    >>> mesh.plot()  # doctest: +SKIP

    """

    def __init__(self, path: str | Path) -> None:
        """Initialize the reader with a file path."""
        self._path = Path(path)
        if not self._path.exists():
            msg = f"File not found: {self._path}"
            raise FileNotFoundError(msg)
        if self._path.suffix.lower() != ".stl":
            msg = f"Expected a .stl file, got: {self._path.suffix}"
            raise ValueError(msg)

    @property
    def path(self) -> Path:
        """Return the file path.

        Returns
        -------
        Path
            The path to the STL file.

        """
        return self._path

    def read(self) -> _STLMesh:
        """Read the STL file and return a Mesh.

        The full file content is base64-encoded and stored so that vtk.js
        can parse it at render time.  Vertex coordinates are extracted on
        the Python side for bounding-sphere and camera-framing calculations.

        Returns
        -------
        Mesh
            A mesh backed by the STL file content.

        Raises
        ------
        ValueError
            If the file format is invalid or unsupported.

        """
        raw = self._path.read_bytes()

        if self._is_binary_stl(raw):
            points = self._extract_points_binary(raw)
        else:
            text = raw.decode("ascii", errors="replace")
            lines = text.splitlines()
            if not lines or "solid" not in lines[0].lower():
                msg = "Invalid STL file: missing 'solid' header"
                raise ValueError(msg)
            points = self._extract_points(lines)

        stl_base64 = base64.b64encode(raw).decode("ascii")
        logger.info("Read %d points from %s", len(points), self._path)
        return _STLMesh(points=points, stl_base64=stl_base64)

    @staticmethod
    def _extract_points(lines: list[str]) -> np.ndarray:
        """Extract vertex coordinates from STL ASCII data.

        Only used for Python-side bounding-sphere computation.
        The actual geometry is parsed by vtk.js at render time.

        Parameters
        ----------
        lines : list[str]
            All lines of the STL file.

        Returns
        -------
        np.ndarray
            Points array with shape (N, 3).

        """
        points = []
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("vertex"):
                parts = stripped.split()
                if len(parts) >= _N_COORDS + 1:
                    points.append(
                        [float(parts[1]), float(parts[2]), float(parts[3])],
                    )
        if not points:
            return np.empty((0, 3))
        return np.array(points)

    @staticmethod
    def _is_binary_stl(raw: bytes) -> bool:
        """Check whether raw bytes represent a binary STL file.

        Binary STL is exactly 84 + 50*N bytes (80-byte header, 4-byte
        triangle count, 50 bytes per triangle). This size check
        reliably distinguishes binary from ASCII.

        Parameters
        ----------
        raw : bytes
            Raw file content.

        Returns
        -------
        bool
            True if the file appears to be binary STL.

        """
        _header_size = 80
        _count_size = 4
        _triangle_size = 50

        if len(raw) < _header_size + _count_size:
            return False

        (n_triangles,) = struct.unpack_from("<I", raw, _header_size)
        expected = _header_size + _count_size + _triangle_size * n_triangles
        return len(raw) == expected

    @staticmethod
    def _extract_points_binary(raw: bytes) -> np.ndarray:
        """Extract vertex coordinates from a binary STL file.

        Binary STL layout: 80-byte header, 4-byte triangle count,
        then 50 bytes per triangle (12 normal + 36 vertices + 2 attr).

        Parameters
        ----------
        raw : bytes
            Raw file content.

        Returns
        -------
        np.ndarray
            Points array with shape (N, 3).

        """
        _header_size = 80
        _count_size = 4
        _triangle_size = 50

        if len(raw) < _header_size + _count_size:
            return np.empty((0, 3))

        (n_triangles,) = struct.unpack_from("<I", raw, _header_size)
        offset = _header_size + _count_size
        points = []

        for _ in range(n_triangles):
            if offset + _triangle_size > len(raw):
                break
            # Skip 12-byte normal, read 3 vertices (each 3 floats = 12 bytes)
            v = struct.unpack_from("<9f", raw, offset + 12)
            points.append([v[0], v[1], v[2]])
            points.append([v[3], v[4], v[5]])
            points.append([v[6], v[7], v[8]])
            offset += _triangle_size

        if not points:
            return np.empty((0, 3))
        return np.array(points)
