"""Mesh classes for pyvista-js.

Provides geometric primitives and mesh handling compatible with PyVista API.
"""

from typing import Tuple

import numpy as np


class Mesh:
    """Base mesh class.

    Parameters
    ----------
    points : array-like
        Vertex coordinates as an (n, 3) array.
    faces : array-like, optional
        Cell connectivity information.
    """

    def __init__(self, points, faces=None):
        """Initialize a mesh."""
        self.points = np.asarray(points)
        self.faces = np.asarray(faces) if faces is not None else None

    @property
    def n_points(self):
        """Return the number of points."""
        return len(self.points)

    @property
    def n_faces(self):
        """Return the number of faces."""
        return len(self.faces) if self.faces is not None else 0


def Sphere(
    radius: float = 1.0,
    center: Tuple[float, float, float] = (0.0, 0.0, 0.0),
    theta_resolution: int = 30,
    phi_resolution: int = 30,
) -> Mesh:
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
    Mesh
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

    mesh = Mesh(points=np.array(points))
    mesh._mesh_type = 'Sphere'
    mesh._params = {
        'radius': radius,
        'center': center,
        'theta_resolution': theta_resolution,
        'phi_resolution': phi_resolution
    }
    return mesh


def Cube(
    center: Tuple[float, float, float] = (0.0, 0.0, 0.0),
    x_length: float = 1.0,
    y_length: float = 1.0,
    z_length: float = 1.0,
) -> Mesh:
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
    Mesh
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

    points = np.array([
        [x - dx, y - dy, z - dz],
        [x + dx, y - dy, z - dz],
        [x + dx, y + dy, z - dz],
        [x - dx, y + dy, z - dz],
        [x - dx, y - dy, z + dz],
        [x + dx, y - dy, z + dz],
        [x + dx, y + dy, z + dz],
        [x - dx, y + dy, z + dz],
    ])

    # Define faces (each face has 4 vertices)
    faces = np.array([
        [0, 1, 2, 3],  # Bottom
        [4, 5, 6, 7],  # Top
        [0, 1, 5, 4],  # Front
        [2, 3, 7, 6],  # Back
        [0, 3, 7, 4],  # Left
        [1, 2, 6, 5],  # Right
    ])

    mesh = Mesh(points=points, faces=faces)
    mesh._mesh_type = 'Cube'
    mesh._params = {
        'center': center,
        'x_length': x_length,
        'y_length': y_length,
        'z_length': z_length
    }
    return mesh


def Cylinder(
    center: Tuple[float, float, float] = (0.0, 0.0, 0.0),
    direction: Tuple[float, float, float] = (1.0, 0.0, 0.0),
    radius: float = 0.5,
    height: float = 1.0,
    resolution: int = 100,
) -> Mesh:
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
    Mesh
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

    mesh = Mesh(points=points)
    mesh._mesh_type = 'Cylinder'
    mesh._params = {
        'center': center,
        'direction': direction,
        'radius': radius,
        'height': height,
        'resolution': resolution
    }
    return mesh
