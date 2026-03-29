"""Geometric and mesh processing algorithms for pyvista-js.

This module provides NumPy-based implementations of geometric primitives
and mesh processing filters that were originally implemented in TypeScript.
The algorithms generate raw mesh data that can be serialized to JSON
for consumption by the vtk.js rendering pipeline.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple, Union


class GeometricAlgorithms:
    """NumPy-based geometric primitive generation algorithms."""

    @staticmethod
    def create_sphere(
        center: Tuple[float, float, float] = (0.0, 0.0, 0.0),
        radius: float = 1.0,
        theta_resolution: int = 32,
        phi_resolution: int = 32,
    ) -> Dict[str, np.ndarray]:
        """Create a sphere mesh with texture coordinates."""
        # Generate spherical coordinates
        theta = np.linspace(0, 2 * np.pi, theta_resolution, endpoint=False)
        phi = np.linspace(0, np.pi, phi_resolution)

        # Create vertex grid
        points = []
        for j, phi_val in enumerate(phi):
            for i, theta_val in enumerate(theta):
                x = radius * np.sin(phi_val) * np.cos(theta_val)
                y = radius * np.sin(phi_val) * np.sin(theta_val)
                z = radius * np.cos(phi_val)
                points.append([x + center[0], y + center[1], z + center[2]])

        # Add poles
        points.append([center[0], center[1], center[2] + radius])  # North pole
        points.append([center[0], center[1], center[2] - radius])  # South pole

        # Create polygons (quads and triangles at poles)
        polys = []

        # Body quads
        for j in range(phi_resolution - 2):
            for i in range(theta_resolution):
                i_next = (i + 1) % theta_resolution
                p1 = j * theta_resolution + i
                p2 = j * theta_resolution + i_next
                p3 = (j + 1) * theta_resolution + i_next
                p4 = (j + 1) * theta_resolution + i
                polys.extend([4, p1, p2, p3, p4])

        # North pole triangles
        north_pole_idx = len(points) - 2
        for i in range(theta_resolution):
            i_next = (i + 1) % theta_resolution
            p1 = (phi_resolution - 2) * theta_resolution + i
            p2 = (phi_resolution - 2) * theta_resolution + i_next
            polys.extend([3, p1, p2, north_pole_idx])

        # South pole triangles
        south_pole_idx = len(points) - 1
        for i in range(theta_resolution):
            i_next = (i + 1) % theta_resolution
            p1 = i
            p2 = i_next
            polys.extend([3, p1, south_pole_idx, p2])

        # Texture coordinates
        tcoords = []
        for j in range(phi_resolution):
            for i in range(theta_resolution):
                u = i / (theta_resolution - 1) if theta_resolution > 1 else 0
                v = j / (phi_resolution - 1) if phi_resolution > 1 else 0
                tcoords.append([u, v])

        # Pole texture coordinates
        tcoords.append([0.5, 1.0])  # North pole
        tcoords.append([0.5, 0.0])  # South pole

        return {
            "points": np.array(points, dtype=np.float32),
            "polys": np.array(polys, dtype=np.uint32),
            "tcoords": np.array(tcoords, dtype=np.float32),
        }

    @staticmethod
    def create_cone(
        height: float = 1.0,
        radius: float = 0.5,
        resolution: int = 32,
        center: Tuple[float, float, float] = (0.0, 0.0, 0.0),
    ) -> Dict[str, np.ndarray]:
        """Create a cone mesh."""
        points = []
        polys = []

        # Base center
        base_center = [center[0], center[1], center[2] - height / 2]
        points.append(base_center)

        # Base circumference
        for i in range(resolution):
            angle = 2 * np.pi * i / resolution
            x = center[0] + radius * np.cos(angle)
            y = center[1] + radius * np.sin(angle)
            z = center[2] - height / 2
            points.append([x, y, z])

        # Apex
        apex = [center[0], center[1], center[2] + height / 2]
        points.append(apex)

        # Base triangles
        for i in range(resolution):
            i_next = (i + 1) % resolution
            polys.extend([3, 0, i + 1, i_next + 1])

        # Side triangles
        for i in range(resolution):
            i_next = (i + 1) % resolution
            polys.extend([3, i + 1, i_next + 1, len(points) - 1])

        return {
            "points": np.array(points, dtype=np.float32),
            "polys": np.array(polys, dtype=np.uint32),
        }

    @staticmethod
    def create_cube(
        x_length: float = 1.0,
        y_length: float = 1.0,
        z_length: float = 1.0,
        center: Tuple[float, float, float] = (0.0, 0.0, 0.0),
    ) -> Dict[str, np.ndarray]:
        """Create a cube mesh."""
        # Half dimensions
        hx, hy, hz = x_length / 2, y_length / 2, z_length / 2

        # 8 vertices
        points = [
            [center[0] - hx, center[1] - hy, center[2] - hz],  # 0
            [center[0] + hx, center[1] - hy, center[2] - hz],  # 1
            [center[0] + hx, center[1] + hy, center[2] - hz],  # 2
            [center[0] - hx, center[1] + hy, center[2] - hz],  # 3
            [center[0] - hx, center[1] - hy, center[2] + hz],  # 4
            [center[0] + hx, center[1] - hy, center[2] + hz],  # 5
            [center[0] + hx, center[1] + hy, center[2] + hz],  # 6
            [center[0] - hx, center[1] + hy, center[2] + hz],  # 7
        ]

        # 6 faces (quads)
        polys = [
            4,
            0,
            1,
            2,
            3,  # Bottom
            4,
            4,
            7,
            6,
            5,  # Top
            4,
            0,
            4,
            5,
            1,  # Front
            4,
            2,
            6,
            7,
            3,  # Back
            4,
            0,
            3,
            7,
            4,  # Left
            4,
            1,
            5,
            6,
            2,  # Right
        ]

        return {
            "points": np.array(points, dtype=np.float32),
            "polys": np.array(polys, dtype=np.uint32),
        }

    @staticmethod
    def create_cylinder(
        height: float = 1.0,
        radius: float = 0.5,
        resolution: int = 32,
        center: Tuple[float, float, float] = (0.0, 0.0, 0.0),
    ) -> Dict[str, np.ndarray]:
        """Create a cylinder mesh."""
        points = []
        polys = []

        # Bottom and top centers
        bottom_center = [center[0], center[1], center[2] - height / 2]
        top_center = [center[0], center[1], center[2] + height / 2]
        points.append(bottom_center)
        points.append(top_center)

        # Bottom and top circumferences
        for i in range(resolution):
            angle = 2 * np.pi * i / resolution
            x = center[0] + radius * np.cos(angle)
            y = center[1] + radius * np.sin(angle)

            # Bottom circle
            points.append([x, y, bottom_center[2]])

            # Top circle
            points.append([x, y, top_center[2]])

        # Bottom triangles
        for i in range(resolution):
            i_next = (i + 1) % resolution
            polys.extend([3, 0, 2 + i * 2, 2 + i_next * 2])

        # Top triangles
        for i in range(resolution):
            i_next = (i + 1) % resolution
            polys.extend([3, 1, 3 + i_next * 2, 3 + i * 2])

        # Side quads
        for i in range(resolution):
            i_next = (i + 1) % resolution
            p1 = 2 + i * 2
            p2 = 2 + i_next * 2
            p3 = 3 + i_next * 2
            p4 = 3 + i * 2
            polys.extend([4, p1, p2, p3, p4])

        return {
            "points": np.array(points, dtype=np.float32),
            "polys": np.array(polys, dtype=np.uint32),
        }


class MeshProcessingAlgorithms:
    """NumPy-based mesh processing and filtering algorithms."""

    @staticmethod
    def apply_shrink_filter(
        points: np.ndarray, polys: np.ndarray, shrink_factor: float = 0.8
    ) -> Dict[str, np.ndarray]:
        """Apply shrink filter to mesh - move vertices toward cell centroids."""
        if len(polys) == 0:
            return {"points": points.copy(), "polys": polys.copy()}

        result_points = []
        result_polys = []
        offset = 0
        index = 0

        while index < len(polys):
            n_verts = int(polys[index])
            index += 1

            # Calculate cell centroid
            centroid = np.zeros(3)
            indices = []

            for i in range(n_verts):
                vi = int(polys[index + i])
                indices.append(vi)
                centroid += points[vi]

            centroid /= n_verts

            # Add shrunk vertices
            result_polys.append(n_verts)
            for i in range(n_verts):
                pi = indices[i]
                point = points[pi]
                # Move toward centroid
                shrunk_point = centroid + (point - centroid) * shrink_factor
                result_points.extend(shrunk_point)
                result_polys.append(offset + i)

            offset += n_verts
            index += n_verts

        return {
            "points": np.array(result_points, dtype=np.float32).reshape(-1, 3),
            "polys": np.array(result_polys, dtype=np.uint32),
        }

    @staticmethod
    def apply_clip_filter(
        points: np.ndarray,
        polys: np.ndarray,
        normal: Tuple[float, float, float],
        origin: Tuple[float, float, float],
        invert: bool = False,
    ) -> Dict[str, np.ndarray]:
        """Clip mesh by plane using centroid-based cell culling."""
        if len(polys) == 0:
            return {"points": points.copy(), "polys": polys.copy()}

        normal = np.array(normal)
        origin = np.array(origin)

        result_points = []
        result_polys = []
        point_map = {}
        next_index = 0
        index = 0

        while index < len(polys):
            n_verts = int(polys[index])
            index += 1

            # Calculate cell centroid
            centroid = np.zeros(3)
            cell_indices = []

            for i in range(n_verts):
                vi = int(polys[index + i])
                cell_indices.append(vi)
                centroid += points[vi]

            centroid /= n_verts

            # Check if cell should be kept
            dot_product = np.dot(centroid - origin, normal)
            keep = (dot_product <= 0) if not invert else (dot_product >= 0)

            if keep:
                result_polys.append(n_verts)
                for i in range(n_verts):
                    pi = cell_indices[i]
                    if pi not in point_map:
                        point_map[pi] = next_index
                        next_index += 1
                        result_points.extend(points[pi])
                    result_polys.append(point_map[pi])

            index += n_verts

        return {
            "points": np.array(result_points, dtype=np.float32).reshape(-1, 3),
            "polys": np.array(result_polys, dtype=np.uint32),
        }

    @staticmethod
    def apply_contour_filter(
        points: np.ndarray, polys: np.ndarray, scalar_data: np.ndarray, values: List[float]
    ) -> Dict[str, np.ndarray]:
        """Extract contour lines using marching triangles algorithm."""
        if len(polys) == 0 or len(scalar_data) == 0:
            return {
                "points": np.zeros((0, 3), dtype=np.float32),
                "lines": np.array([], dtype=np.uint32),
            }

        out_points = []
        out_lines = []
        point_index = 0
        index = 0

        def interpolate_edge(p1: int, p2: int, s1: float, s2: float, value: float) -> np.ndarray:
            """Interpolate point on edge."""
            if (s1 <= value < s2) or (s2 <= value < s1):
                t = (value - s1) / (s2 - s1)
                return points[p1] + t * (points[p2] - points[p1])
            return None

        while index < len(polys):
            n_verts = int(polys[index])
            index += 1

            if n_verts == 3:  # Triangle only
                idx0 = int(polys[index])
                idx1 = int(polys[index + 1])
                idx2 = int(polys[index + 2])

                s0 = scalar_data[idx0]
                s1 = scalar_data[idx1]
                s2 = scalar_data[idx2]

                for value in values:
                    intersections = []

                    # Check each edge for intersection
                    edges = [(idx0, idx1, s0, s1), (idx1, idx2, s1, s2), (idx2, idx0, s2, s0)]

                    for edge in edges:
                        intersection = interpolate_edge(*edge, value)
                        if intersection is not None:
                            intersections.append(intersection)

                    # If we have exactly 2 intersections, create a line
                    if len(intersections) == 2:
                        out_points.extend(intersections[0])
                        out_points.extend(intersections[1])
                        out_lines.extend([2, point_index, point_index + 1])
                        point_index += 2

            index += n_verts

        return {
            "points": np.array(out_points, dtype=np.float32).reshape(-1, 3)
            if out_points
            else np.zeros((0, 3), dtype=np.float32),
            "lines": np.array(out_lines, dtype=np.uint32)
            if out_lines
            else np.array([], dtype=np.uint32),
        }


def mesh_to_vtkjs_dict(mesh_data: Dict[str, np.ndarray]) -> Dict[str, List]:
    """Convert mesh data to JSON-serializable format for vtk.js."""
    result = {}
    for key, array in mesh_data.items():
        if isinstance(array, np.ndarray):
            result[key] = array.tolist()
        else:
            result[key] = array
    return result


# Convenience functions for direct use
def create_sphere_source(**kwargs) -> Dict[str, List]:
    """Create sphere source with vtk.js compatible output."""
    mesh = GeometricAlgorithms.create_sphere(**kwargs)
    return mesh_to_vtkjs_dict(mesh)


def create_cone_source(**kwargs) -> Dict[str, List]:
    """Create cone source with vtk.js compatible output."""
    mesh = GeometricAlgorithms.create_cone(**kwargs)
    return mesh_to_vtkjs_dict(mesh)


def create_cube_source(**kwargs) -> Dict[str, List]:
    """Create cube source with vtk.js compatible output."""
    mesh = GeometricAlgorithms.create_cube(**kwargs)
    return mesh_to_vtkjs_dict(mesh)


def create_cylinder_source(**kwargs) -> Dict[str, List]:
    """Create cylinder source with vtk.js compatible output."""
    mesh = GeometricAlgorithms.create_cylinder(**kwargs)
    return mesh_to_vtkjs_dict(mesh)


def apply_shrink_filter_source(
    points: List, polys: List, shrink_factor: float = 0.8
) -> Dict[str, List]:
    """Apply shrink filter with vtk.js compatible output."""
    points_array = np.array(points, dtype=np.float32).reshape(-1, 3)
    polys_array = np.array(polys, dtype=np.uint32)
    mesh = MeshProcessingAlgorithms.apply_shrink_filter(points_array, polys_array, shrink_factor)
    return mesh_to_vtkjs_dict(mesh)


def apply_clip_filter_source(
    points: List,
    polys: List,
    normal: Tuple[float, float, float],
    origin: Tuple[float, float, float],
    invert: bool = False,
) -> Dict[str, List]:
    """Apply clip filter with vtk.js compatible output."""
    points_array = np.array(points, dtype=np.float32).reshape(-1, 3)
    polys_array = np.array(polys, dtype=np.uint32)
    mesh = MeshProcessingAlgorithms.apply_clip_filter(
        points_array, polys_array, normal, origin, invert
    )
    return mesh_to_vtkjs_dict(mesh)


def apply_contour_filter_source(
    points: List, polys: List, scalar_data: List, values: List[float]
) -> Dict[str, List]:
    """Apply contour filter with vtk.js compatible output."""
    points_array = np.array(points, dtype=np.float32).reshape(-1, 3)
    polys_array = np.array(polys, dtype=np.uint32)
    scalar_array = np.array(scalar_data, dtype=np.float32)
    mesh = MeshProcessingAlgorithms.apply_contour_filter(
        points_array, polys_array, scalar_array, values
    )
    return mesh_to_vtkjs_dict(mesh)
