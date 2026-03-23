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
from jinja2 import Environment, FileSystemLoader, StrictUndefined

from .mesh import PolyData, _GaussianSplatMesh

_TEMPLATES_DIR_FOR_LOADER = Path(__file__).parent / "templates"
_jinja_env = Environment(
    loader=FileSystemLoader(_TEMPLATES_DIR_FOR_LOADER),
    undefined=StrictUndefined,
    autoescape=False,  # noqa: S701
)


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
_GLTF_READER_SOURCE_TEMPLATE = (_TEMPLATES_DIR / "gltf_reader_source.html").read_text()
_GLTF_URL_SOURCE_TEMPLATE = (_TEMPLATES_DIR / "gltf_url_source.html").read_text()


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


class _GLTFMesh(PolyData):
    """Mesh loaded from a glTF file, rendered via vtk.js GLTF importer."""

    def __init__(self, points: np.ndarray, gltf_base64: str, gltf_url: str | None = None) -> None:
        """Initialize with points and base64-encoded glTF file content.

        Parameters
        ----------
        points : np.ndarray
            Vertex coordinates (N, 3) extracted for bounding sphere computation.
        gltf_base64 : str
            Base64-encoded content of the glTF file passed to vtk.js for rendering.
        gltf_url : str or None, optional
            Source URL of the glTF file. When provided, the URL is used directly
            in the model-viewer element instead of embedding the full base64 data,
            which avoids large payload issues in JupyterLite.

        """
        super().__init__(points)
        self._gltf_base64 = gltf_base64
        self._gltf_url = gltf_url

    def generate_vtk_js_source(self, idx: int) -> str:
        """Generate vtk.js source code using model-viewer web component."""
        if self._gltf_url is not None:
            return _render(
                _GLTF_URL_SOURCE_TEMPLATE,
                INDEX=str(idx),
                GLTF_URL=self._gltf_url,
            )
        escaped = json.dumps(self._gltf_base64)
        return _render(
            _GLTF_READER_SOURCE_TEMPLATE,
            INDEX=str(idx),
            GLTF_BASE64=escaped,
        )

    def get_mapper_setup(self, idx: int) -> str:
        """Get the mapper setup code."""
        return f"mapper{idx}.setInputData(source{idx});"

    def generate_full_actor_code(self, idx: int, _actor_info: dict) -> str:
        """Generate complete vtk.js actor code for a glTF mesh.

        vtkGLTFImporter adds actors directly via importActors(renderer),
        bypassing the standard mapper/actor pipeline used by other readers.

        Parameters
        ----------
        idx : int
            Actor index for unique variable names.
        actor_info : dict
            Actor info dict (unused; GLTF materials come from the file).

        Returns
        -------
        str
            Self-contained JavaScript that imports the glTF into the scene.

        """
        return self.generate_vtk_js_source(idx)


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
        header_byte_offset = 0
        for i, line in enumerate(lines):
            if line.strip() == "end_header":
                header_end = i
                # Calculate byte offset after header
                header_byte_offset = raw.find(b"end_header") + len(b"end_header") + 1
                break

        if header_end is None:
            msg = "Invalid PLY file: missing 'end_header'"
            raise ValueError(msg)

        fmt = self._parse_format(lines[1 : header_end + 1])

        if fmt == "ascii":
            points = self._extract_points(lines, header_end)
        elif fmt in ("binary_little_endian", "binary_big_endian"):
            points = self._extract_points_binary(
                raw,
                lines[1 : header_end + 1],
                header_byte_offset,
                fmt,
            )
        else:
            msg = f"Unsupported PLY format: {fmt}"
            raise ValueError(msg)

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

    @staticmethod
    def _parse_vertex_info(header_lines: list[str]) -> tuple[int, list[str]]:
        """Extract vertex count and property types from PLY header lines.

        Parameters
        ----------
        header_lines : list[str]
            Header lines between 'ply' and 'end_header'.

        Returns
        -------
        tuple[int, list[str]]
            Vertex count and list of property type strings.

        """
        n_vertices = 0
        vertex_properties: list[str] = []
        in_vertex_element = False

        for line in header_lines:
            parts = line.strip().split()
            if not parts:
                continue
            if parts[0] == "element":
                if len(parts) >= _N_COORDS and parts[1] == "vertex":
                    n_vertices = int(parts[2])
                    in_vertex_element = True
                else:
                    in_vertex_element = False
            elif parts[0] == "property" and in_vertex_element and len(parts) >= _N_COORDS:
                vertex_properties.append(parts[1])

        return n_vertices, vertex_properties

    @staticmethod
    def _extract_points_binary(
        raw: bytes,
        header_lines: list[str],
        data_offset: int,
        fmt: str,
    ) -> np.ndarray:
        """Extract vertex coordinates from binary PLY data.

        Parameters
        ----------
        raw : bytes
            Raw binary content of the PLY file.
        header_lines : list[str]
            Header lines between 'ply' and 'end_header'.
        data_offset : int
            Byte offset where vertex data starts (after 'end_header').
        fmt : str
            Format string ('binary_little_endian' or 'binary_big_endian').

        Returns
        -------
        np.ndarray
            Points array with shape (N, 3).

        """
        endian = "<" if fmt == "binary_little_endian" else ">"

        n_vertices, vertex_properties = PLYReader._parse_vertex_info(header_lines)

        if n_vertices == 0:
            return np.empty((0, 3))

        # Build struct format for one vertex
        # We need to know the size of each property to skip them
        type_map = {
            "char": "b",
            "uchar": "B",
            "short": "h",
            "ushort": "H",
            "int": "i",
            "uint": "I",
            "float": "f",
            "double": "d",
        }

        # Calculate bytes per vertex
        vertex_fmt = endian
        bytes_per_vertex = 0
        for prop_type in vertex_properties:
            if prop_type in type_map:
                vertex_fmt += type_map[prop_type]
                bytes_per_vertex += struct.calcsize(endian + type_map[prop_type])

        # Extract points (first 3 properties assumed to be x, y, z)
        points = []
        offset = data_offset

        for _ in range(n_vertices):
            if offset + bytes_per_vertex > len(raw):
                break

            try:
                vertex_data = struct.unpack_from(vertex_fmt, raw, offset)
                # Take only first 3 values (x, y, z)
                points.append([float(vertex_data[0]), float(vertex_data[1]), float(vertex_data[2])])
                offset += bytes_per_vertex
            except struct.error:
                break

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


