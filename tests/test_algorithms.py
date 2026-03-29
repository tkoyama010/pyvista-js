""" "Tests for Python algorithms module."""

import numpy as np

from pyvista_js.algorithms import (
    clip_mesh,
    compute_contour,
    create_cone,
    create_cube,
    create_cylinder,
    create_sphere,
    shrink_mesh,
)


def test_create_sphere():
    """Test sphere creation."""
    points, faces = create_sphere(radius=1.0, theta_resolution=8, phi_resolution=8)

    # Check that we get points and faces
    assert len(points) > 0
    assert len(faces) > 0

    # Check that points have 3 coordinates
    for point in points:
        assert len(point) == 3

    # Check that faces have correct format (3 vertices per triangle)
    i = 0
    while i < len(faces):
        n_verts = faces[i]
        assert n_verts == 3  # Triangles
        i += n_verts + 1


def test_create_cone():
    """Test cone creation."""
    points, faces = create_cone(radius=1.0, height=2.0, resolution=8)

    # Check that we get points and faces
    assert len(points) > 0
    assert len(faces) > 0

    # Check structure
    for point in points:
        assert len(point) == 3


def test_create_cube():
    """Test cube creation."""
    points, faces = create_cube(size=2.0)

    # Cube should have 8 vertices
    assert len(points) == 8

    # Each point should have 3 coordinates
    for point in points:
        assert len(point) == 3

    # Check faces format
    i = 0
    while i < len(faces):
        n_verts = faces[i]
        assert n_verts == 3  # Triangles
        i += n_verts + 1


def test_create_cylinder():
    """Test cylinder creation."""
    points, faces = create_cylinder(radius=1.0, height=2.0, resolution=8)

    # Check that we get points and faces
    assert len(points) > 0
    assert len(faces) > 0

    # Check structure
    for point in points:
        assert len(point) == 3


def test_shrink_mesh():
    """Test mesh shrinking."""
    # Create a simple cube
    points = [
        [-1, -1, -1],
        [1, -1, -1],
        [1, 1, -1],
        [-1, 1, -1],
        [-1, -1, 1],
        [1, -1, 1],
        [1, 1, 1],
        [-1, 1, 1],
    ]

    shrunk_points = shrink_mesh(points, shrink_factor=0.5)

    # Should have same number of points
    assert len(shrunk_points) == len(points)

    # Points should move towards centroid
    original_centroid = np.mean(points, axis=0)
    shrunk_centroid = np.mean(shrunk_points, axis=0)

    # Centroid should remain the same
    np.testing.assert_allclose(original_centroid, shrunk_centroid, rtol=1e-10)


def test_clip_mesh():
    """Test mesh clipping."""
    # Create a simple cube
    points = [
        [-1, -1, -1],
        [1, -1, -1],
        [1, 1, -1],
        [-1, 1, -1],
        [-1, -1, 1],
        [1, -1, 1],
        [1, 1, 1],
        [-1, 1, 1],
    ]
    faces = [
        3,
        0,
        1,
        2,
        3,
        0,
        2,
        3,  # Bottom face
        3,
        4,
        7,
        6,
        3,
        4,
        6,
        5,  # Top face
    ]

    # Clip with plane at z=0
    new_points, new_faces = clip_mesh(points, faces, [0, 0, 0], [0, 0, 1])

    # Should have fewer or equal points after clipping
    assert len(new_points) <= len(points)
    assert len(new_faces) <= len(faces)


def test_compute_contour():
    """Test contour computation."""
    # Create points with values
    points = [
        [0, 0, 0],
        [1, 0, 0],
        [2, 0, 0],
        [0, 1, 0],
        [1, 1, 0],
        [2, 1, 0],
    ]
    values = [0.1, 0.5, 0.8, 0.2, 0.6, 0.9]

    # Extract contour at isovalue 0.5
    contour_points = compute_contour(points, values, 0.5)

    # Should get points with values >= 0.5
    assert len(contour_points) > 0
