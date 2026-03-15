"""Mesh classes for pyvista-js.

Provides geometric primitives and mesh handling compatible with PyVista API.
"""

from __future__ import annotations

import warnings
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from collections.abc import Callable

    from numpy.typing import ArrayLike

# Load JavaScript templates relative to this file
_JS_DIR = Path(__file__).parent / "js"
_MESH_SOURCE_TEMPLATE = (_JS_DIR / "mesh_source.js").read_text()
_SPHERE_SOURCE_TEMPLATE = (_JS_DIR / "sphere_source.js").read_text()
_CUBE_SOURCE_TEMPLATE = (_JS_DIR / "cube_source.js").read_text()
_CYLINDER_SOURCE_TEMPLATE = (_JS_DIR / "cylinder_source.js").read_text()
_SHRINK_FILTER_TEMPLATE = (_JS_DIR / "shrink_filter.js").read_text()
_CIRCLE_SOURCE_TEMPLATE = (_JS_DIR / "circle_source.js").read_text()
_LINE_SOURCE_TEMPLATE = (_JS_DIR / "line_source.js").read_text()
_CIRCLE_MIN_RESOLUTION = 3


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
        _vtk_js_source_fn: Callable[[int], str] | None = None,
        _mapper_setup_fn: Callable[[int], str] | None = None,
    ) -> None:
        """Initialize a PolyData mesh."""
        self.points = np.asarray(points)
        self.faces = np.asarray(faces) if faces is not None else None
        self.t_coords = np.asarray(t_coords) if t_coords is not None else None
        self._vtk_js_source_fn = _vtk_js_source_fn
        self._mapper_setup_fn = _mapper_setup_fn

    @property
    def n_points(self) -> int:
        """Return the number of points."""
        return len(self.points)

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
        >>> sphere.plot(color='red')

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
            shrink_code = _SHRINK_FILTER_TEMPLATE.replace("{{INDEX}}", str(idx)).replace(
                "{{SHRINK_FACTOR}}",
                str(shrink_factor),
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
            source_code = _MESH_SOURCE_TEMPLATE.replace("{{INDEX}}", str(idx)).replace(
                "{{POINTS_DATA}}",
                points_str,
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


class Mesh(PolyData):
    """Deprecated base mesh class.

    .. deprecated:: 0.2
        :class:`Mesh` is deprecated and will be removed in version 0.4.
        Use :class:`PolyData` instead.

    Parameters
    ----------
    points : array-like
        Vertex coordinates as an (n, 3) array.
    faces : array-like, optional
        Cell connectivity information.

    """

    def __init__(self, points: ArrayLike, faces: ArrayLike | None = None) -> None:
        """Initialize a Mesh (deprecated)."""
        warnings.warn(
            "Mesh is deprecated and will be removed in version 0.4. Use PolyData instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init__(points, faces)


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
    902

    """
    theta = np.linspace(0, 2 * np.pi, theta_resolution)
    phi = np.linspace(0, np.pi, phi_resolution)

    points = []
    for p in phi:
        for t in theta:
            x = radius * np.sin(p) * np.cos(t) + center[0]
            y = radius * np.sin(p) * np.sin(t) + center[1]
            z = radius * np.cos(p) + center[2]
            points.append([x, y, z])

    def _vtk_js_source(idx: int) -> str:
        return (
            _SPHERE_SOURCE_TEMPLATE.replace("{{INDEX}}", str(idx))
            .replace("{{CENTER_X}}", str(center[0]))
            .replace("{{CENTER_Y}}", str(center[1]))
            .replace("{{CENTER_Z}}", str(center[2]))
            .replace("{{RADIUS}}", str(radius))
            .replace("{{THETA_RESOLUTION}}", str(theta_resolution))
            .replace("{{PHI_RESOLUTION}}", str(phi_resolution))
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
    8

    """
    x, y, z = center
    dx, dy, dz = x_length / 2, y_length / 2, z_length / 2

    points = np.array(
        [
            [x - dx, y - dy, z - dz],
            [x + dx, y - dy, z - dz],
            [x + dx, y + dy, z - dz],
            [x - dx, y + dy, z - dz],
            [x - dx, y - dy, z + dz],
            [x + dx, y - dy, z + dz],
            [x + dx, y + dy, z + dz],
            [x - dx, y + dy, z + dz],
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
        return (
            _CUBE_SOURCE_TEMPLATE.replace("{{INDEX}}", str(idx))
            .replace("{{CENTER_X}}", str(center[0]))
            .replace("{{CENTER_Y}}", str(center[1]))
            .replace("{{CENTER_Z}}", str(center[2]))
            .replace("{{X_LENGTH}}", str(x_length))
            .replace("{{Y_LENGTH}}", str(y_length))
            .replace("{{Z_LENGTH}}", str(z_length))
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
    theta = np.linspace(0, 2 * np.pi, resolution)

    bottom_points = []
    for t in theta:
        bx = radius * np.cos(t) + center[0]
        by = radius * np.sin(t) + center[1]
        bz = center[2] - height / 2
        bottom_points.append([bx, by, bz])

    top_points = []
    for t in theta:
        tx = radius * np.cos(t) + center[0]
        ty = radius * np.sin(t) + center[1]
        tz = center[2] + height / 2
        top_points.append([tx, ty, tz])

    points = np.vstack([bottom_points, top_points])

    def _vtk_js_source(idx: int) -> str:
        return (
            _CYLINDER_SOURCE_TEMPLATE.replace("{{INDEX}}", str(idx))
            .replace("{{CENTER_X}}", str(center[0]))
            .replace("{{CENTER_Y}}", str(center[1]))
            .replace("{{CENTER_Z}}", str(center[2]))
            .replace("{{RADIUS}}", str(radius))
            .replace("{{HEIGHT}}", str(height))
            .replace("{{RESOLUTION}}", str(resolution))
        )

    def _mapper_setup_cylinder(idx: int) -> str:
        return f"mapper{idx}.setInputConnection(source{idx}.getOutputPort());"

    return PolyData(
        points=points,
        _vtk_js_source_fn=_vtk_js_source,
        _mapper_setup_fn=_mapper_setup_cylinder,
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
        return (
            _CIRCLE_SOURCE_TEMPLATE.replace("{{INDEX}}", str(idx))
            .replace("{{CENTER_X}}", str(center[0]))
            .replace("{{CENTER_Y}}", str(center[1]))
            .replace("{{CENTER_Z}}", str(center[2]))
            .replace("{{RADIUS}}", str(radius))
            .replace("{{RESOLUTION}}", str(resolution))
        )

    def _mapper_setup_circle(idx: int) -> str:
        return f"mapper{idx}.setInputData(source{idx});"

    return PolyData(
        points=points,
        _vtk_js_source_fn=_vtk_js_source,
        _mapper_setup_fn=_mapper_setup_circle,
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

    """
    if resolution < 1:
        msg = f"resolution must be >= 1, got {resolution}"
        raise ValueError(msg)

    points = np.linspace(pointa, pointb, resolution + 1)

    def _vtk_js_source(idx: int) -> str:
        return (
            _LINE_SOURCE_TEMPLATE.replace("{{INDEX}}", str(idx))
            .replace("{{POINT_A_X}}", str(float(pointa[0])))
            .replace("{{POINT_A_Y}}", str(float(pointa[1])))
            .replace("{{POINT_A_Z}}", str(float(pointa[2])))
            .replace("{{POINT_B_X}}", str(float(pointb[0])))
            .replace("{{POINT_B_Y}}", str(float(pointb[1])))
            .replace("{{POINT_B_Z}}", str(float(pointb[2])))
            .replace("{{RESOLUTION}}", str(resolution))
        )

    def _mapper_setup_line(idx: int) -> str:
        return f"mapper{idx}.setInputConnection(source{idx}.getOutputPort());"

    return PolyData(
        points=points,
        _vtk_js_source_fn=_vtk_js_source,
        _mapper_setup_fn=_mapper_setup_line,
    )
