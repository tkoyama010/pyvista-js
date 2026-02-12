"""Mesh classes for pyvista-js.

Provides geometric primitives and mesh handling compatible with PyVista API.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from numpy.typing import ArrayLike

# Load JavaScript templates
_JS_DIR = Path(__file__).parent / "js"
_MESH_SOURCE_TEMPLATE = (_JS_DIR / "mesh_source.js").read_text()
_SPHERE_SOURCE_TEMPLATE = (_JS_DIR / "sphere_source.js").read_text()
_CUBE_SOURCE_TEMPLATE = (_JS_DIR / "cube_source.js").read_text()
_CYLINDER_SOURCE_TEMPLATE = (_JS_DIR / "cylinder_source.js").read_text()


class Mesh:
    """Base mesh class.

    Parameters
    ----------
    points : array-like
        Vertex coordinates as an (n, 3) array.
    faces : array-like, optional
        Cell connectivity information.

    """

    def __init__(self, points: ArrayLike, faces: ArrayLike | None = None) -> None:
        """Initialize a mesh."""
        self.points = np.asarray(points)
        self.faces = np.asarray(faces) if faces is not None else None

    @property
    def n_points(self) -> int:
        """Return the number of points."""
        return len(self.points)

    @property
    def n_faces(self) -> int:
        """Return the number of faces."""
        return len(self.faces) if self.faces is not None else 0

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
        # Default implementation for generic meshes using polydata
        points_flat = self.points.flatten().tolist()
        points_str = ",".join(map(str, points_flat))
        return _MESH_SOURCE_TEMPLATE.replace("{{INDEX}}", str(idx)).replace(
            "{{POINTS_DATA}}",
            points_str,
        )

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
        # Default implementation for generic meshes
        return f"mapper{idx}.setInputData(source{idx});"


class SphereMesh(Mesh):
    """Sphere mesh with vtk.js source generation."""

    def __init__(
        self,
        points: ArrayLike,
        radius: float,
        center: tuple[float, float, float],
        theta_resolution: int,
        phi_resolution: int,
    ) -> None:
        """Initialize a sphere mesh."""
        super().__init__(points)
        self.radius = radius
        self.center = center
        self.theta_resolution = theta_resolution
        self.phi_resolution = phi_resolution

    def generate_vtk_js_source(self, idx: int) -> str:
        """Generate vtk.js sphere source code."""
        return (
            _SPHERE_SOURCE_TEMPLATE.replace("{{INDEX}}", str(idx))
            .replace("{{CENTER_X}}", str(self.center[0]))
            .replace("{{CENTER_Y}}", str(self.center[1]))
            .replace("{{CENTER_Z}}", str(self.center[2]))
            .replace("{{RADIUS}}", str(self.radius))
            .replace("{{THETA_RESOLUTION}}", str(self.theta_resolution))
            .replace("{{PHI_RESOLUTION}}", str(self.phi_resolution))
        )

    def get_mapper_setup(self, idx: int) -> str:
        """Get the mapper setup code for sphere mesh."""
        return f"mapper{idx}.setInputConnection(source{idx}.getOutputPort());"


class CubeMesh(Mesh):
    """Cube mesh with vtk.js source generation."""

    def __init__(  # noqa: PLR0913
        self,
        points: ArrayLike,
        faces: ArrayLike,
        center: tuple[float, float, float],
        x_length: float,
        y_length: float,
        z_length: float,
    ) -> None:
        """Initialize a cube mesh."""
        super().__init__(points, faces)
        self.center = center
        self.x_length = x_length
        self.y_length = y_length
        self.z_length = z_length

    def generate_vtk_js_source(self, idx: int) -> str:
        """Generate vtk.js cube source code."""
        return (
            _CUBE_SOURCE_TEMPLATE.replace("{{INDEX}}", str(idx))
            .replace("{{CENTER_X}}", str(self.center[0]))
            .replace("{{CENTER_Y}}", str(self.center[1]))
            .replace("{{CENTER_Z}}", str(self.center[2]))
            .replace("{{X_LENGTH}}", str(self.x_length))
            .replace("{{Y_LENGTH}}", str(self.y_length))
            .replace("{{Z_LENGTH}}", str(self.z_length))
        )

    def get_mapper_setup(self, idx: int) -> str:
        """Get the mapper setup code for cube mesh."""
        return f"mapper{idx}.setInputConnection(source{idx}.getOutputPort());"


class CylinderMesh(Mesh):
    """Cylinder mesh with vtk.js source generation."""

    def __init__(  # noqa: PLR0913
        self,
        points: ArrayLike,
        center: tuple[float, float, float],
        direction: tuple[float, float, float],
        radius: float,
        height: float,
        resolution: int,
    ) -> None:
        """Initialize a cylinder mesh."""
        super().__init__(points)
        self.center = center
        self.direction = direction
        self.radius = radius
        self.height = height
        self.resolution = resolution

    def generate_vtk_js_source(self, idx: int) -> str:
        """Generate vtk.js cylinder source code."""
        return (
            _CYLINDER_SOURCE_TEMPLATE.replace("{{INDEX}}", str(idx))
            .replace("{{CENTER_X}}", str(self.center[0]))
            .replace("{{CENTER_Y}}", str(self.center[1]))
            .replace("{{CENTER_Z}}", str(self.center[2]))
            .replace("{{RADIUS}}", str(self.radius))
            .replace("{{HEIGHT}}", str(self.height))
            .replace("{{RESOLUTION}}", str(self.resolution))
        )

    def get_mapper_setup(self, idx: int) -> str:
        """Get the mapper setup code for cylinder mesh."""
        return f"mapper{idx}.setInputConnection(source{idx}.getOutputPort());"


def Sphere(  # noqa: N802
    radius: float = 1.0,
    center: tuple[float, float, float] = (0.0, 0.0, 0.0),
    theta_resolution: int = 30,
    phi_resolution: int = 30,
) -> SphereMesh:
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
    SphereMesh
        A sphere mesh.

    Examples
    --------
    >>> import pyvista_js as pv
    >>> sphere = pv.Sphere(radius=1.0)
    >>> sphere.n_points
    902

    """
    # Generate sphere points using spherical coordinates
    theta = np.linspace(0, 2 * np.pi, theta_resolution)
    phi = np.linspace(0, np.pi, phi_resolution)

    points = []
    for p in phi:
        for t in theta:
            x = radius * np.sin(p) * np.cos(t) + center[0]
            y = radius * np.sin(p) * np.sin(t) + center[1]
            z = radius * np.cos(p) + center[2]
            points.append([x, y, z])

    mesh = SphereMesh(
        points=np.array(points),
        radius=radius,
        center=center,
        theta_resolution=theta_resolution,
        phi_resolution=phi_resolution,
    )
    # Store mesh metadata for backward compatibility
    mesh.__dict__["_mesh_type"] = "Sphere"
    mesh.__dict__["_params"] = {
        "radius": radius,
        "center": center,
        "theta_resolution": theta_resolution,
        "phi_resolution": phi_resolution,
    }
    return mesh


