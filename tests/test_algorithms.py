"""Tests for pyvista-js algorithms module."""

import numpy as np
import pytest
from pyvista_js.algorithms import (
    GeometricAlgorithms,
    MeshProcessingAlgorithms,
    create_sphere_source,
    create_cone_source,
    create_cube_source,
    create_cylinder_source,
    apply_shrink_filter_source,
    apply_clip_filter_source,
    apply_contour_filter_source,
)


class TestGeometricAlgorithms:
    """Test geometric primitive generation algorithms."""

    def test_create_sphere_basic(self):
        """Test basic sphere creation."""
        result = GeometricAlgorithms.create_sphere()

        assert "points" in result
        assert "polys" in result
        assert "tcoords" in result

        # Check that we have vertices
        assert result["points"].shape[0] > 0
        assert result["points"].shape[1] == 3  # 3D coordinates

        # Check that we have polygons
        assert result["polys"].shape[0] > 0

        # Check that we have texture coordinates
        assert result["tcoords"].shape[0] > 0
        assert result["tcoords"].shape[1] == 2  # 2D texture coordinates

    def test_create_cone_basic(self):
        """Test basic cone creation."""
        result = GeometricAlgorithms.create_cone()

        assert "points" in result
        assert "polys" in result

        # Check structure
        points = result["points"]
        polys = result["polys"]

        assert points.shape[0] > 0
        assert points.shape[1] == 3
        assert polys.shape[0] > 0

    def test_create_cube_basic(self):
        """Test basic cube creation."""
        result = GeometricAlgorithms.create_cube()

        assert "points" in result
        assert "polys" in result

        points = result["points"]
        polys = result["polys"]

        # Should have exactly 8 vertices
        assert points.shape[0] == 8
        assert points.shape[1] == 3

    def test_create_cylinder_basic(self):
        """Test basic cylinder creation."""
        result = GeometricAlgorithms.create_cylinder()

        assert "points" in result
        assert "polys" in result

        points = result["points"]
        polys = result["polys"]

        assert points.shape[0] > 0
        assert points.shape[1] == 3
        assert polys.shape[0] > 0


class TestMeshProcessingAlgorithms:
    """Test mesh processing algorithms."""

    def test_apply_shrink_filter_basic(self):
        """Test basic shrink filter application."""
        # Create a simple cube
        cube = GeometricAlgorithms.create_cube(x_length=2.0, y_length=2.0, z_length=2.0)
        points = cube["points"]
        polys = cube["polys"]

        # Apply shrink filter
        result = MeshProcessingAlgorithms.apply_shrink_filter(points, polys, shrink_factor=0.8)

        assert "points" in result
        assert "polys" in result

        # Check that topology structure is preserved (same number of faces, same face sizes)
        # The actual vertex indices will change due to point remapping
        assert len(result["polys"]) == len(polys)

        # Check that face sizes are preserved
        orig_idx = 0
        result_idx = 0
        while orig_idx < len(polys) and result_idx < len(result["polys"]):
            orig_n_verts = polys[orig_idx]
            result_n_verts = result["polys"][result_idx]
            assert orig_n_verts == result_n_verts
            orig_idx += orig_n_verts + 1
            result_idx += result_n_verts + 1

        # Check that points have moved toward centroids (vertices should be closer to origin)
        original_centroid = np.mean(points, axis=0)
        shrunk_centroid = np.mean(result["points"], axis=0)

        # Centroid should remain approximately the same
        np.testing.assert_allclose(original_centroid, shrunk_centroid, rtol=1e-5)

    def test_apply_clip_filter_basic(self):
        """Test basic clip filter application."""
        # Create a simple cube
        cube = GeometricAlgorithms.create_cube(x_length=2.0, y_length=2.0, z_length=2.0)
        points = cube["points"]
        polys = cube["polys"]

        # Clip with plane at z=0, normal pointing up
        result = MeshProcessingAlgorithms.apply_clip_filter(
            points, polys, normal=(0.0, 0.0, 1.0), origin=(0.0, 0.0, 0.0), invert=False
        )

        assert "points" in result
        assert "polys" in result

    def test_apply_contour_filter_basic(self):
        """Test basic contour filter application."""
        # Create a simple mesh with scalar data
        points = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.5, 1.0, 0.0]], dtype=np.float32)

        polys = np.array([3, 0, 1, 2], dtype=np.uint32)
        scalar_data = np.array([0.0, 1.0, 0.5], dtype=np.float32)
        values = [0.5]

        result = MeshProcessingAlgorithms.apply_contour_filter(points, polys, scalar_data, values)

        assert "points" in result
        assert "lines" in result


class TestConvenienceFunctions:
    """Test convenience functions for vtk.js compatibility."""

    def test_create_sphere_source_json(self):
        """Test sphere source with JSON serialization."""
        result = create_sphere_source(center=(1.0, 2.0, 3.0), radius=1.5)

        # Should return JSON-serializable format
        assert isinstance(result, dict)
        assert "points" in result
        assert "polys" in result
        assert "tcoords" in result

    def test_apply_shrink_filter_source_json(self):
        """Test shrink filter with JSON serialization."""
        # Create simple test data
        points = [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [1.0, 1.0, 0.0]]
        polys = [4, 0, 1, 3, 2]  # Quad

        result = apply_shrink_filter_source(points, polys, shrink_factor=0.8)

        assert isinstance(result, dict)
        assert "points" in result
        assert "polys" in result


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_empty_mesh_shrink(self):
        """Test shrink filter on empty mesh."""
        points = np.zeros((0, 3), dtype=np.float32)
        polys = np.array([], dtype=np.uint32)

        result = MeshProcessingAlgorithms.apply_shrink_filter(points, polys)

        assert result["points"].shape[0] == 0
        assert result["polys"].shape[0] == 0

    def test_empty_mesh_clip(self):
        """Test clip filter on empty mesh."""
        points = np.zeros((0, 3), dtype=np.float32)
        polys = np.array([], dtype=np.uint32)

        result = MeshProcessingAlgorithms.apply_clip_filter(
            points, polys, (0.0, 0.0, 1.0), (0.0, 0.0, 0.0)
        )

        assert result["points"].shape[0] == 0
        assert result["polys"].shape[0] == 0

    def test_empty_mesh_contour(self):
        """Test contour filter on empty mesh."""
        points = np.zeros((0, 3), dtype=np.float32)
        polys = np.array([], dtype=np.uint32)
        scalar_data = np.array([], dtype=np.float32)

        result = MeshProcessingAlgorithms.apply_contour_filter(points, polys, scalar_data, [0.5])

        assert result["points"].shape[0] == 0
        assert result["lines"].shape[0] == 0
