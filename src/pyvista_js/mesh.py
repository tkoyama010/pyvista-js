"""Mesh classes for pyvista-js.

Provides geometric primitives and mesh handling compatible with PyVista API.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
from jinja2 import Environment, FileSystemLoader, StrictUndefined

if TYPE_CHECKING:
    from collections.abc import Callable

    from numpy.typing import ArrayLike

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


class PointData:
    """Dict-like container for point data arrays.

    This class provides a dictionary interface for storing named scalar arrays
    associated with mesh points, mimicking PyVista's point_data API.

    Examples
    --------
    >>> import pyvista_js as pv
    >>> import numpy as np
    >>> mesh = pv.Sphere()
    >>> mesh.point_data['elevation'] = mesh.points[:, 2]
    >>> 'elevation' in mesh.point_data
    True

    Render with scalar coloring:

    >>> plotter = pv.Plotter()
    >>> _ = plotter.add_mesh(mesh, scalars='elevation', cmap='viridis')
    >>> plotter.show()  # doctest: +SKIP

    """

    def __init__(self) -> None:
        """Initialize an empty PointData container."""
        self._arrays: dict[str, np.ndarray] = {}

    def __setitem__(self, name: str, array: ArrayLike) -> None:
        """Set a named array.

        Parameters
        ----------
        name : str
            Name of the array.
        array : array-like
            Data array to store.

        """
        self._arrays[name] = np.asarray(array)

    def __getitem__(self, name: str) -> np.ndarray:
        """Get a named array.

        Parameters
        ----------
        name : str
            Name of the array.

        Returns
        -------
        np.ndarray
            The requested array.

        """
        return self._arrays[name]

    def __contains__(self, name: str) -> bool:
        """Check if an array with the given name exists.

        Parameters
        ----------
        name : str
            Name to check.

        Returns
        -------
        bool
            True if the array exists.

        """
        return name in self._arrays

    def __len__(self) -> int:
        """Return the number of arrays."""
        return len(self._arrays)

    def keys(self) -> list[str]:
        """Return the names of all arrays.

        Returns
        -------
        list
            List of array names.

        """
        return list(self._arrays.keys())

    def items(self) -> list[tuple[str, np.ndarray]]:
        """Return (name, array) pairs.

        Returns
        -------
        list
            List of (name, array) tuples.

        """
        return list(self._arrays.items())

    def values(self) -> list[np.ndarray]:
        """Return all arrays.

        Returns
        -------
        list
            List of arrays.

        """
        return list(self._arrays.values())


# Load JavaScript templates relative to this file
_TEMPLATES_DIR = Path(__file__).parent / "templates"
_MESH_SOURCE_TEMPLATE = (_TEMPLATES_DIR / "mesh_source.html").read_text()
_SPHERE_SOURCE_TEMPLATE = (_TEMPLATES_DIR / "sphere_source.html").read_text()
_CUBE_SOURCE_TEMPLATE = (_TEMPLATES_DIR / "cube_source.html").read_text()
_CYLINDER_SOURCE_TEMPLATE = (_TEMPLATES_DIR / "cylinder_source.html").read_text()
_SHRINK_FILTER_TEMPLATE = (_TEMPLATES_DIR / "shrink_filter.html").read_text()
_CLIP_FILTER_TEMPLATE = (_TEMPLATES_DIR / "clip_filter.html").read_text()
_TUBE_FILTER_TEMPLATE = (_TEMPLATES_DIR / "tube_filter.html").read_text()
_CONTOUR_FILTER_TEMPLATE = (_TEMPLATES_DIR / "contour_filter.html").read_text()
_CIRCLE_SOURCE_TEMPLATE = (_TEMPLATES_DIR / "circle_source.html").read_text()
_DISK_SOURCE_TEMPLATE = (_TEMPLATES_DIR / "disk_source.html").read_text()
_ARROW_SOURCE_TEMPLATE = (_TEMPLATES_DIR / "arrow_source.html").read_text()
_CONE_SOURCE_TEMPLATE = (_TEMPLATES_DIR / "cone_source.html").read_text()
_LINE_SOURCE_TEMPLATE = (_TEMPLATES_DIR / "line_source.html").read_text()
_PLANE_SOURCE_TEMPLATE = (_TEMPLATES_DIR / "plane_source.html").read_text()
_GAUSSIAN_SPLAT_SOURCE_TEMPLATE = (_TEMPLATES_DIR / "gaussian_splat_source.html").read_text()
_CIRCLE_MIN_RESOLUTION = 3
_VECTOR_COMPONENTS = 3  # Number of components in a 3D vector (x, y, z)
_TUBE_MIN_SIDES = 3


class PolyData:
    """Base polygonal mesh class.

    Parameters
    ----------
    points : array-like
        Vertex coordinates as an (n, 3) array.
    faces : array-like, optional
        Cell connectivity information.

    """

    def __init__(
        self,
        points: ArrayLike,
        faces: ArrayLike | None = None,
        *,
        t_coords: ArrayLike | None = None,
        scalars: ArrayLike | None = None,
        scalar_name: str = "scalars",
        _vtk_js_source_fn: Callable[[int], str] | None = None,
        _mapper_setup_fn: Callable[[int], str] | None = None,
        _vtk_js_source_is_filter: bool = True,
    ) -> None:
        """Initialize a PolyData mesh."""
        self.points = np.asarray(points)
        self.faces = np.asarray(faces) if faces is not None else None
        self.t_coords = np.asarray(t_coords) if t_coords is not None else None
        self.scalars = np.asarray(scalars) if scalars is not None else None
        self.scalar_name = scalar_name
        self._vtk_js_source_fn = _vtk_js_source_fn
        self._mapper_setup_fn = _mapper_setup_fn
        self._vtk_js_source_is_filter = _vtk_js_source_is_filter
        self._point_data = PointData()

    @property
    def point_data(self) -> PointData:
        """Access point data arrays.

        Returns
        -------
        PointData
            Dict-like container for point data arrays.

        Examples
        --------
        >>> import pyvista_js as pv
        >>> import numpy as np
        >>> mesh = pv.Sphere()
        >>> mesh.point_data['elevation'] = mesh.points[:, 2]
        >>> 'elevation' in mesh.point_data
        True

        Render with scalar coloring:

        >>> plotter = pv.Plotter()
        >>> _ = plotter.add_mesh(mesh, scalars='elevation', cmap='viridis')
        >>> plotter.show()  # doctest: +SKIP

        """
        return self._point_data

    def __setitem__(self, name: str, array: ArrayLike) -> None:
        """Set a point data array using dictionary-style access.

        Parameters
        ----------
        name : str
            Name of the array.
        array : array-like
            Data array to store.

        Examples
        --------
        >>> import pyvista_js as pv
        >>> import numpy as np
        >>> mesh = pv.Sphere()
        >>> mesh['elevation'] = mesh.points[:, 2]
        >>> plotter = pv.Plotter()
        >>> _ = plotter.add_mesh(mesh, scalars='elevation', cmap='viridis')
        >>> plotter.show()  # doctest: +SKIP

        """
        self._point_data[name] = array

    def __getitem__(self, name: str) -> np.ndarray:
        """Get a point data array using dictionary-style access.

        Parameters
        ----------
        name : str
            Name of the array.

        Returns
        -------
        np.ndarray
            The requested array.

        """
        return self._point_data[name]

    @property
    def n_points(self) -> int:
        """Return the number of points."""
        return len(self.points)

    @property
    def is_primitive(self) -> bool:
        """Return whether this mesh is backed by a vtk.js source primitive.

        Returns
        -------
        bool
            ``True`` if the mesh was created from a primitive factory
            (e.g. :func:`Sphere`, :func:`Cube`), ``False`` otherwise.

        """
        return self._vtk_js_source_fn is not None

    @property
    def bounding_sphere(self) -> tuple[float, tuple[float, float, float]]:
        """Compute the radius and center of a bounding sphere.

        Uses Ritter's algorithm to approximate the minimum bounding sphere.
        Returns NaN values if there are no points.

        Returns
        -------
        float, tuple
            Sphere radius as a float and center as a tuple of floats ``(x, y, z)``.

        Examples
        --------
        >>> import pyvista_js as pv
        >>> mesh = pv.Sphere(radius=1.5, center=(1, 2, 3))
        >>> radius, center = mesh.bounding_sphere
        >>> round(radius, 5)
        1.5
        >>> [round(c, 5) for c in center]
        [1.0, 2.0, 3.0]

        """
        if self.n_points == 0:
            nan = float("nan")
            return nan, (nan, nan, nan)

        pts = self.points.astype(float)

        # Ritter's algorithm
        p = pts[0]
        dists = np.linalg.norm(pts - p, axis=1)
        q = pts[np.argmax(dists)]
        dists = np.linalg.norm(pts - q, axis=1)
        r = pts[np.argmax(dists)]

        center = (q + r) / 2.0
        radius = float(np.linalg.norm(r - q) / 2.0)

        for pt in pts:
            d = float(np.linalg.norm(pt - center))
            if d > radius:
                radius = (radius + d) / 2.0
                center = center + (d - radius) / d * (pt - center)

        return radius, (float(center[0]), float(center[1]), float(center[2]))

    @property
    def n_faces(self) -> int:
        """Return the number of faces."""
        return len(self.faces) if self.faces is not None else 0

    def plot(
        self,
        color: str | tuple[float, float, float] | None = None,
        opacity: float = 1.0,
        pbr: bool = False,  # noqa: FBT001 FBT002
        metallic: float = 0.0,
        roughness: float = 0.5,
    ) -> None:
        """Plot this mesh.

        This is a convenience method that creates a :class:`~pyvista_js.Plotter`,
        adds this mesh, and calls :func:`~pyvista_js.Plotter.show`.

        Parameters
        ----------
        color : str or tuple, optional
            Color of the mesh. Can be a color name or RGB tuple.
        opacity : float, optional
            Opacity of the mesh, between 0 (transparent) and 1 (opaque).
        pbr : bool, optional
            Enable physically based rendering (PBR). Default is False.
        metallic : float, optional
            Metallic factor for PBR, between 0 and 1. Default is 0.0.
        roughness : float, optional
            Roughness factor for PBR, between 0 and 1. Default is 0.5.

        Examples
        --------
        >>> import pyvista_js as pv
        >>> sphere = pv.Sphere()
        >>> sphere.plot(color='red')  # doctest: +SKIP

        """
        from .plotter import Plotter  # noqa: PLC0415

        plotter = Plotter()
        plotter.add_mesh(
            self,
            color=color,
            opacity=opacity,
            pbr=pbr,
            metallic=metallic,
            roughness=roughness,
        )
        plotter.show()

    def save(self, filename: str | Path) -> None:
        """Write this mesh to disk using meshio.

        The file format is inferred from the extension of ``filename``.
        Any format supported by `meshio <https://github.com/nschloe/meshio>`_
        can be used (e.g. ``'.obj'``, ``'.vtk'``, ``'.ply'``, ``'.stl'``).

        .. note::

            Requires ``meshio`` to be installed::

                pip install "pyvista-js[io]"

            In Pyodide / JupyterLite, install it with micropip before calling
            this method::

                import micropip
                await micropip.install("meshio")

        Parameters
        ----------
        filename : str or Path
            Output path. The extension determines the file format.

        Returns
        -------
        None

        Raises
        ------
        ImportError
            If ``meshio`` is not installed.

        Examples
        --------
        >>> from pyvista_js import examples
        >>> mesh = examples.download_trumpet()  # doctest: +SKIP
        >>> mesh.save('trumpet.obj')  # doctest: +SKIP

        """
        try:
            import meshio  # noqa: PLC0415
        except ImportError:
            msg = (
                "meshio is required for save(). "
                "Install it with: pip install 'pyvista-js[io]'\n"
                "In Pyodide: await micropip.install('meshio')"
            )
            raise ImportError(msg) from None

        cells = self._meshio_cells()
        mesh = meshio.Mesh(points=self.points, cells=cells)
        mesh.write(str(filename))

    def _meshio_cells(self) -> list:
        """Build a meshio-compatible cell list from ``self.faces``."""
        if self.faces is None or len(self.faces) == 0:
            return []

        from collections import defaultdict  # noqa: PLC0415

        groups: dict = defaultdict(list)
        for face in self.faces:
            groups[len(face)].append(face)

        _CELL_TYPES = {3: "triangle", 4: "quad"}  # noqa: N806
        return [(_CELL_TYPES.get(n, "polygon"), np.array(faces)) for n, faces in groups.items()]

    def shrink(self, shrink_factor: float = 0.8) -> PolyData:
        """Shrink the cells of a mesh towards their centroid.

        This filter shrinks the individual cells of a mesh towards their
        centroids, producing visual separation between adjacent cells.
        It mirrors the PyVista ``shrink`` filter API.

        .. note::

            The shrink is computed in JavaScript at render time by
            iterating over the cell array from the vtk.js source,
            moving each vertex toward its cell's centroid.
            ``vtk.js`` does not include ``vtkShrinkFilter``, so this
            filter is implemented as a custom JavaScript pass.

        Parameters
        ----------
        shrink_factor : float, optional
            The factor to shrink each cell by, between 0 and 1.
            A value of 1.0 produces no change; lower values produce
            more shrinkage. Default is 0.8.

        Returns
        -------
        PolyData
            A new mesh with shrunk cells.

        Examples
        --------
        >>> import pyvista_js as pv
        >>> sphere = pv.Sphere()
        >>> shrunk = sphere.shrink(shrink_factor=0.8)
        >>> isinstance(shrunk, pv.PolyData)
        True

        Render the shrunk mesh:

        >>> shrunk.plot()  # doctest: +SKIP

        """
        if not (0.0 <= shrink_factor <= 1.0):
            msg = f"shrink_factor must be between 0 and 1, got {shrink_factor}"
            raise ValueError(msg)

        orig_vtk_js_source_fn = self._vtk_js_source_fn

        def _vtk_js_source_with_shrink(idx: int) -> str:
            base = orig_vtk_js_source_fn(idx) if orig_vtk_js_source_fn is not None else ""
            shrink_code = _render(
                _SHRINK_FILTER_TEMPLATE,
                SOURCE=f"source{idx}",
                SHRUNK_PD=f"shrunkPD{idx}",
                SHRINK_FACTOR=str(shrink_factor),
            )
            return base + "\n" + shrink_code

        def _mapper_setup_shrink(idx: int) -> str:
            return f"mapper{idx}.setInputData(shrunkPD{idx});"

        return PolyData(
            points=self.points,
            faces=self.faces,
            _vtk_js_source_fn=_vtk_js_source_with_shrink,
            _mapper_setup_fn=_mapper_setup_shrink,
        )

    def clip(
        self,
        normal: str | tuple[float, float, float] = "x",
        origin: tuple[float, float, float] | None = None,
        *,
        invert: bool = False,
    ) -> PolyData:
        """Clip the mesh with a plane.

        This filter clips the mesh with a plane defined by a normal vector
        and an origin point. Points on one side of the plane are removed.
        It mirrors the PyVista ``clip`` filter API.

        .. note::

            The clipping is computed in JavaScript at render time by
            evaluating the signed distance of each vertex from the clip plane.
            Cells with all vertices on the clipped side are removed.
            ``vtk.js`` does not include a built-in clipping filter with
            the exact PyVista API, so this filter is implemented as a
            custom JavaScript pass.

        Parameters
        ----------
        normal : str or tuple of float, optional
            The normal vector of the clipping plane. Can be a string
            specifying a cardinal direction ('x', 'y', 'z', '-x', '-y', '-z')
            or a 3-tuple of floats (nx, ny, nz). Default is 'x'.
        origin : tuple of float, optional
            The origin point of the clipping plane as (x, y, z).
            If not provided, defaults to the center of the mesh's bounding box.
        invert : bool, optional
            If True, flip the clipping direction to keep the part that would
            normally be removed. Default is False.

        Returns
        -------
        PolyData
            A new mesh with clipped cells removed.

        Examples
        --------
        >>> import pyvista_js as pv
        >>> sphere = pv.Sphere()
        >>> clipped = sphere.clip(normal='x', origin=(0, 0, 0))
        >>> isinstance(clipped, pv.PolyData)
        True

        Clip along the negative Y axis:

        >>> clipped = sphere.clip(normal='-y')
        >>> isinstance(clipped, pv.PolyData)
        True

        Clip with a custom normal vector:

        >>> clipped = sphere.clip(normal=(1, 1, 0), origin=(0, 0, 0))
        >>> isinstance(clipped, pv.PolyData)
        True

        Render the clipped mesh:

        >>> clipped.plot()  # doctest: +SKIP

        """
        # Parse normal vector
        if isinstance(normal, str):
            normal_map = {
                "x": (1.0, 0.0, 0.0),
                "+x": (1.0, 0.0, 0.0),
                "-x": (-1.0, 0.0, 0.0),
                "y": (0.0, 1.0, 0.0),
                "+y": (0.0, 1.0, 0.0),
                "-y": (0.0, -1.0, 0.0),
                "z": (0.0, 0.0, 1.0),
                "+z": (0.0, 0.0, 1.0),
                "-z": (0.0, 0.0, -1.0),
            }
            if normal not in normal_map:
                msg = f"Invalid normal string '{normal}'. Must be one of {list(normal_map.keys())}"
                raise ValueError(msg)
            normal_vec = normal_map[normal]
        else:
            if len(normal) != _VECTOR_COMPONENTS:  # type: ignore[arg-type]
                msg = f"Normal vector must have {_VECTOR_COMPONENTS} components, got {len(normal)}"  # type: ignore[arg-type]
                raise ValueError(msg)
            n = [float(x) for x in normal]  # type: ignore[arg-type]
            normal_vec = (n[0], n[1], n[2])

        # Compute origin if not provided (use center of bounding box)
        if origin is None:
            pts = self.points
            origin = (
                float((pts[:, 0].min() + pts[:, 0].max()) / 2),
                float((pts[:, 1].min() + pts[:, 1].max()) / 2),
                float((pts[:, 2].min() + pts[:, 2].max()) / 2),
            )
        else:
            if len(origin) != _VECTOR_COMPONENTS:
                msg = f"Origin must have {_VECTOR_COMPONENTS} components, got {len(origin)}"
                raise ValueError(msg)
            o = [float(x) for x in origin]
            origin = (o[0], o[1], o[2])

        orig_vtk_js_source_fn = self._vtk_js_source_fn

        def _vtk_js_source_with_clip(idx: int) -> str:
            base = orig_vtk_js_source_fn(idx) if orig_vtk_js_source_fn is not None else ""
            clip_code = _render(
                _CLIP_FILTER_TEMPLATE,
                SOURCE=f"source{idx}",
                CLIPPED_PD=f"clippedPD{idx}",
                NORMAL_X=str(normal_vec[0]),
                NORMAL_Y=str(normal_vec[1]),
                NORMAL_Z=str(normal_vec[2]),
                ORIGIN_X=str(origin[0]),
                ORIGIN_Y=str(origin[1]),
                ORIGIN_Z=str(origin[2]),
                INVERT="true" if invert else "false",
            )
            return base + "\n" + clip_code

        def _mapper_setup_clip(idx: int) -> str:
            return f"mapper{idx}.setInputData(clippedPD{idx});"

        return PolyData(
            points=self.points,
            faces=self.faces,
            _vtk_js_source_fn=_vtk_js_source_with_clip,
            _mapper_setup_fn=_mapper_setup_clip,
        )

    def tube(
        self,
        *,
        radius: float = 0.5,
        n_sides: int = 20,
        capping: bool = True,
    ) -> PolyData:
        """Generate a tube around a line polydata.

        This filter creates a tube representation around lines in the mesh
        by sweeping a polygonal cross-section along each line. It mirrors
        the PyVista ``tube`` filter API and is backed by vtk.js's
        ``vtkTubeFilter``.

        .. note::

            This filter is intended for use with line-based polydata (such as
            the output of :class:`Line`). It uses vtk.js's ``vtkTubeFilter``,
            which generates a tube by sweeping a circle with ``n_sides`` sides
            along the line segments.

        Parameters
        ----------
        radius : float, optional
            The radius of the tube. Default is 0.5.
        n_sides : int, optional
            The number of sides for the tube cross-section.
            Higher values produce smoother tubes. Default is 20.
        capping : bool, optional
            Whether to cap the ends of the tube. Default is True.

        Returns
        -------
        PolyData
            A new mesh representing the tube.

        Examples
        --------
        >>> import pyvista_js as pv
        >>> line = pv.Line()
        >>> tube = line.tube(radius=0.05, n_sides=20)
        >>> isinstance(tube, pv.PolyData)
        True

        Render the tube:

        >>> tube.plot()  # doctest: +SKIP

        """
        if radius <= 0:
            msg = f"radius must be positive, got {radius}"
            raise ValueError(msg)
        if n_sides < _TUBE_MIN_SIDES:
            msg = f"n_sides must be at least {_TUBE_MIN_SIDES}, got {n_sides}"
            raise ValueError(msg)

        orig_vtk_js_source_fn = self._vtk_js_source_fn

        def _vtk_js_source_with_tube(idx: int) -> str:
            base = orig_vtk_js_source_fn(idx) if orig_vtk_js_source_fn is not None else ""
            tube_code = _render(
                _TUBE_FILTER_TEMPLATE,
                SOURCE=f"source{idx}",
                TUBED_PD=f"tubedPD{idx}",
                TUBE_FILTER=f"tubeFilter{idx}",
                RADIUS=str(radius),
                N_SIDES=str(n_sides),
                CAPPING="true" if capping else "false",
            )
            return base + "\n" + tube_code

        def _mapper_setup_tube(idx: int) -> str:
            return f"mapper{idx}.setInputData(tubedPD{idx});"

        return PolyData(
            points=self.points,
            faces=self.faces,
            _vtk_js_source_fn=_vtk_js_source_with_tube,
            _mapper_setup_fn=_mapper_setup_tube,
        )

    def contour(
        self,
        isosurfaces: int | list[float] = 10,
        scalars: ArrayLike | None = None,
        scalar_name: str | None = None,
    ) -> PolyData:
        """Generate contour lines at constant scalar values.

        This filter extracts isolines from the mesh at specified scalar values
        using a marching triangles algorithm implemented in JavaScript.
        It mirrors the PyVista ``contour`` filter API.

        .. note::

            The contour is computed in JavaScript at render time by applying
            the marching triangles algorithm to each triangle of the mesh,
            interpolating edge crossings at the specified iso-values.
            ``vtk.js`` does not support ``vtkPolyData`` input for
            ``vtkContourFilter``, so this filter is implemented as a custom
            JavaScript pass.

        Parameters
        ----------
        isosurfaces : int or list of float, optional
            Number of evenly spaced contours to generate, or a list of explicit
            scalar values at which to generate contours. Default is 10.
        scalars : array-like, optional
            Scalar values per point to use for contouring. If not provided,
            uses the mesh's existing ``scalars`` attribute. Must have length
            equal to ``n_points``.
        scalar_name : str, optional
            Name for the scalar array in vtk.js. If not provided, uses the
            mesh's existing ``scalar_name`` attribute or defaults to "scalars".

        Returns
        -------
        PolyData
            A new mesh containing the contour lines.

        Raises
        ------
        ValueError
            If no scalars are provided and the mesh has no scalar data, or if
            isosurfaces parameter is invalid.

        Examples
        --------
        >>> import pyvista_js as pv
        >>> sphere = pv.Sphere()
        >>> sphere_scalars = sphere.points[:, 2]
        >>> contours = sphere.contour(isosurfaces=5, scalars=sphere_scalars)
        >>> isinstance(contours, pv.PolyData)
        True

        Generate contours at specific values:

        >>> contours = sphere.contour(isosurfaces=[-0.5, 0.0, 0.5], scalars=sphere_scalars)

        Render the contours:

        >>> contours.plot()

        """
        # Determine scalar data to use
        scalar_data = self._get_contour_scalars(scalars)

        # Determine scalar name
        scalar_name_final = scalar_name or self.scalar_name

        # Generate contour values
        contour_values = self._get_contour_values(isosurfaces, scalar_data)

        # Build the vtk.js source function
        orig_vtk_js_source_fn = self._vtk_js_source_fn

        def _vtk_js_source_with_contour(idx: int) -> str:
            base = self._get_base_source(idx, orig_vtk_js_source_fn)
            scalar_injection = self._build_scalar_injection(idx, scalar_data, scalar_name_final)
            contour_code = self._build_contour_code(idx, contour_values)
            return base + "\n" + scalar_injection + "\n" + contour_code

        def _mapper_setup_contour(idx: int) -> str:
            return f"mapper{idx}.setInputData(contourPD{idx});"

        # Return new PolyData with contour filter applied
        return PolyData(
            points=self.points,
            faces=self.faces,
            scalars=scalar_data,
            scalar_name=scalar_name_final,
            _vtk_js_source_fn=_vtk_js_source_with_contour,
            _mapper_setup_fn=_mapper_setup_contour,
        )

    def _get_contour_scalars(self, scalars: ArrayLike | None) -> np.ndarray:
        """Get scalar data for contouring, validating length."""
        if scalars is not None:
            scalar_data = np.asarray(scalars)
        elif self.scalars is not None:
            scalar_data = self.scalars
        else:
            msg = "No scalar data provided. Pass scalars parameter or set mesh.scalars"
            raise ValueError(msg)

        if len(scalar_data) != self.n_points:
            msg = f"scalars must have length {self.n_points}, got {len(scalar_data)}"
            raise ValueError(msg)

        return scalar_data

    def _get_contour_values(
        self,
        isosurfaces: int | list[float],
        scalar_data: np.ndarray,
    ) -> list[float]:
        """Generate contour values from isosurfaces parameter."""
        if isinstance(isosurfaces, int):
            if isosurfaces < 1:
                msg = f"isosurfaces must be >= 1 when int, got {isosurfaces}"
                raise ValueError(msg)
            scalar_min, scalar_max = float(scalar_data.min()), float(scalar_data.max())
            return np.linspace(scalar_min, scalar_max, isosurfaces).tolist()

        contour_values = [float(v) for v in isosurfaces]
        if len(contour_values) < 1:
            msg = "isosurfaces list must contain at least one value"
            raise ValueError(msg)
        return contour_values

    def _get_base_source(
        self,
        idx: int,
        orig_vtk_js_source_fn: Callable[[int], str] | None,
    ) -> str:
        """Generate base vtk.js source code."""
        if orig_vtk_js_source_fn is not None:
            return orig_vtk_js_source_fn(idx)

        # Default implementation for generic meshes
        points_flat = self.points.flatten().tolist()
        points_str = ",".join(map(str, points_flat))
        return _MESH_SOURCE_TEMPLATE.replace("{{INDEX}}", str(idx)).replace(
            "{{POINTS_DATA}}",
            points_str,
        )

    def _build_scalar_injection(
        self,
        idx: int,
        scalar_data: np.ndarray,
        scalar_name: str,
    ) -> str:
        """Build JavaScript code to inject scalar data."""
        scalars_flat = scalar_data.flatten().tolist()
        scalars_str = ",".join(map(str, scalars_flat))
        return (
            f"\n// Inject scalar data for contouring\n"
            f"(function() {{\n"
            f"  var pd = (typeof source{idx}.getOutputData === 'function') ? "
            f"source{idx}.getOutputData(0) : source{idx};\n"
            f"  var scalars{idx} = vtk.Common.Core.vtkDataArray.newInstance({{\n"
            f"    numberOfComponents: 1,\n"
            f"    values: Float32Array.from([{scalars_str}]),\n"
            f"    name: '{scalar_name}'\n"
            f"  }});\n"
            f"  pd.getPointData().setScalars(scalars{idx});\n"
            f"}})();\n"
        )

    def _build_contour_code(
        self,
        idx: int,
        contour_values: list[float],
    ) -> str:
        """Build JavaScript code for contour filter."""
        values_str = ",".join(map(str, contour_values))
        return _render(
            _CONTOUR_FILTER_TEMPLATE,
            INDEX=str(idx),
            CONTOUR_VALUES=values_str,
        )

    def texture_map_to_plane(self) -> PolyData:
        """Generate texture coordinates by projecting points onto the XY plane.

        Maps the mesh's X and Y extents to UV coordinates in the [0, 1] range.
        This mirrors the PyVista :meth:`pyvista.DataSet.texture_map_to_plane` API.

        Returns
        -------
        PolyData
            A new mesh with texture coordinates (``t_coords``) set.

        Examples
        --------
        >>> import pyvista_js as pv
        >>> mesh = pv.Sphere()
        >>> mapped = mesh.texture_map_to_plane()
        >>> mapped.t_coords is not None
        True
        >>> mapped.t_coords.shape == (mesh.n_points, 2)
        True

        """
        pts = self.points.astype(float)
        x_min, x_max = float(pts[:, 0].min()), float(pts[:, 0].max())
        y_min, y_max = float(pts[:, 1].min()), float(pts[:, 1].max())
        x_range = x_max - x_min or 1.0
        y_range = y_max - y_min or 1.0

        u = (pts[:, 0] - x_min) / x_range
        v = (pts[:, 1] - y_min) / y_range
        t_coords = np.column_stack([u, v])

        return PolyData(
            points=self.points,
            faces=self.faces,
            t_coords=t_coords,
            scalars=self.scalars,
            scalar_name=self.scalar_name,
            _vtk_js_source_fn=self._vtk_js_source_fn,
            _mapper_setup_fn=self._mapper_setup_fn,
        )

    def generate_vtk_js_source(self, idx: int) -> str:
        """Generate vtk.js source code for this mesh.

        Parameters
        ----------
        idx : int
            Index of this mesh in the rendering pipeline.

        Returns
        -------
        str
            JavaScript code to create the vtk.js source for this mesh.

        """
        if self._vtk_js_source_fn is not None:
            source_code = self._vtk_js_source_fn(idx)
        else:
            # Default implementation for generic meshes using polydata
            points_flat = self.points.flatten().tolist()
            points_str = ",".join(map(str, points_flat))
            source_code = _render(
                _MESH_SOURCE_TEMPLATE,
                SOURCE=f"source{idx}",
                POINTS_DATA=points_str,
            )

        # Inject texture coordinates into the generic polydata (not primitives).
        # Primitive sources (Sphere, Cube, Cylinder) auto-generate TCoords via vtk.js.
        if self.t_coords is not None and self._vtk_js_source_fn is None:
            tcoords_flat = self.t_coords.flatten().tolist()
            tcoords_str = ",".join(map(str, tcoords_flat))
            source_code += (
                f"\n// Inject texture coordinates\n"
                f"const tcoords{idx} = vtk.Common.Core.vtkDataArray.newInstance({{\n"
                f"  numberOfComponents: 2,\n"
                f"  values: Float32Array.from([{tcoords_str}]),\n"
                f"  name: 'TextureCoordinates'\n"
                f"}});\n"
                f"polydata{idx}.getPointData().setTCoords(tcoords{idx});\n"
            )

        # Inject point data scalar arrays
        if len(self._point_data) > 0:
            # For primitives (source-based), make polydata{idx} available.
            # For generic meshes, polydata{idx} already exists (from mesh_source.js).
            if self._vtk_js_source_fn is not None:
                if self._vtk_js_source_is_filter:
                    # source{idx} is a vtk.js filter - extract its output polydata
                    source_code += (
                        f"\n// Extract output polydata from source for scalar injection\n"
                        f"source{idx}.update();\n"
                        f"const polydata{idx} = source{idx}.getOutputData();\n"
                    )
                else:
                    # source{idx} is already a vtkPolyData - alias it directly
                    source_code += (
                        f"\n// source{idx} is already a vtkPolyData\n"
                        f"const polydata{idx} = source{idx};\n"
                    )

            for name, array in self._point_data.items():
                array_flat = array.flatten().tolist()
                array_str = ",".join(map(str, array_flat))
                # Determine number of components based on array shape
                if array.ndim == 1:
                    n_components = 1
                elif array.ndim == 2:  # noqa: PLR2004
                    n_components = array.shape[1]
                else:
                    msg = f"Point data array '{name}' must be 1D or 2D, got shape {array.shape}"
                    raise ValueError(msg)

                safe_name = name.replace(" ", "_")
                source_code += (
                    f"\n// Inject point data array '{name}'\n"
                    f"const pointArray{idx}_{safe_name} = "
                    f"vtk.Common.Core.vtkDataArray.newInstance({{\n"
                    f"  numberOfComponents: {n_components},\n"
                    f"  values: Float32Array.from([{array_str}]),\n"
                    f"  name: '{name}'\n"
                    f"}});\n"
                    f"polydata{idx}.getPointData().addArray("
                    f"pointArray{idx}_{safe_name});\n"
                )

        return source_code

    def get_mapper_setup(self, idx: int) -> str:
        """Get the mapper setup code for this mesh.

        Parameters
        ----------
        idx : int
            Index of this mesh in the rendering pipeline.

        Returns
        -------
        str
            JavaScript code to set up the mapper for this mesh.

        """
        if self._mapper_setup_fn is not None:
            return self._mapper_setup_fn(idx)
        return f"mapper{idx}.setInputData(source{idx});"

    def __getstate__(self) -> dict[str, object]:
        """Return state for pickling.

        Excludes the unpicklable callable functions (_vtk_js_source_fn and
        _mapper_setup_fn), keeping only the serializable mesh data.

        Returns
        -------
        dict
            State dictionary containing points, faces, texture coordinates,
            point data, and source type flag.

        """
        return {
            "points": self.points,
            "faces": self.faces,
            "t_coords": self.t_coords,
            "_point_data": self._point_data,
            "_vtk_js_source_is_filter": self._vtk_js_source_is_filter,
        }

    def __setstate__(self, state: dict[str, object]) -> None:
        """Restore state from pickle.

        Reconstructs the mesh from pickled state. Note that primitive
        meshes will lose their vtk.js source functions and will be
        treated as generic PolyData after unpickling.

        Parameters
        ----------
        state : dict
            State dictionary from __getstate__.

        """
        self.points = state["points"]  # type: ignore[assignment]
        self.faces = state["faces"]  # type: ignore[assignment]
        self.t_coords = state["t_coords"]  # type: ignore[assignment]
        self._point_data = state["_point_data"]  # type: ignore[assignment]
        self._vtk_js_source_is_filter = state["_vtk_js_source_is_filter"]  # type: ignore[assignment]
        # Set unpicklable callables to None
        self._vtk_js_source_fn = None
        self._mapper_setup_fn = None


def Sphere(  # noqa: N802
    radius: float = 1.0,
    center: tuple[float, float, float] = (0.0, 0.0, 0.0),
    theta_resolution: int = 30,
    phi_resolution: int = 30,
) -> PolyData:
    """Create a sphere mesh.

    Parameters
    ----------
    radius : float, optional
        Sphere radius. Default is 1.0.
    center : tuple, optional
        Center of the sphere (x, y, z). Default is (0, 0, 0).
    theta_resolution : int, optional
        Number of points in the azimuthal direction. Default is 30.
    phi_resolution : int, optional
        Number of points in the polar direction. Default is 30.

    Returns
    -------
    PolyData
        A sphere mesh.

    Examples
    --------
    >>> import pyvista_js as pv
    >>> sphere = pv.Sphere(radius=1.0)
    >>> sphere.n_points
    842

    """
    # Generate points matching vtk.js vtkSphereSource ordering exactly:
    #   index 0: north pole
    #   index 1: south pole
    #   then theta (outer) x phi (inner) for intermediate rows
    # phi[j] = j * pi / (phi_resolution - 1)  for j = 1 .. phi_resolution-2
    # theta[i] = i * 2*pi / theta_resolution   for i = 0 .. theta_resolution-1
    delta_phi = np.pi / (phi_resolution - 1)
    delta_theta = 2.0 * np.pi / theta_resolution

    points = []
    # North pole (index 0)
    points.append([center[0], center[1], center[2] + radius])
    # South pole (index 1)
    points.append([center[0], center[1], center[2] - radius])
    # Intermediate points: theta outer loop, phi inner loop
    for i in range(theta_resolution):
        theta = i * delta_theta
        for j in range(1, phi_resolution - 1):
            phi = j * delta_phi
            x = radius * np.sin(phi) * np.cos(theta) + center[0]
            y = radius * np.sin(phi) * np.sin(theta) + center[1]
            z = radius * np.cos(phi) + center[2]
            points.append([x, y, z])

    def _vtk_js_source(idx: int) -> str:
        return _render(
            _SPHERE_SOURCE_TEMPLATE,
            SOURCE=f"source{idx}",
            TEX_MAP_SPHERE=f"texMapSphere{idx}",
            CENTER_X=str(center[0]),
            CENTER_Y=str(center[1]),
            CENTER_Z=str(center[2]),
            RADIUS=str(radius),
            THETA_RESOLUTION=str(theta_resolution),
            PHI_RESOLUTION=str(phi_resolution),
        )

    def _mapper_setup_sphere(idx: int) -> str:
        return f"mapper{idx}.setInputConnection(texMapSphere{idx}.getOutputPort());"

    return PolyData(
        points=np.array(points),
        _vtk_js_source_fn=_vtk_js_source,
        _mapper_setup_fn=_mapper_setup_sphere,
    )


def Cube(  # noqa: N802
    center: tuple[float, float, float] = (0.0, 0.0, 0.0),
    x_length: float = 1.0,
    y_length: float = 1.0,
    z_length: float = 1.0,
) -> PolyData:
    """Create a cube mesh.

    Parameters
    ----------
    center : tuple, optional
        Center of the cube (x, y, z). Default is (0, 0, 0).
    x_length : float, optional
        Length in x direction. Default is 1.0.
    y_length : float, optional
        Length in y direction. Default is 1.0.
    z_length : float, optional
        Length in z direction. Default is 1.0.

    Returns
    -------
    PolyData
        A cube mesh.

    Examples
    --------
    >>> import pyvista_js as pv
    >>> cube = pv.Cube()
    >>> cube.n_points
    24

    """
    x, y, z = center
    dx, dy, dz = x_length / 2, y_length / 2, z_length / 2

    # Generate 24 points matching vtk.js vtkCubeSource ordering:
    # 4 points per face, 6 faces (3 axis pairs), each corner duplicated 3x with face normal.
    # Block 1 - X-facing faces (i=0: -hx face, i=1: +hx face), inner order: j(y), k(z)
    # Block 2 - Y-facing faces (i=0: -hy face, i=1: +hy face), inner order: j(x), k(z)
    # Block 3 - Z-facing faces (i=0: -hz face, i=1: +hz face), inner order: j(y), k(x)
    px = [x - dx, x + dx]
    py = [y - dy, y + dy]
    pz = [z - dz, z + dz]
    points = np.array(
        [
            # Block 1: X-facing faces
            [px[0], py[0], pz[0]],
            [px[0], py[0], pz[1]],
            [px[0], py[1], pz[0]],
            [px[0], py[1], pz[1]],
            [px[1], py[0], pz[0]],
            [px[1], py[0], pz[1]],
            [px[1], py[1], pz[0]],
            [px[1], py[1], pz[1]],
            # Block 2: Y-facing faces
            [px[0], py[0], pz[0]],
            [px[0], py[0], pz[1]],
            [px[1], py[0], pz[0]],
            [px[1], py[0], pz[1]],
            [px[0], py[1], pz[0]],
            [px[0], py[1], pz[1]],
            [px[1], py[1], pz[0]],
            [px[1], py[1], pz[1]],
            # Block 3: Z-facing faces
            [px[0], py[0], pz[0]],
            [px[1], py[0], pz[0]],
            [px[0], py[1], pz[0]],
            [px[1], py[1], pz[0]],
            [px[0], py[0], pz[1]],
            [px[1], py[0], pz[1]],
            [px[0], py[1], pz[1]],
            [px[1], py[1], pz[1]],
        ],
    )

    faces = np.array(
        [
            [0, 1, 2, 3],  # Bottom
            [4, 5, 6, 7],  # Top
            [0, 1, 5, 4],  # Front
            [2, 3, 7, 6],  # Back
            [0, 3, 7, 4],  # Left
            [1, 2, 6, 5],  # Right
        ],
    )

    def _vtk_js_source(idx: int) -> str:
        return _render(
            _CUBE_SOURCE_TEMPLATE,
            SOURCE=f"source{idx}",
            CENTER_X=str(center[0]),
            CENTER_Y=str(center[1]),
            CENTER_Z=str(center[2]),
            X_LENGTH=str(x_length),
            Y_LENGTH=str(y_length),
            Z_LENGTH=str(z_length),
        )

    def _mapper_setup_cube(idx: int) -> str:
        return f"mapper{idx}.setInputConnection(source{idx}.getOutputPort());"

    return PolyData(
        points=points,
        faces=faces,
        _vtk_js_source_fn=_vtk_js_source,
        _mapper_setup_fn=_mapper_setup_cube,
    )


def Cylinder(  # noqa: N802
    center: tuple[float, float, float] = (0.0, 0.0, 0.0),
    direction: tuple[float, float, float] = (1.0, 0.0, 0.0),  # noqa: ARG001
    radius: float = 0.5,
    height: float = 1.0,
    resolution: int = 100,
) -> PolyData:
    """Create a cylinder mesh.

    Parameters
    ----------
    center : tuple, optional
        Center of the cylinder (x, y, z). Default is (0, 0, 0).
    direction : tuple, optional
        Direction vector of the cylinder axis. Default is (1, 0, 0).
    radius : float, optional
        Radius of the cylinder. Default is 0.5.
    height : float, optional
        Height of the cylinder. Default is 1.0.
    resolution : int, optional
        Number of points around the cylinder. Default is 100.

    Returns
    -------
    PolyData
        A cylinder mesh.

    Examples
    --------
    >>> import pyvista_js as pv
    >>> cylinder = pv.Cylinder(radius=1.0, height=2.0)

    """
    # Generate points matching vtk.js vtkCylinderSource ordering (capping=true default):
    # Cylinder axis is Y. Total = 4 * resolution points:
    #   indices 0..2R-1:   side wall, interleaved pairs [y=+h/2, y=-h/2] per angle step
    #   indices 2R..3R-1:  top cap ring at y=+h/2, forward angular order
    #   indices 3R..4R-1:  bottom cap ring at y=-h/2, REVERSED angular order
    # x = radius*cos(i*angle), z = -radius*sin(i*angle) (vtk.js uses -sin for z)
    angle = 2.0 * np.pi / resolution
    cx, cy, cz = center
    points_list = []
    # Side wall
    for i in range(resolution):
        px = radius * np.cos(i * angle) + cx
        pz = -radius * np.sin(i * angle) + cz
        points_list.append([px, cy + height / 2, pz])  # y = +h/2
        points_list.append([px, cy - height / 2, pz])  # y = -h/2
    # Top cap (forward order, y = +h/2)
    points_list.extend(
        [radius * np.cos(i * angle) + cx, cy + height / 2, -radius * np.sin(i * angle) + cz]
        for i in range(resolution)
    )
    # Bottom cap (reversed order, y = -h/2)
    points_list.extend(
        [
            radius * np.cos((resolution - 1 - k) * angle) + cx,
            cy - height / 2,
            -radius * np.sin((resolution - 1 - k) * angle) + cz,
        ]
        for k in range(resolution)
    )
    points = np.array(points_list)

    def _vtk_js_source(idx: int) -> str:
        return _render(
            _CYLINDER_SOURCE_TEMPLATE,
            SOURCE=f"source{idx}",
            CENTER_X=str(center[0]),
            CENTER_Y=str(center[1]),
            CENTER_Z=str(center[2]),
            RADIUS=str(radius),
            HEIGHT=str(height),
            RESOLUTION=str(resolution),
        )

    def _mapper_setup_cylinder(idx: int) -> str:
        return f"mapper{idx}.setInputConnection(source{idx}.getOutputPort());"

    return PolyData(
        points=points,
        _vtk_js_source_fn=_vtk_js_source,
        _mapper_setup_fn=_mapper_setup_cylinder,
    )


def Disc(  # noqa: N802, PLR0913
    center: tuple[float, float, float] = (0.0, 0.0, 0.0),
    inner: float = 0.25,
    outer: float = 0.5,
    normal: tuple[float, float, float] = (0.0, 0.0, 1.0),
    r_res: int = 1,
    c_res: int = 6,
) -> PolyData:
    """Create a disc (annular ring) geometric primitive.

    This mirrors the :func:`pyvista.Disc` API.  The geometry is built
    directly from ``(r_res + 1)`` rings of ``c_res`` points each, connected
    as triangles, so it renders correctly in vtk.js without depending on any
    specific vtk.js source filter.

    Parameters
    ----------
    center : tuple, optional
        Center of the disc (x, y, z). Default is (0, 0, 0).
    inner : float, optional
        Inner radius of the disc. Default is 0.25.
    outer : float, optional
        Outer radius of the disc. Default is 0.5.
    normal : tuple, optional
        Normal vector of the disc. Default is (0, 0, 1).
    r_res : int, optional
        Number of radial subdivisions. Default is 1.
    c_res : int, optional
        Number of circumferential subdivisions. Default is 6.

    Returns
    -------
    PolyData
        A disc (annular ring) mesh.

    Examples
    --------
    >>> import pyvista_js as pv
    >>> disc = pv.Disc(center=(0, 0, 0), inner=0.25, outer=0.5)
    >>> disc.n_points
    12

    >>> disc.plot()  # doctest: +SKIP

    """
    # Generate points matching vtk.js vtkDiskSource ordering:
    # outer loop circumferential (i), inner loop radial (j)
    # point index = i * (r_res + 1) + j
    theta_step = 2.0 * np.pi / c_res
    delta_r = (outer - inner) / r_res
    pts_list = []
    for i in range(c_res):
        theta = i * theta_step
        cos_t = np.cos(theta)
        sin_t = np.sin(theta)
        for j in range(r_res + 1):
            r = inner + j * delta_r
            pts_list.append([r * cos_t, r * sin_t, 0.0])
    pts = np.array(pts_list)

    # Build triangular faces: two triangles per quad between adjacent rings
    faces = []
    for i in range(c_res):
        next_i = (i + 1) % c_res
        for j in range(r_res):
            p0 = i * (r_res + 1) + j
            p1 = p0 + 1
            p2 = next_i * (r_res + 1) + j + 1
            p3 = p2 - 1
            faces.append([p0, p1, p2])
            faces.append([p0, p2, p3])

    # Rotate from default normal (0,0,1) to requested normal
    n = np.asarray(normal, dtype=float)
    n = n / np.linalg.norm(n)
    z = np.array([0.0, 0.0, 1.0])
    if not np.allclose(n, z):
        if np.allclose(n, -z):
            pts[:, 2] = -pts[:, 2]
        else:
            axis = np.cross(z, n)
            axis = axis / np.linalg.norm(axis)
            angle = np.arccos(np.clip(np.dot(z, n), -1.0, 1.0))
            c, s = np.cos(angle), np.sin(angle)
            t_val = 1.0 - c
            ax, ay, az = axis
            rot = np.array(
                [
                    [t_val * ax * ax + c, t_val * ax * ay - s * az, t_val * ax * az + s * ay],
                    [t_val * ax * ay + s * az, t_val * ay * ay + c, t_val * ay * az - s * ax],
                    [t_val * ax * az - s * ay, t_val * ay * az + s * ax, t_val * az * az + c],
                ],
            )
            pts = pts @ rot.T

    pts += np.asarray(center, dtype=float)

    def _vtk_js_source(idx: int) -> str:
        return _render(
            _DISK_SOURCE_TEMPLATE,
            SOURCE=f"source{idx}",
            R_RES=str(r_res),
            C_RES=str(c_res),
            INNER=str(inner),
            OUTER=str(outer),
        )

    def _mapper_setup_disc(idx: int) -> str:
        return f"mapper{idx}.setInputData(source{idx});"

    return PolyData(
        points=pts,
        faces=np.array(faces) if faces else None,
        _vtk_js_source_fn=_vtk_js_source,
        _mapper_setup_fn=_mapper_setup_disc,
        _vtk_js_source_is_filter=False,
    )


def Circle(  # noqa: N802
    radius: float = 0.5,
    resolution: int = 100,
) -> PolyData:
    """Create a circle defined by a set of points in the XY plane.

    This mirrors the :func:`pyvista.Circle` API, producing a closed polygon
    outline of ``resolution`` points lying in the XY plane.

    Parameters
    ----------
    radius : float, optional
        Radius of the circle. Default is 0.5.
    resolution : int, optional
        Number of points on the circle. Default is 100.

    Returns
    -------
    PolyData
        A circle mesh (closed polyline in the XY plane).

    Examples
    --------
    >>> import pyvista_js as pv
    >>> circle = pv.Circle(radius=1.0)
    >>> circle.n_points
    101

    >>> circle.plot(color="black")  # doctest: +SKIP

    """
    if resolution < _CIRCLE_MIN_RESOLUTION:
        msg = f"resolution must be >= {_CIRCLE_MIN_RESOLUTION}, got {resolution}"
        raise ValueError(msg)

    theta = np.linspace(0, 2 * np.pi, resolution, endpoint=False)
    points = np.column_stack([radius * np.cos(theta), radius * np.sin(theta), np.zeros(resolution)])
    # Close the loop by appending the first point
    points = np.vstack([points, points[0]])

    center = (0.0, 0.0, 0.0)

    def _vtk_js_source(idx: int) -> str:
        return _render(
            _CIRCLE_SOURCE_TEMPLATE,
            SOURCE=f"source{idx}",
            RESOLUTION=str(resolution),
            RADIUS=str(radius),
            CENTER_X=str(center[0]),
            CENTER_Y=str(center[1]),
            CENTER_Z=str(center[2]),
        )

    def _mapper_setup_circle(idx: int) -> str:
        return f"mapper{idx}.setInputData(source{idx});"

    return PolyData(
        points=points,
        _vtk_js_source_fn=_vtk_js_source,
        _mapper_setup_fn=_mapper_setup_circle,
        _vtk_js_source_is_filter=False,
    )


def Arrow(  # noqa: N802, PLR0913
    start: tuple[float, float, float] = (0.0, 0.0, 0.0),
    direction: tuple[float, float, float] = (1.0, 0.0, 0.0),
    tip_length: float = 0.25,
    tip_radius: float = 0.1,
    tip_resolution: int = 20,
    shaft_radius: float = 0.05,
    shaft_resolution: int = 20,
    scale: float | None = None,
) -> PolyData:
    """Create an arrow mesh.

    Returns a :class:`PolyData` representing an arrow starting at ``start``
    and pointing in ``direction``, backed by vtk.js ``vtkArrowSource``.

    Parameters
    ----------
    start : tuple, optional
        Starting point of the arrow ``(x, y, z)``. Default is ``(0, 0, 0)``.
    direction : tuple, optional
        Direction vector of the arrow. Default is ``(1, 0, 0)``.
    tip_length : float, optional
        Length of the conical tip as a fraction of the total arrow length.
        Default is 0.25.
    tip_radius : float, optional
        Radius of the base of the tip. Default is 0.1.
    tip_resolution : int, optional
        Number of faces around the tip cone. Default is 20.
    shaft_radius : float, optional
        Radius of the cylindrical shaft. Default is 0.05.
    shaft_resolution : int, optional
        Number of faces around the shaft cylinder. Default is 20.
    scale : float, optional
        Scaling factor applied to the entire arrow. When ``None`` the arrow
        is not scaled.

    Returns
    -------
    PolyData
        An arrow mesh.

    Examples
    --------
    >>> import pyvista_js as pv
    >>> arrow = pv.Arrow()
    >>> isinstance(arrow, pv.PolyData)
    True

    Create an arrow with a custom start point and direction:

    >>> arrow = pv.Arrow(start=(1, 0, 0), direction=(0, 1, 0))
    >>> isinstance(arrow, pv.PolyData)
    True

    Plot the arrow:

    >>> arrow.plot()  # doctest: +SKIP

    """
    direction_arr = np.asarray(direction, dtype=float)
    norm = float(np.linalg.norm(direction_arr))
    if norm == 0.0:
        msg = "direction must be a non-zero vector"
        raise ValueError(msg)
    unit_dir = direction_arr / norm

    length = 1.0 if scale is None else float(scale)

    # Build a simple representative point set: shaft start + tip end
    start_arr = np.asarray(start, dtype=float)
    end = start_arr + unit_dir * length
    points = np.array([start_arr, end])

    def _vtk_js_source(idx: int) -> str:
        return _render(
            _ARROW_SOURCE_TEMPLATE,
            SOURCE=f"source{idx}",
            TIP_LENGTH=str(tip_length),
            TIP_RADIUS=str(tip_radius),
            TIP_RESOLUTION=str(tip_resolution),
            SHAFT_RADIUS=str(shaft_radius),
            SHAFT_RESOLUTION=str(shaft_resolution),
            DIR_X=str(float(unit_dir[0])),
            DIR_Y=str(float(unit_dir[1])),
            DIR_Z=str(float(unit_dir[2])),
        )

    def _mapper_setup_arrow(idx: int) -> str:
        return f"mapper{idx}.setInputConnection(source{idx}.getOutputPort());"

    return PolyData(
        points=points,
        _vtk_js_source_fn=_vtk_js_source,
        _mapper_setup_fn=_mapper_setup_arrow,
    )


def Cone(  # noqa: N802 PLR0913
    center: tuple[float, float, float] = (0.0, 0.0, 0.0),
    direction: tuple[float, float, float] = (1.0, 0.0, 0.0),
    height: float = 1.0,
    radius: float = 0.5,
    resolution: int = 6,
    capping: bool = True,  # noqa: FBT001 FBT002
) -> PolyData:
    """Create a cone mesh.

    Parameters
    ----------
    center : tuple, optional
        Center of the cone (x, y, z). Default is (0, 0, 0).
    direction : tuple, optional
        Direction vector of the cone axis. Default is (1, 0, 0).
    height : float, optional
        Height of the cone. Default is 1.0.
    radius : float, optional
        Base radius of the cone. Default is 0.5.
    resolution : int, optional
        Number of facets around the cone. Default is 6.
    capping : bool, optional
        Whether to cap the base of the cone. Default is True.

    Returns
    -------
    PolyData
        A cone mesh.

    Examples
    --------
    >>> import pyvista_js as pv
    >>> cone = pv.Cone(center=(0, 0, 0), direction=(1, 0, 0), height=1.0, radius=0.5, resolution=6)
    >>> cone.plot()  # doctest: +SKIP

    """
    # Generate approximate points for the cone
    norm = np.linalg.norm(direction)
    d = np.asarray(direction, dtype=float) / (norm if norm > 0 else 1.0)

    # Build two perpendicular vectors to d
    perp1 = np.cross(d, [1.0, 0.0, 0.0]) if abs(d[0]) < 0.9 else np.cross(d, [0.0, 1.0, 0.0])  # noqa: PLR2004
    perp1 /= np.linalg.norm(perp1)
    perp2 = np.cross(d, perp1)

    apex = np.asarray(center, dtype=float) + d * (height / 2.0)
    base_center = np.asarray(center, dtype=float) - d * (height / 2.0)

    theta = np.linspace(0, 2 * np.pi, resolution, endpoint=False)
    base_points = np.array(
        [base_center + radius * (np.cos(t) * perp1 + np.sin(t) * perp2) for t in theta],
    )

    points = np.vstack([apex[np.newaxis, :], base_points])
    if capping:
        points = np.vstack([points, base_center[np.newaxis, :]])

    def _vtk_js_source(idx: int) -> str:
        return _render(
            _CONE_SOURCE_TEMPLATE,
            SOURCE=f"source{idx}",
            CENTER_X=str(center[0]),
            CENTER_Y=str(center[1]),
            CENTER_Z=str(center[2]),
            DIRECTION_X=str(d[0]),
            DIRECTION_Y=str(d[1]),
            DIRECTION_Z=str(d[2]),
            HEIGHT=str(height),
            RADIUS=str(radius),
            RESOLUTION=str(resolution),
            CAPPING="true" if capping else "false",
        )

    def _mapper_setup_cone(idx: int) -> str:
        return f"mapper{idx}.setInputConnection(source{idx}.getOutputPort());"

    return PolyData(
        points=points,
        _vtk_js_source_fn=_vtk_js_source,
        _mapper_setup_fn=_mapper_setup_cone,
    )


def Line(  # noqa: N802
    pointa: tuple[float, float, float] = (0.0, 0.0, 0.0),
    pointb: tuple[float, float, float] = (1.0, 0.0, 0.0),
    resolution: int = 1,
) -> PolyData:
    """Create a line segment between two points.

    This mirrors the :func:`pyvista.Line` API, producing a polyline of
    ``resolution + 1`` evenly spaced points from ``pointa`` to ``pointb``.

    Parameters
    ----------
    pointa : tuple, optional
        Start point of the line (x, y, z). Default is (0, 0, 0).
    pointb : tuple, optional
        End point of the line (x, y, z). Default is (1, 0, 0).
    resolution : int, optional
        Number of line segments (i.e. ``resolution + 1`` points). Default is 1.

    Returns
    -------
    PolyData
        A line mesh.

    Raises
    ------
    ValueError
        If ``resolution`` is less than 1.

    Examples
    --------
    >>> import pyvista_js as pv
    >>> line = pv.Line(pointa=(0, 0, 0), pointb=(1, 0, 0), resolution=1)
    >>> line.n_points
    2

    >>> line.plot(color="black")  # doctest: +SKIP

    """
    if resolution < 1:
        msg = f"resolution must be >= 1, got {resolution}"
        raise ValueError(msg)

    points = np.linspace(pointa, pointb, resolution + 1)

    def _vtk_js_source(idx: int) -> str:
        return _render(
            _LINE_SOURCE_TEMPLATE,
            SOURCE=f"source{idx}",
            POINT_A_X=str(float(pointa[0])),
            POINT_A_Y=str(float(pointa[1])),
            POINT_A_Z=str(float(pointa[2])),
            POINT_B_X=str(float(pointb[0])),
            POINT_B_Y=str(float(pointb[1])),
            POINT_B_Z=str(float(pointb[2])),
            RESOLUTION=str(resolution),
        )

    def _mapper_setup_line(idx: int) -> str:
        return f"mapper{idx}.setInputConnection(source{idx}.getOutputPort());"

    return PolyData(
        points=points,
        _vtk_js_source_fn=_vtk_js_source,
        _mapper_setup_fn=_mapper_setup_line,
    )


def Plane(  # noqa: N802 PLR0913
    center: tuple[float, float, float] = (0.0, 0.0, 0.0),
    direction: tuple[float, float, float] = (0.0, 0.0, 1.0),
    i_size: float = 1.0,
    j_size: float = 1.0,
    i_resolution: int = 10,
    j_resolution: int = 10,
) -> PolyData:
    """Create a plane mesh.

    This mirrors the :func:`pyvista.Plane` API, producing a flat rectangular
    mesh oriented according to the given normal ``direction``.

    Parameters
    ----------
    center : tuple, optional
        Center of the plane (x, y, z). Default is (0, 0, 0).
    direction : tuple, optional
        Normal direction of the plane (x, y, z). Default is (0, 0, 1).
    i_size : float, optional
        Size in the i (first) direction. Default is 1.0.
    j_size : float, optional
        Size in the j (second) direction. Default is 1.0.
    i_resolution : int, optional
        Number of subdivisions in the i direction. Default is 10.
    j_resolution : int, optional
        Number of subdivisions in the j direction. Default is 10.

    Returns
    -------
    PolyData
        A plane mesh.

    Examples
    --------
    >>> import pyvista_js as pv
    >>> plane = pv.Plane()
    >>> plane.n_points
    121

    >>> plane.plot()  # doctest: +SKIP

    """
    n = np.array(direction, dtype=float)
    n = n / np.linalg.norm(n)

    # Find two orthogonal vectors in the plane
    if not np.allclose(np.abs(n), [0.0, 1.0, 0.0]):
        ref = np.array([0.0, 1.0, 0.0])
    else:
        ref = np.array([1.0, 0.0, 0.0])
    i_hat = np.cross(ref, n)
    i_hat = i_hat / np.linalg.norm(i_hat)
    j_hat = np.cross(n, i_hat)
    j_hat = j_hat / np.linalg.norm(j_hat)

    c = np.array(center, dtype=float)
    origin = c - (i_size / 2) * i_hat - (j_size / 2) * j_hat
    point1 = c + (i_size / 2) * i_hat - (j_size / 2) * j_hat
    point2 = c - (i_size / 2) * i_hat + (j_size / 2) * j_hat

    # Build Python points grid for PolyData
    points = []
    for j in range(j_resolution + 1):
        for i in range(i_resolution + 1):
            p = origin + (i / i_resolution) * i_size * i_hat + (j / j_resolution) * j_size * j_hat
            points.append(p)

    # Build quad faces
    faces = []
    for j in range(j_resolution):
        for i in range(i_resolution):
            idx0 = j * (i_resolution + 1) + i
            idx1 = idx0 + 1
            idx2 = idx0 + i_resolution + 2
            idx3 = idx0 + i_resolution + 1
            faces.append([idx0, idx1, idx2, idx3])

    def _vtk_js_source(idx: int) -> str:
        return _render(
            _PLANE_SOURCE_TEMPLATE,
            SOURCE=f"source{idx}",
            ORIGIN_X=str(float(origin[0])),
            ORIGIN_Y=str(float(origin[1])),
            ORIGIN_Z=str(float(origin[2])),
            POINT1_X=str(float(point1[0])),
            POINT1_Y=str(float(point1[1])),
            POINT1_Z=str(float(point1[2])),
            POINT2_X=str(float(point2[0])),
            POINT2_Y=str(float(point2[1])),
            POINT2_Z=str(float(point2[2])),
            I_RESOLUTION=str(i_resolution),
            J_RESOLUTION=str(j_resolution),
        )

    def _mapper_setup_plane(idx: int) -> str:
        return f"mapper{idx}.setInputConnection(source{idx}.getOutputPort());"

    return PolyData(
        points=np.array(points),
        faces=np.array(faces),
        _vtk_js_source_fn=_vtk_js_source,
        _mapper_setup_fn=_mapper_setup_plane,
    )


class _GaussianSplatMesh(PolyData):
    """Mesh for Gaussian splat rendering.

    This class handles Gaussian splat data (3D Gaussian distributions) typically
    used in Neural Radiance Field (NeRF) and 3D Gaussian Splatting workflows.
    The splat data is parsed on the JavaScript side and rendered using WebGL.

    Parameters
    ----------
    points : np.ndarray
        Gaussian center positions (N, 3) extracted for bounding sphere computation.
    splat_base64 : str
        Base64-encoded content of the Gaussian splat file passed to the renderer.

    """

    def __init__(self, points: np.ndarray, splat_base64: str) -> None:
        """Initialize with points and base64-encoded splat file content."""
        super().__init__(points)
        self._splat_base64 = splat_base64

    def generate_vtk_js_source(self, idx: int) -> str:
        """Generate JavaScript code for Gaussian splat rendering.

        Returns
        -------
        str
            JavaScript code that parses and prepares the Gaussian splat data.

        """
        import json
        escaped = json.dumps(self._splat_base64)
        return _render(
            _GAUSSIAN_SPLAT_SOURCE_TEMPLATE,
            SOURCE=f"source{idx}",
            SPLAT_READER=f"splatReader{idx}",
            SPLAT_BASE64=escaped,
            INDEX=str(idx),
            SPLAT_DATA=f"splatData{idx}",
        )

    def get_mapper_setup(self, idx: int) -> str:
        """Get the mapper setup code for Gaussian splats.

        Returns
        -------
        str
            JavaScript code to connect the source to the mapper.

        """
        return f"mapper{idx}.setInputData(source{idx});"