class GLTFReader:
    """Reader for glTF (GL Transmission Format) files (``.gltf`` or ``.glb``).

    Reads a glTF file and produces a :class:`Mesh` that delegates parsing
    to vtk.js's ``vtkGLTFImporter`` at render time. Python extracts
    vertex coordinates from the JSON structure so that camera framing and
    bounding-sphere queries work before rendering.

    Parameters
    ----------
    path : str or Path
        Path to the ``.gltf`` or ``.glb`` file.

    See Also
    --------
    :ref:`using-download-damaged-helmet`
        Interactive browser tutorial for glTF rendering.

    Examples
    --------
    >>> import pyvista_js as pv
    >>> reader = pv.GLTFReader("model.gltf")  # doctest: +SKIP
    >>> mesh = reader.read()  # doctest: +SKIP

    """

    def __init__(self, path: str | Path, gltf_url: str | None = None) -> None:
        """Initialize the reader with a file path.

        Parameters
        ----------
        path : str or Path
            Path to the ``.gltf`` or ``.glb`` file.
        gltf_url : str or None, optional
            Source URL of the glTF file. When provided, the returned mesh will
            render using the URL directly (avoiding large base64 embedding).

        """
        self._path = Path(path)
        if not self._path.exists():
            msg = f"File not found: {self._path}"
            raise FileNotFoundError(msg)
        if self._path.suffix.lower() not in (".gltf", ".glb"):
            msg = f"Expected a .gltf or .glb file, got: {self._path.suffix}"
            raise ValueError(msg)
        self._gltf_url = gltf_url

    @property
    def path(self) -> Path:
        """Return the file path.

        Returns
        -------
        Path
            The path to the glTF file.

        """
        return self._path

    def read(self) -> _GLTFMesh:
        """Read the glTF file and return a Mesh.

        The full file content is base64-encoded and stored so that vtk.js
        can parse it at render time.  Vertex coordinates are extracted on
        the Python side for bounding-sphere and camera-framing calculations.

        Returns
        -------
        Mesh
            A mesh backed by the glTF file content.

        Raises
        ------
        ValueError
            If the file format is invalid.

        """
        raw = self._path.read_bytes()

        # Extract points from glTF JSON structure
        points = self._extract_points(raw)
        gltf_base64 = base64.b64encode(raw).decode("ascii")
        logger.info("Read %d points from %s", len(points), self._path)
        return _GLTFMesh(points=points, gltf_base64=gltf_base64, gltf_url=self._gltf_url)

    @staticmethod
    def _extract_points(raw: bytes) -> np.ndarray:
        """Extract vertex coordinates from glTF file.

        Only used for Python-side bounding-sphere computation.
        The actual geometry is parsed by vtk.js at render time.

        Parameters
        ----------
        raw : bytes
            Raw content of the glTF file.

        Returns
        -------
        np.ndarray
            Points array with shape (N, 3).

        """
        # Parse glTF JSON
        try:
            text = raw.decode("utf-8")
            gltf_data = json.loads(text)
        except (UnicodeDecodeError, json.JSONDecodeError):
            return np.empty((0, 3))

        # Extract position accessor
        accessor = GLTFReader._get_position_accessor(gltf_data)
        if accessor is None:
            return np.empty((0, 3))

        # Extract bounding box from accessor min/max
        return GLTFReader._extract_bounds_points(accessor)

    @staticmethod
    def _get_position_accessor(gltf_data: dict) -> dict | None:
        """Get the position accessor from glTF data.

        Parameters
        ----------
        gltf_data : dict
            Parsed glTF JSON data.

        Returns
        -------
        dict or None
            The position accessor or None if not found.

        """
        if "meshes" not in gltf_data or not gltf_data["meshes"]:
            return None

        first_mesh = gltf_data["meshes"][0]
        if "primitives" not in first_mesh or not first_mesh["primitives"]:
            return None

        primitives = first_mesh["primitives"][0]
        if "attributes" not in primitives or "POSITION" not in primitives["attributes"]:
            return None

        position_accessor_idx = primitives["attributes"]["POSITION"]
        if "accessors" not in gltf_data or position_accessor_idx >= len(
            gltf_data["accessors"],
        ):
            return None

        return gltf_data["accessors"][position_accessor_idx]

    @staticmethod
    def _extract_bounds_points(accessor: dict) -> np.ndarray:
        """Extract bounding box corners from accessor.

        Parameters
        ----------
        accessor : dict
            The position accessor from glTF.

        Returns
        -------
        np.ndarray
            Array of 8 bounding box corners or empty array.

        """
        if "min" not in accessor or "max" not in accessor:
            return np.empty((0, 3))

        min_vals = accessor["min"]
        max_vals = accessor["max"]
        if len(min_vals) < _N_COORDS or len(max_vals) < _N_COORDS:
            return np.empty((0, 3))

        # Generate 8 corners of bounding box
        points = [
            [x, y, z]
            for x in [min_vals[0], max_vals[0]]
            for y in [min_vals[1], max_vals[1]]
            for z in [min_vals[2], max_vals[2]]
        ]
        return np.array(points)


