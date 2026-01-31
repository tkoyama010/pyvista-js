"""Test mesh creation and properties."""

import pytest
import numpy as np
from pyvista_js import Mesh, Sphere, Cube, Cylinder


def test_mesh_creation():
    """Test basic mesh creation."""
    points = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]])
    mesh = Mesh(points)
    
    assert mesh.n_points == 3
    assert np.array_equal(mesh.points, points)


def test_sphere_creation():
    """Test sphere primitive creation."""
    sphere = Sphere(radius=1.0)
    
    assert sphere.n_points > 0
    assert isinstance(sphere.points, np.ndarray)
    assert sphere.points.shape[1] == 3  # 3D coordinates


def test_sphere_parameters():
    """Test sphere with custom parameters."""
    sphere = Sphere(radius=2.0, center=(1, 2, 3))
    
    # Check that points are roughly centered at (1, 2, 3)
    center = np.mean(sphere.points, axis=0)
    assert np.allclose(center, [1, 2, 3], atol=0.1)


def test_cube_creation():
    """Test cube primitive creation."""
    cube = Cube()
    
    assert cube.n_points == 8
    assert cube.n_faces == 6


def test_cube_size():
    """Test cube with custom size."""
    cube = Cube(x_length=2.0, y_length=2.0, z_length=2.0)
    
    # Check bounding box
    mins = np.min(cube.points, axis=0)
    maxs = np.max(cube.points, axis=0)
    
    assert np.allclose(maxs - mins, [2.0, 2.0, 2.0])


def test_cylinder_creation():
    """Test cylinder primitive creation."""
    cylinder = Cylinder(radius=1.0, height=2.0)
    
    assert cylinder.n_points > 0
    assert isinstance(cylinder.points, np.ndarray)
