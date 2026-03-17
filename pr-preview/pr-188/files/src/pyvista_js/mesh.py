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
    >>> plotter.add_mesh(mesh, scalars='elevation', cmap='viridis')
    >>> plotter.show()

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
_JS_DIR = Path(__file__).parent / "js"
_MESH_SOURCE_TEMPLATE = (_JS_DIR / "mesh_source.js").read_text()
_SPHERE_SOURCE_TEMPLATE = (_JS_DIR / "sphere_source.js").read_text()
_CUBE_SOURCE_TEMPLATE = (_JS_DIR / "cube_source.js").read_text()
_CYLINDER_SOURCE_TEMPLATE = (_JS_DIR / "cylinder_source.js").read_text()
_SHRINK_FILTER_TEMPLATE = (_JS_DIR / "shrink_filter.js").read_text()
_TUBE_FILTER_TEMPLATE = (_JS_DIR / "tube_filter.js").read_text()
_CIRCLE_SOURCE_TEMPLATE = (_JS_DIR / "circle_source.js").read_text()
_DISK_SOURCE_TEMPLATE = (_JS_DIR / "disk_source.js").read_text()
_ARROW_SOURCE_TEMPLATE = (_JS_DIR / "arrow_source.js").read_text()
_CONE_SOURCE_TEMPLATE = (_JS_DIR / "cone_source.js").read_text()
_LINE_SOURCE_TEMPLATE = (_JS_DIR / "line_source.js").read_text()
_PLANE_SOURCE_TEMPLATE = (_JS_DIR / "plane_source.js").read_text()
_CIRCLE_MIN_RESOLUTION = 3
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
        _vtk_js_source_fn: Callable[[int], str] | None = None,
        _mapper_setup_fn: Callable[[int], str] | None = None,
    ) -> None:
        """Initialize a PolyData mesh."""
        self.points = np.asarray(points)
        self.faces = np.asarray(faces) if faces is not None else None
        self.t_coords = np.asarray(t_coords) if t_coords is not None else None
        self._vtk_js_source_fn = _vtk_js_source_fn
        self._mapper_setup_fn = _mapper_setup_fn
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
        >>> plotter.add_mesh(mesh, scalars='elevation', cmap='viridis')
        >>> plotter.show()

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
        >>> plotter.add_mesh(mesh, scalars='elevation', cmap='viridis')
        >>> plotter.show()

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
            tube_code = (
                _TUBE_FILTER_TEMPLATE.replace("{{INDEX}}", str(idx))
                .replace("{{RADIUS}}", str(radius))
                .replace("{{N_SIDES}}", str(n_sides))
                .replace("{{CAPPING}}", "true" if capping else "false")
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

        # Inject point data scalar arrays
        if len(self._point_data) > 0:
            # For primitives (source-based), extract output polydata first.
            # For generic meshes, polydata{idx} already exists.
            if self._vtk_js_source_fn is not None:
                source_code += (
                    f"\n// Extract output polydata from source for scalar injection\n"
                    f"source{idx}.update();\n"
                    f"const polydata{idx} = source{idx}.getOutputData();\n"
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
    # Generate points in XY plane: (r_res+1) rings * c_res points
    radii = np.linspace(inner, outer, r_res + 1)
    theta = np.linspace(0, 2 * np.pi, c_res, endpoint=False)
    pts = np.array(
        [[r * np.cos(t), r * np.sin(t), 0.0] for r in radii for t in theta],
    )

    # Build triangular faces: two triangles per quad between adjacent rings
    faces = []
    for ring in range(r_res):
        for ci in range(c_res):
            ci1 = (ci + 1) % c_res
            i00 = ring * c_res + ci
            i01 = ring * c_res + ci1
            i10 = (ring + 1) * c_res + ci
            i11 = (ring + 1) * c_res + ci1
            faces.append([i00, i01, i11])
            faces.append([i00, i11, i10])

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
        return (
            _DISK_SOURCE_TEMPLATE.replace("{{INDEX}}", str(idx))
            .replace("{{INNER}}", str(inner))
            .replace("{{OUTER}}", str(outer))
            .replace("{{R_RES}}", str(r_res))
            .replace("{{C_RES}}", str(c_res))
        )

    def _mapper_setup_disc(idx: int) -> str:
        return f"mapper{idx}.setInputData(source{idx});"

    return PolyData(
        points=pts,
        faces=np.array(faces) if faces else None,
        _vtk_js_source_fn=_vtk_js_source,
        _mapper_setup_fn=_mapper_setup_disc,
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
        return (
            _ARROW_SOURCE_TEMPLATE.replace("{{INDEX}}", str(idx))
            .replace("{{TIP_LENGTH}}", str(tip_length))
            .replace("{{TIP_RADIUS}}", str(tip_radius))
            .replace("{{TIP_RESOLUTION}}", str(tip_resolution))
            .replace("{{SHAFT_RADIUS}}", str(shaft_radius))
            .replace("{{SHAFT_RESOLUTION}}", str(shaft_resolution))
            .replace("{{DIR_X}}", str(float(unit_dir[0])))
            .replace("{{DIR_Y}}", str(float(unit_dir[1])))
            .replace("{{DIR_Z}}", str(float(unit_dir[2])))
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
    >>> cone.plot()

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
        capping_str = "true" if capping else "false"
        return (
            _CONE_SOURCE_TEMPLATE.replace("{{INDEX}}", str(idx))
            .replace("{{CENTER_X}}", str(center[0]))
            .replace("{{CENTER_Y}}", str(center[1]))
            .replace("{{CENTER_Z}}", str(center[2]))
            .replace("{{DIRECTION_X}}", str(d[0]))
            .replace("{{DIRECTION_Y}}", str(d[1]))
            .replace("{{DIRECTION_Z}}", str(d[2]))
            .replace("{{HEIGHT}}", str(height))
            .replace("{{RADIUS}}", str(radius))
            .replace("{{RESOLUTION}}", str(resolution))
            .replace("{{CAPPING}}", capping_str)
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
        return (
            _PLANE_SOURCE_TEMPLATE.replace("{{INDEX}}", str(idx))
            .replace("{{ORIGIN_X}}", str(float(origin[0])))
            .replace("{{ORIGIN_Y}}", str(float(origin[1])))
            .replace("{{ORIGIN_Z}}", str(float(origin[2])))
            .replace("{{POINT1_X}}", str(float(point1[0])))
            .replace("{{POINT1_Y}}", str(float(point1[1])))
            .replace("{{POINT1_Z}}", str(float(point1[2])))
            .replace("{{POINT2_X}}", str(float(point2[0])))
            .replace("{{POINT2_Y}}", str(float(point2[1])))
            .replace("{{POINT2_Z}}", str(float(point2[2])))
            .replace("{{I_RESOLUTION}}", str(i_resolution))
            .replace("{{J_RESOLUTION}}", str(j_resolution))
        )

    def _mapper_setup_plane(idx: int) -> str:
        return f"mapper{idx}.setInputConnection(source{idx}.getOutputPort());"

    return PolyData(
        points=np.array(points),
        faces=np.array(faces),
        _vtk_js_source_fn=_vtk_js_source,
        _mapper_setup_fn=_mapper_setup_plane,
    )