class GaussianSplatReader:
    """Reader for Gaussian splat files (``.ply``, ``.splat``).

    Reads Gaussian splat data typically used in 3D Gaussian Splatting and NeRF
    workflows. The file format is PLY with specific properties for position, scale,
    rotation, opacity, and spherical harmonic coefficients. Parsing is delegated to
    JavaScript at render time, with Python extracting only positions for bounding
    sphere calculations.

    Parameters
    ----------
    path : str or Path
        Path to the Gaussian splat file (``.ply`` or ``.splat``).

    Examples
    --------
    >>> import pyvista_js as pv
    >>> reader = pv.GaussianSplatReader("scene.ply")  # doctest: +SKIP
    >>> mesh = reader.read()  # doctest: +SKIP
    >>> plotter = pv.Plotter()  # doctest: +SKIP
    >>> plotter.add_mesh(mesh)  # doctest: +SKIP
    >>> plotter.show()  # doctest: +SKIP

    """

    def __init__(self, path: str | Path) -> None:
        """Initialize the reader with a file path."""
        self._path = Path(path)
        if not self._path.exists():
            msg = f"File not found: {self._path}"
            raise FileNotFoundError(msg)
        if self._path.suffix.lower() not in (".ply", ".splat"):
            msg = f"Expected a .ply or .splat file, got: {self._path.suffix}"
            raise ValueError(msg)

    @property
    def path(self) -> Path:
        """Return the file path.

        Returns
        -------
        Path
            The path to the Gaussian splat file.

        """
        return self._path

    def read(self) -> _GaussianSplatMesh:
        """Read the Gaussian splat file and return a mesh.

        The full file content is base64-encoded for JavaScript parsing.
        Only position data is extracted in Python for bounding calculations.

        Returns
        -------
        _GaussianSplatMesh
            A mesh containing Gaussian splat data.

        Raises
        ------
        ValueError
            If the file format is invalid or unsupported.

        """
        raw = self._path.read_bytes()
        splat_base64 = base64.b64encode(raw).decode("ascii")

        # Extract positions for bounding sphere computation
        points = self._extract_positions(raw)

        return _GaussianSplatMesh(points, splat_base64)

    def _extract_positions(self, raw_data: bytes) -> np.ndarray:
        """Extract Gaussian center positions from the file.

        Parameters
        ----------
        raw_data : bytes
            Raw file content.

        Returns
        -------
        np.ndarray
            Array of positions (N, 3) for bounding calculations.

        """
        try:
            text = raw_data.decode("ascii", errors="replace")
        except UnicodeDecodeError:
            text = raw_data.decode("utf-8", errors="replace")

        lines = text.splitlines()

        if not lines or lines[0].strip() != "ply":
            msg = "Invalid Gaussian splat file: missing 'ply' magic number"
            raise ValueError(msg)

        # Find header end
        header_end = None
        header_byte_offset = 0
        for i, line in enumerate(lines):
            if line.strip() == "end_header":
                header_end = i
                header_byte_offset = raw_data.find(b"end_header") + len(b"end_header") + 1
                break

        if header_end is None:
            msg = "Invalid Gaussian splat file: missing 'end_header'"
            raise ValueError(msg)

        header_lines = lines[1 : header_end + 1]

        # Parse vertex count
        n_vertices = 0
        for line in header_lines:
            if line.startswith("element vertex"):
                parts = line.split()
                if len(parts) >= _N_COORDS:
                    n_vertices = int(parts[2])
                break

        if n_vertices == 0:
            return np.empty((0, _N_COORDS))

        # Parse format
        fmt = self._parse_format(header_lines)

        # Parse property layout to find x, y, z positions
        properties = []
        for line in header_lines:
            if line.startswith("property"):
                parts = line.split()
                if len(parts) >= _N_COORDS:
                    prop_type = parts[1]
                    prop_name = parts[2]
                    properties.append((prop_name, prop_type))

        # Find x, y, z indices
        x_idx = next((i for i, (name, _) in enumerate(properties) if name == "x"), -1)
        y_idx = next((i for i, (name, _) in enumerate(properties) if name == "y"), -1)
        z_idx = next((i for i, (name, _) in enumerate(properties) if name == "z"), -1)

        if x_idx < 0 or y_idx < 0 or z_idx < 0:
            msg = "Invalid Gaussian splat file: missing x, y, or z position properties"
            raise ValueError(msg)

        # Extract positions based on format
        if fmt == "ascii":
            return self._extract_positions_ascii(
                lines,
                header_end,
                n_vertices,
                x_idx,
                y_idx,
                z_idx,
            )
        if fmt in ("binary_little_endian", "binary_big_endian"):
            return self._extract_positions_binary(
                raw_data,
                header_byte_offset,
                n_vertices,
                properties,
                x_idx,
                y_idx,
                z_idx,
                fmt,
            )
        msg = f"Unsupported format: {fmt}"
        raise ValueError(msg)

    @staticmethod
    def _parse_format(header_lines: list[str]) -> str:
        """Parse the format line from PLY header."""
        for line in header_lines:
            if line.startswith("format"):
                parts = line.split()
                if len(parts) >= 2:
                    return parts[1]
        return "ascii"

    @staticmethod
    def _extract_positions_ascii(
        lines: list[str],
        header_end: int,
        n_vertices: int,
        x_idx: int,
        y_idx: int,
        z_idx: int,
    ) -> np.ndarray:
        """Extract positions from ASCII format."""
        positions = []
        data_start = header_end + 1

        for i in range(n_vertices):
            if data_start + i >= len(lines):
                break
            line = lines[data_start + i].strip()
            if not line:
                continue

            values = line.split()
            if len(values) > max(x_idx, y_idx, z_idx):
                try:
                    x = float(values[x_idx])
                    y = float(values[y_idx])
                    z = float(values[z_idx])
                    positions.append([x, y, z])
                except (ValueError, IndexError):
                    continue

        return np.array(positions) if positions else np.empty((0, _N_COORDS))

    @staticmethod
    def _extract_positions_binary(
        raw_data: bytes,
        header_byte_offset: int,
        n_vertices: int,
        properties: list[tuple[str, str]],
        x_idx: int,
        y_idx: int,
        z_idx: int,
        fmt: str,
    ) -> np.ndarray:
        """Extract positions from binary format."""
        # Calculate stride (bytes per vertex)
        stride = 0
        offsets = []
        for _, prop_type in properties:
            size = 4  # float
            if prop_type in ("double",):
                size = 8
            elif prop_type in ("uchar", "char", "uint8", "int8"):
                size = 1
            elif prop_type in ("ushort", "short", "uint16", "int16"):
                size = 2
            offsets.append(stride)
            stride += size

        little_endian = fmt == "binary_little_endian"
        endian_char = "<" if little_endian else ">"

        positions = []
        for i in range(n_vertices):
            offset = header_byte_offset + i * stride
            if offset + stride > len(raw_data):
                break

            try:
                x = struct.unpack(f"{endian_char}f", raw_data[offset + offsets[x_idx] : offset + offsets[x_idx] + 4])[0]
                y = struct.unpack(f"{endian_char}f", raw_data[offset + offsets[y_idx] : offset + offsets[y_idx] + 4])[0]
                z = struct.unpack(f"{endian_char}f", raw_data[offset + offsets[z_idx] : offset + offsets[z_idx] + 4])[0]
                positions.append([x, y, z])
            except struct.error:
                continue

        return np.array(positions) if positions else np.empty((0, _N_COORDS))
