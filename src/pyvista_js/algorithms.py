"""Geometric algorithms migrated from TypeScript to Python for performance."""

import numpy as np


def create_sphere(
    radius: float = 1.0,
    theta_resolution: int = 32,
    phi_resolution: int = 32,
) -> tuple[np.ndarray, np.ndarray]:
    """Create a sphere mesh using NumPy vectorization for improved performance."""
    theta = np.linspace(0, 2 * np.pi, theta_resolution)
    phi = np.linspace(0, np.pi, phi_resolution)
    theta_grid, phi_grid = np.meshgrid(theta, phi)

    x = radius * np.sin(phi_grid) * np.cos(theta_grid)
    y = radius * np.sin(phi_grid) * np.sin(theta_grid)
    z = radius * np.cos(phi_grid)

    points = np.column_stack([x.ravel(), y.ravel(), z.ravel()])

    # Create face connectivity
    faces = []
    for i in range(phi_resolution - 1):
        for j in range(theta_resolution - 1):
            p1 = i * theta_resolution + j
            p2 = i * theta_resolution + (j + 1)
            p3 = (i + 1) * theta_resolution + (j + 1)
            p4 = (i + 1) * theta_resolution + j

            faces.extend([[3, p1, p2, p4], [3, p2, p3, p4]])

    # Flatten faces list properly
    flattened_faces = []
    for face in faces:
        flattened_faces.extend(face)

    return points.tolist(), flattened_faces


def create_cone(
    radius: float = 1.0,
    height: float = 2.0,
    resolution: int = 32,
) -> tuple[np.ndarray, np.ndarray]:
    """Create a cone mesh with optimized NumPy operations."""
    theta = np.linspace(0, 2 * np.pi, resolution, endpoint=False)

    # Base circle points
    base_points = np.column_stack(
        [radius * np.cos(theta), radius * np.sin(theta), np.zeros(resolution)],
    )

    # Apex point
    apex = np.array([[0.0, 0.0, height]])
    points = np.vstack([base_points, apex])

    # Create triangular faces
    faces = []
    for i in range(resolution):
        next_i = (i + 1) % resolution
        faces.append([3, i, next_i, resolution])  # Side triangles

    # Flatten faces list properly
    flattened_faces = []
    for face in faces:
        flattened_faces.extend(face)

    return points.tolist(), flattened_faces


def create_cube(size: float = 2.0) -> tuple[np.ndarray, np.ndarray]:
    """Create a cube mesh with NumPy optimization."""
    s = size / 2
    points = np.array(
        [
            [-s, -s, -s],
            [s, -s, -s],
            [s, s, -s],
            [-s, s, -s],  # Bottom face
            [-s, -s, s],
            [s, -s, s],
            [s, s, s],
            [-s, s, s],  # Top face
        ],
    )

    # Define faces (triangles)
    faces = [
        [3, 0, 1, 2],
        [3, 0, 2, 3],  # Bottom
        [3, 4, 7, 6],
        [3, 4, 6, 5],  # Top
        [3, 0, 4, 5],
        [3, 0, 5, 1],  # Front
        [3, 2, 6, 7],
        [3, 2, 7, 3],  # Back
        [3, 1, 5, 6],
        [3, 1, 6, 2],  # Right
        [3, 4, 0, 3],
        [3, 4, 3, 7],  # Left
    ]

    # Flatten faces list properly
    flattened_faces = []
    for face in faces:
        flattened_faces.extend(face)

    return points.tolist(), flattened_faces


def create_cylinder(
    radius: float = 1.0,
    height: float = 2.0,
    resolution: int = 32,
) -> tuple[np.ndarray, np.ndarray]:
    """Create a cylinder mesh with NumPy vectorization."""
    theta = np.linspace(0, 2 * np.pi, resolution, endpoint=False)

    # Bottom and top circles
    bottom_points = np.column_stack(
        [radius * np.cos(theta), radius * np.sin(theta), np.zeros(resolution)],
    )

    top_points = np.column_stack(
        [radius * np.cos(theta), radius * np.sin(theta), np.full(resolution, height)],
    )

    points = np.vstack([bottom_points, top_points])

    # Create faces
    faces = []
    for i in range(resolution):
        next_i = (i + 1) % resolution
        # Side quads (as triangles)
        faces.extend(
            [[3, i, next_i, i + resolution], [3, next_i, next_i + resolution, i + resolution]],
        )

    # Flatten faces list properly
    flattened_faces = []
    for face in faces:
        flattened_faces.extend(face)

    return points.tolist(), flattened_faces


def shrink_mesh(points: np.ndarray, shrink_factor: float = 0.8) -> np.ndarray:
    """Shrink mesh towards its centroid using NumPy vectorization."""
    centroid = np.mean(points, axis=0)
    return centroid + shrink_factor * (points - centroid)


def clip_mesh(
    points: np.ndarray,
    faces: np.ndarray,
    plane_origin: np.ndarray,
    plane_normal: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Clip mesh with a plane using NumPy operations."""
    # Convert inputs to numpy arrays if they aren't already
    points_array = np.array(points)
    plane_origin_array = np.array(plane_origin)
    plane_normal_array = np.array(plane_normal)
    faces_array = np.array(faces)

    # Simple plane clipping implementation
    plane_normal_normalized = plane_normal_array / np.linalg.norm(plane_normal_array)
    distances = np.dot(points_array - plane_origin_array, plane_normal_normalized)

    # Keep points on the positive side of the plane
    keep_mask = distances >= 0

    # Filter points and faces
    new_points = points_array[keep_mask]
    point_map = np.full(len(points_array), -1)
    point_map[keep_mask] = np.arange(np.sum(keep_mask))

    # Filter faces that have all vertices kept
    valid_faces = []
    i = 0
    while i < len(faces_array):
        n_verts = faces_array[i]
        i += 1
        vertex_indices = faces_array[i : i + n_verts]

        # Check if all vertices are kept
        if all(point_map[idx] >= 0 for idx in vertex_indices):
            new_face = [n_verts] + [point_map[idx] for idx in vertex_indices]
            valid_faces.append(new_face)

        i += n_verts

    # Flatten faces list properly
    flattened_faces = []
    for face in valid_faces:
        flattened_faces.extend(face)

    return new_points.tolist(), flattened_faces


def compute_contour(points: np.ndarray, values: np.ndarray, isovalue: float) -> np.ndarray:
    """Compute contour using NumPy vectorization."""
    # Convert inputs to numpy arrays if they aren't already
    points_array = np.array(points)
    values_array = np.array(values)

    # Simple contour extraction based on isovalue
    mask = values_array >= isovalue
    return points_array[mask].tolist()