def Cube(  # noqa: N802
    center: tuple[float, float, float] = (0.0, 0.0, 0.0),
    x_length: float = 1.0,
    y_length: float = 1.0,
    z_length: float = 1.0,
) -> CubeMesh:
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
    CubeMesh
        A cube mesh.

    Examples
    --------
    >>> import pyvista_js as pv
    >>> cube = pv.Cube()
    >>> cube.n_points
    8

    """
    # Generate cube vertices
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

    # Define faces (each face has 4 vertices)
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

    mesh = CubeMesh(
        points=points,
        faces=faces,
        center=center,
        x_length=x_length,
        y_length=y_length,
        z_length=z_length,
    )
    # Store mesh metadata for backward compatibility
    mesh.__dict__["_mesh_type"] = "Cube"
    mesh.__dict__["_params"] = {
        "center": center,
        "x_length": x_length,
        "y_length": y_length,
        "z_length": z_length,
    }
    return mesh


def Cylinder(  # noqa: N802
    center: tuple[float, float, float] = (0.0, 0.0, 0.0),
    direction: tuple[float, float, float] = (1.0, 0.0, 0.0),
    radius: float = 0.5,
    height: float = 1.0,
    resolution: int = 100,
) -> CylinderMesh:
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
    CylinderMesh
        A cylinder mesh.

    Examples
    --------
    >>> import pyvista_js as pv
    >>> cylinder = pv.Cylinder(radius=1.0, height=2.0)

    """
    # Generate cylinder points
    theta = np.linspace(0, 2 * np.pi, resolution)

    # Bottom circle
    bottom_points = []
    for t in theta:
        x = radius * np.cos(t) + center[0]
        y = radius * np.sin(t) + center[1]
        z = center[2] - height / 2
        bottom_points.append([x, y, z])

    # Top circle
    top_points = []
    for t in theta:
        x = radius * np.cos(t) + center[0]
        y = radius * np.sin(t) + center[1]
        z = center[2] + height / 2
        top_points.append([x, y, z])

    points = np.vstack([bottom_points, top_points])

    mesh = CylinderMesh(
        points=points,
        center=center,
        direction=direction,
        radius=radius,
        height=height,
        resolution=resolution,
    )
    # Store mesh metadata for backward compatibility
    mesh.__dict__["_mesh_type"] = "Cylinder"
    mesh.__dict__["_params"] = {
        "center": center,
        "direction": direction,
        "radius": radius,
        "height": height,
        "resolution": resolution,
    }
    return mesh
