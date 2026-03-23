"""Test mesh creation and properties."""

import builtins
import webbrowser
from pathlib import Path

import numpy as np
import pytest

from pyvista_js import (
    Arrow,
    Circle,
    Cone,
    Cube,
    Cylinder,
    Disc,
    Line,
    Plane,
    PolyData,
    Sphere,
)


def test_mesh_creation() -> None:
    """Test basic mesh creation."""
    points = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]])
    mesh = PolyData(points)

    assert mesh.n_points == 3
    assert np.array_equal(mesh.points, points)


def test_sphere_creation() -> None:
    """Test sphere primitive creation."""
    sphere = Sphere(radius=1.0)

    assert sphere.n_points > 0
    assert isinstance(sphere.points, np.ndarray)
    assert sphere.points.shape[1] == 3  # 3D coordinates


def test_sphere_parameters() -> None:
    """Test sphere with custom parameters."""
    sphere = Sphere(radius=2.0, center=(1, 2, 3))

    # Check that points are roughly centered at (1, 2, 3)
    center = np.mean(sphere.points, axis=0)
    assert np.allclose(center, [1, 2, 3], atol=0.1)


def test_cube_creation() -> None:
    """Test cube primitive creation."""
    cube = Cube()

    assert cube.n_points == 24
    assert cube.n_faces == 6


def test_cube_size() -> None:
    """Test cube with custom size."""
    cube = Cube(x_length=2.0, y_length=2.0, z_length=2.0)

    # Check bounding box
    mins = np.min(cube.points, axis=0)
    maxs = np.max(cube.points, axis=0)

    assert np.allclose(maxs - mins, [2.0, 2.0, 2.0])


def test_cylinder_creation() -> None:
    """Test cylinder primitive creation."""
    cylinder = Cylinder(radius=1.0, height=2.0)

    assert cylinder.n_points > 0
    assert isinstance(cylinder.points, np.ndarray)


def test_bounding_sphere_empty_mesh() -> None:
    """Test bounding_sphere returns NaN values for a mesh with no points."""
    mesh = PolyData(points=np.empty((0, 3)))
    r, c = mesh.bounding_sphere

    assert np.isnan(r)
    assert all(np.isnan(x) for x in c)


@pytest.mark.parametrize(
    ("mesh_factory", "expected_radius", "expected_center"),
    [
        (lambda: Sphere(radius=1.5, center=(1.0, 2.0, 3.0)), 1.5, (1.0, 2.0, 3.0)),
        (lambda: Sphere(radius=0.5, center=(0.0, 0.0, 0.0)), 0.5, (0.0, 0.0, 0.0)),
        (
            lambda: Cube(center=(0.0, 0.0, 0.0), x_length=2.0, y_length=2.0, z_length=2.0),
            3**0.5,
            (0.0, 0.0, 0.0),
        ),
    ],
)
def test_bounding_sphere(mesh_factory, expected_radius, expected_center) -> None:
    """Test bounding_sphere radius and center for various meshes."""
    mesh = mesh_factory()
    r, c = mesh.bounding_sphere

    assert isinstance(r, float)
    assert isinstance(c, tuple)
    assert len(c) == 3
    assert all(isinstance(x, float) for x in c)
    assert np.isclose(r, expected_radius, atol=1e-3)
    assert np.allclose(c, expected_center, atol=1e-3)


def test_mesh_plot(monkeypatch) -> None:
    """Test that Mesh.plot() creates a plotter, adds the mesh, and shows it."""
    opened: list[str] = []
    monkeypatch.setattr(webbrowser, "open", opened.append)

    sphere = Sphere(radius=1.0)
    sphere.plot(color="red")

    assert len(opened) == 1
    assert opened[0].startswith("file://")


def test_mesh_plot_with_kwargs(monkeypatch) -> None:
    """Test that Mesh.plot() passes kwargs to add_mesh."""
    opened: list[str] = []
    monkeypatch.setattr(webbrowser, "open", opened.append)

    cube = Cube()
    cube.plot(color="blue", opacity=0.5)

    assert len(opened) == 1


def test_generic_mesh_plot(monkeypatch) -> None:
    """Test that generic PolyData instances can also use plot()."""
    opened: list[str] = []
    monkeypatch.setattr(webbrowser, "open", opened.append)

    points = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]])
    mesh = PolyData(points)
    mesh.plot()

    assert len(opened) == 1


def test_shrink_returns_polydata() -> None:
    """Test that shrink returns a PolyData instance."""
    sphere = Sphere()
    shrunk = sphere.shrink(shrink_factor=0.8)
    assert isinstance(shrunk, PolyData)
    assert shrunk.n_points == sphere.n_points


def test_shrink_default_factor() -> None:
    """Test that shrink works with default shrink_factor."""
    cube = Cube()
    shrunk = cube.shrink()
    assert isinstance(shrunk, PolyData)


def test_shrink_vtk_js_source_contains_shrink_logic() -> None:
    """Test that shrunk mesh generates JS with the custom shrink computation."""
    sphere = Sphere()
    shrunk = sphere.shrink(shrink_factor=0.5)
    js_source = shrunk.generate_vtk_js_source(0)
    assert "shrunkPD0" in js_source
    assert "0.5" in js_source
    assert "vtkPolyData" in js_source


def test_shrink_mapper_setup_uses_shrunk_pd() -> None:
    """Test that shrunk mesh mapper uses setInputData with the shrunk polydata."""
    sphere = Sphere()
    shrunk = sphere.shrink(shrink_factor=0.8)
    mapper_code = shrunk.get_mapper_setup(0)
    assert "shrunkPD0" in mapper_code
    assert "setInputData" in mapper_code


def test_shrink_invalid_factor() -> None:
    """Test that an invalid shrink_factor raises ValueError."""
    sphere = Sphere()
    with pytest.raises(ValueError, match="shrink_factor must be between 0 and 1"):
        sphere.shrink(shrink_factor=1.5)
    with pytest.raises(ValueError, match="shrink_factor must be between 0 and 1"):
        sphere.shrink(shrink_factor=-0.1)


def test_shrink_preserves_faces() -> None:
    """Test that shrink preserves face information."""
    cube = Cube()
    shrunk = cube.shrink(shrink_factor=0.8)
    assert shrunk.n_faces == cube.n_faces


def test_clip_returns_polydata() -> None:
    """Test that clip returns a PolyData instance."""
    sphere = Sphere()
    clipped = sphere.clip(normal="x", origin=(0, 0, 0))
    assert isinstance(clipped, PolyData)


def test_clip_default_normal() -> None:
    """Test that clip works with default normal ('x')."""
    cube = Cube()
    clipped = cube.clip()
    assert isinstance(clipped, PolyData)


def test_clip_string_normals() -> None:
    """Test clip with all valid string normal directions."""
    sphere = Sphere()
    for normal in ["x", "+x", "-x", "y", "+y", "-y", "z", "+z", "-z"]:
        clipped = sphere.clip(normal=normal)
        assert isinstance(clipped, PolyData)


def test_clip_tuple_normal() -> None:
    """Test clip with tuple normal vector."""
    sphere = Sphere()
    clipped = sphere.clip(normal=(1.0, 1.0, 0.0), origin=(0, 0, 0))
    assert isinstance(clipped, PolyData)


def test_clip_default_origin() -> None:
    """Test that clip uses mesh center as default origin."""
    sphere = Sphere()
    clipped = sphere.clip(normal="x")
    assert isinstance(clipped, PolyData)


def test_clip_custom_origin() -> None:
    """Test clip with custom origin."""
    sphere = Sphere()
    clipped = sphere.clip(normal="x", origin=(0.5, 0.0, 0.0))
    assert isinstance(clipped, PolyData)


def test_clip_invert() -> None:
    """Test clip with invert flag."""
    sphere = Sphere()
    clipped = sphere.clip(normal="x", origin=(0, 0, 0), invert=True)
    assert isinstance(clipped, PolyData)


def test_clip_vtk_js_source_contains_clip_logic() -> None:
    """Test that clipped mesh generates JS with the custom clip computation."""
    sphere = Sphere()
    clipped = sphere.clip(normal="y", origin=(0, 0, 0))
    js_source = clipped.generate_vtk_js_source(0)
    assert "clippedPD0" in js_source
    assert "vtkPolyData" in js_source
    # Check that normal and origin are in the source
    assert "0.0" in js_source  # normal x component
    assert "1.0" in js_source  # normal y component


def test_clip_mapper_setup_uses_clipped_pd() -> None:
    """Test that clipped mesh mapper uses setInputData with the clipped polydata."""
    sphere = Sphere()
    clipped = sphere.clip(normal="x", origin=(0, 0, 0))
    mapper_code = clipped.get_mapper_setup(0)
    assert "clippedPD0" in mapper_code
    assert "setInputData" in mapper_code


def test_clip_invalid_normal_string() -> None:
    """Test that an invalid normal string raises ValueError."""
    sphere = Sphere()
    with pytest.raises(ValueError, match="Invalid normal string"):
        sphere.clip(normal="invalid")


def test_clip_invalid_normal_tuple_length() -> None:
    """Test that a normal tuple with wrong length raises ValueError."""
    sphere = Sphere()
    with pytest.raises(ValueError, match="Normal vector must have 3 components"):
        sphere.clip(normal=(1.0, 0.0))  # type: ignore[arg-type]


def test_clip_invalid_origin_length() -> None:
    """Test that an origin with wrong length raises ValueError."""
    sphere = Sphere()
    with pytest.raises(ValueError, match="Origin must have 3 components"):
        sphere.clip(normal="x", origin=(0.0, 0.0))  # type: ignore[arg-type]


def test_clip_preserves_points_and_faces() -> None:
    """Test that clip preserves point and face data structures."""
    cube = Cube()
    clipped = cube.clip(normal="x", origin=(0, 0, 0))
    # The clipped mesh should have the same point and face arrays
    # (filtering happens in JavaScript)
    assert clipped.points.shape == cube.points.shape
    assert clipped.n_faces == cube.n_faces


def test_tube_returns_polydata() -> None:
    """Test that tube returns a PolyData instance."""
    line = Line()
    tube = line.tube(radius=0.5, n_sides=20)
    assert isinstance(tube, PolyData)
    assert tube.n_points == line.n_points


def test_tube_default_parameters() -> None:
    """Test that tube works with default parameters."""
    line = Line()
    tube = line.tube()
    assert isinstance(tube, PolyData)


def test_tube_vtk_js_source_contains_tube_logic() -> None:
    """Test that tubed mesh generates JS with the tube filter."""
    line = Line()
    tube = line.tube(radius=0.1, n_sides=12)
    js_source = tube.generate_vtk_js_source(0)
    assert "tubedPD0" in js_source
    assert "0.1" in js_source
    assert "12" in js_source
    assert "vtkTubeFilter" in js_source


def test_tube_mapper_setup_uses_tubed_pd() -> None:
    """Test that tubed mesh mapper uses setInputData with the tubed polydata."""
    line = Line()
    tube = line.tube(radius=0.5, n_sides=20)
    mapper_code = tube.get_mapper_setup(0)
    assert "tubedPD0" in mapper_code
    assert "setInputData" in mapper_code


def test_tube_invalid_radius() -> None:
    """Test that an invalid radius raises ValueError."""
    line = Line()
    with pytest.raises(ValueError, match="radius must be positive"):
        line.tube(radius=0)
    with pytest.raises(ValueError, match="radius must be positive"):
        line.tube(radius=-0.1)


def test_tube_invalid_n_sides() -> None:
    """Test that invalid n_sides raises ValueError."""
    line = Line()
    with pytest.raises(ValueError, match="n_sides must be at least 3"):
        line.tube(n_sides=2)
    with pytest.raises(ValueError, match="n_sides must be at least 3"):
        line.tube(n_sides=0)


def test_tube_capping_parameter() -> None:
    """Test that capping parameter is properly propagated."""
    line = Line()
    tube_capped = line.tube(radius=0.5, capping=True)
    tube_uncapped = line.tube(radius=0.5, capping=False)

    js_capped = tube_capped.generate_vtk_js_source(0)
    js_uncapped = tube_uncapped.generate_vtk_js_source(0)

    assert 'data-capping="&quot;true&quot;"' in js_capped or 'data-capping=""true""' in js_capped
    assert (
        'data-capping="&quot;false&quot;"' in js_uncapped or 'data-capping=""false""' in js_uncapped
    )


def test_tube_preserves_faces() -> None:
    """Test that tube preserves face information."""
    line = Line()
    tube = line.tube(radius=0.5, n_sides=20)
    assert tube.n_faces == line.n_faces


def test_contour_returns_polydata() -> None:
    """Test that contour returns a PolyData instance."""
    sphere = Sphere()
    scalars = sphere.points[:, 2]  # Z coordinate
    contours = sphere.contour(isosurfaces=5, scalars=scalars)
    assert isinstance(contours, PolyData)


def test_contour_with_int_isosurfaces() -> None:
    """Test contour with integer number of isosurfaces."""
    sphere = Sphere()
    scalars = sphere.points[:, 2]
    contours = sphere.contour(isosurfaces=3, scalars=scalars)
    js_source = contours.generate_vtk_js_source(0)
    assert "contourPD0" in js_source
    assert "Marching triangles" in js_source or "marching" in js_source.lower()
    # Should have 3 values in the array
    assert "values.length" in js_source


def test_contour_with_list_isosurfaces() -> None:
    """Test contour with explicit list of isosurface values."""
    sphere = Sphere()
    scalars = sphere.points[:, 2]
    contours = sphere.contour(isosurfaces=[0.0, 0.5, 1.0], scalars=scalars)
    js_source = contours.generate_vtk_js_source(0)
    assert "contourPD0" in js_source
    assert "0.0" in js_source or "0" in js_source
    assert "0.5" in js_source
    assert "1.0" in js_source or "1" in js_source


def test_contour_mapper_setup_uses_contour_pd() -> None:
    """Test that contour mesh mapper uses setInputData with contourPD."""
    sphere = Sphere()
    scalars = sphere.points[:, 2]
    contours = sphere.contour(isosurfaces=5, scalars=scalars)
    mapper_code = contours.get_mapper_setup(0)
    assert "contourPD0" in mapper_code
    assert "setInputData" in mapper_code


def test_contour_no_scalars_raises() -> None:
    """Test that contour without scalars raises ValueError."""
    sphere = Sphere()
    with pytest.raises(ValueError, match="No scalar data provided"):
        sphere.contour(isosurfaces=5)


def test_contour_invalid_scalar_length_raises() -> None:
    """Test that scalars with wrong length raises ValueError."""
    sphere = Sphere()
    scalars = np.array([1, 2, 3])  # Wrong length
    with pytest.raises(ValueError, match="scalars must have length"):
        sphere.contour(isosurfaces=5, scalars=scalars)


def test_contour_invalid_isosurfaces_int_raises() -> None:
    """Test that invalid integer isosurfaces raises ValueError."""
    sphere = Sphere()
    scalars = sphere.points[:, 2]
    with pytest.raises(ValueError, match="isosurfaces must be >= 1"):
        sphere.contour(isosurfaces=0, scalars=scalars)
    with pytest.raises(ValueError, match="isosurfaces must be >= 1"):
        sphere.contour(isosurfaces=-5, scalars=scalars)


def test_contour_empty_list_raises() -> None:
    """Test that empty isosurfaces list raises ValueError."""
    sphere = Sphere()
    scalars = sphere.points[:, 2]
    with pytest.raises(ValueError, match="isosurfaces list must contain at least one value"):
        sphere.contour(isosurfaces=[], scalars=scalars)


def test_contour_with_mesh_scalars() -> None:
    """Test contour using scalars stored on the mesh."""
    sphere = Sphere()
    scalars = sphere.points[:, 2]
    sphere_with_scalars = PolyData(
        points=sphere.points,
        faces=sphere.faces,
        scalars=scalars,
        scalar_name="elevation",
    )
    contours = sphere_with_scalars.contour(isosurfaces=5)
    assert isinstance(contours, PolyData)
    js_source = contours.generate_vtk_js_source(0)
    assert "contourPD0" in js_source
    assert "elevation" in js_source


def test_contour_scalar_injection() -> None:
    """Test that scalar data is properly injected into vtk.js code."""
    sphere = Sphere()
    scalars = sphere.points[:, 2]
    contours = sphere.contour(isosurfaces=5, scalars=scalars, scalar_name="test_scalars")
    js_source = contours.generate_vtk_js_source(0)
    assert "test_scalars" in js_source
    assert "vtkDataArray" in js_source
    assert "setScalars" in js_source
    assert "Float32Array" in js_source


def test_contour_preserves_scalar_data() -> None:
    """Test that contour preserves scalar data in returned mesh."""
    sphere = Sphere()
    scalars = sphere.points[:, 2]
    contours = sphere.contour(isosurfaces=5, scalars=scalars)
    assert contours.scalars is not None
    assert len(contours.scalars) == sphere.n_points


def test_contour_custom_scalar_name() -> None:
    """Test contour with custom scalar name."""
    cube = Cube()
    scalars = cube.points[:, 0] + cube.points[:, 1]
    contours = cube.contour(isosurfaces=3, scalars=scalars, scalar_name="custom_field")
    js_source = contours.generate_vtk_js_source(0)
    assert "custom_field" in js_source


def test_circle_creation() -> None:
    """Test circle primitive creation."""
    circle = Circle()

    assert isinstance(circle, PolyData)
    assert circle.n_points == 101  # resolution(100) + 1 closing point
    assert circle.points.shape[1] == 3


def test_circle_default_radius() -> None:
    """Test that default circle has radius 0.5."""
    circle = Circle()
    radii = np.linalg.norm(circle.points[:-1, :2], axis=1)
    assert np.allclose(radii, 0.5, atol=1e-10)


def test_circle_custom_radius() -> None:
    """Test circle with custom radius."""
    circle = Circle(radius=2.0)
    radii = np.linalg.norm(circle.points[:-1, :2], axis=1)
    assert np.allclose(radii, 2.0, atol=1e-10)


def test_circle_in_xy_plane() -> None:
    """Test that circle points lie in the XY plane (z=0)."""
    circle = Circle(radius=1.0)
    assert np.allclose(circle.points[:, 2], 0.0)


def test_circle_resolution() -> None:
    """Test circle with custom resolution."""
    circle = Circle(radius=1.0, resolution=50)
    assert circle.n_points == 51  # resolution + 1 closing point


def test_circle_closed() -> None:
    """Test that the circle is closed (first and last points are equal)."""
    circle = Circle(radius=1.0, resolution=100)
    assert np.allclose(circle.points[0], circle.points[-1])


def test_circle_invalid_resolution() -> None:
    """Test that resolution < 3 raises ValueError."""
    with pytest.raises(ValueError, match="resolution must be >= 3"):
        Circle(radius=1.0, resolution=2)


def test_circle_vtk_js_source() -> None:
    """Test that Circle generates vtk.js source code."""
    circle = Circle(radius=1.5, resolution=60)
    js_source = circle.generate_vtk_js_source(0)
    assert "1.5" in js_source
    assert "60" in js_source


def test_circle_mapper_setup() -> None:
    """Test that Circle mapper uses setInputData."""
    circle = Circle()
    mapper_code = circle.get_mapper_setup(0)
    assert "setInputData" in mapper_code
    assert "source0" in mapper_code


def test_disc_creation() -> None:
    """Test disc primitive creation."""
    disc = Disc()
    assert isinstance(disc, PolyData)
    assert disc.n_points > 0
    assert disc.points.shape[1] == 3


def test_disc_default_radii() -> None:
    """Test that default disc has inner=0.25 and outer=0.5."""
    disc = Disc()
    radii = np.linalg.norm(disc.points[:, :2], axis=1)
    assert radii.min() >= 0.25 - 1e-10
    assert radii.max() <= 0.5 + 1e-10


def test_disc_custom_radii() -> None:
    """Test disc with custom inner and outer radii."""
    disc = Disc(inner=0.1, outer=1.0)
    radii = np.linalg.norm(disc.points[:, :2], axis=1)
    assert radii.min() >= 0.1 - 1e-10
    assert radii.max() <= 1.0 + 1e-10


def test_disc_center() -> None:
    """Test disc with a custom center."""
    disc = Disc(center=(1.0, 2.0, 3.0))
    assert np.allclose(disc.points[:, 2], 3.0)


def test_disc_vtk_js_source() -> None:
    """Test that Disc generates vtk.js source code with correct parameters."""
    disc = Disc(inner=0.1, outer=0.8, r_res=2, c_res=12)
    js_source = disc.generate_vtk_js_source(0)
    assert "0.1" in js_source
    assert "0.8" in js_source
    assert "2" in js_source
    assert "12" in js_source
    assert "vtkPolyData" in js_source


def test_disc_mapper_setup() -> None:
    """Test that Disc mapper uses setInputData."""
    disc = Disc()
    mapper_code = disc.get_mapper_setup(0)
    assert "setInputData" in mapper_code
    assert "source0" in mapper_code


def test_arrow_creation() -> None:
    """Test arrow primitive creation with defaults."""
    arrow = Arrow()
    assert isinstance(arrow, PolyData)
    assert arrow.n_points > 0
    assert arrow.points.shape[1] == 3


def test_arrow_custom_parameters() -> None:
    """Test arrow with custom start, direction, and dimensions."""
    arrow = Arrow(
        start=(1.0, 2.0, 3.0),
        direction=(0.0, 1.0, 0.0),
        tip_length=0.3,
        tip_radius=0.15,
        shaft_radius=0.06,
    )
    assert isinstance(arrow, PolyData)
    assert arrow.n_points > 0


def test_arrow_scale() -> None:
    """Test arrow scale parameter."""
    arrow = Arrow(scale=2.0)
    assert isinstance(arrow, PolyData)


def test_arrow_zero_direction_raises() -> None:
    """Test that a zero direction vector raises ValueError."""
    with pytest.raises(ValueError, match="non-zero"):
        Arrow(direction=(0.0, 0.0, 0.0))


def test_arrow_vtk_js_source() -> None:
    """Test that the vtk.js source code is generated correctly."""
    arrow = Arrow(
        tip_length=0.25,
        tip_radius=0.1,
        tip_resolution=20,
        shaft_radius=0.05,
        shaft_resolution=20,
    )
    js = arrow.generate_vtk_js_source(0)
    assert "vtkArrowSource" in js
    assert "tipLength" in js
    assert "shaftRadius" in js


def test_arrow_mapper_setup() -> None:
    """Test that the mapper setup code references the correct output port."""
    arrow = Arrow()
    setup = arrow.get_mapper_setup(0)
    assert "getOutputPort" in setup


def test_cone_creation() -> None:
    """Test cone primitive creation with default parameters."""
    cone = Cone()

    assert isinstance(cone, PolyData)
    assert cone.n_points > 0
    assert cone.points.shape[1] == 3


def test_cone_custom_parameters() -> None:
    """Test cone with custom parameters."""
    cone = Cone(center=(1, 2, 3), direction=(0, 1, 0), height=2.0, radius=1.0, resolution=8)

    assert cone.n_points > 0
    # Apex should be at center + direction * height/2
    apex = cone.points[0]
    assert np.allclose(apex, [1.0, 3.0, 3.0], atol=1e-5)


def test_cone_resolution() -> None:
    """Test that resolution controls the number of base facets."""
    cone6 = Cone(resolution=6)
    cone12 = Cone(resolution=12)

    # With capping=True: apex + resolution base points + base center
    assert cone6.n_points == 6 + 2
    assert cone12.n_points == 12 + 2


def test_cone_no_capping() -> None:
    """Test cone without capping has no base center point."""
    cone = Cone(resolution=6, capping=False)

    # apex + resolution base points (no base center)
    assert cone.n_points == 6 + 1


def test_cone_vtk_js_source() -> None:
    """Test that Cone generates valid vtk.js source code."""
    cone = Cone(center=(0, 0, 0), direction=(1, 0, 0), height=2.0, radius=0.5, resolution=6)
    js_source = cone.generate_vtk_js_source(0)

    assert "vtkConeSource" in js_source
    assert "2.0" in js_source
    assert "0.5" in js_source
    assert "6" in js_source
    assert "true" in js_source  # capping


def test_cone_vtk_js_source_no_capping() -> None:
    """Test that capping=False is reflected in vtk.js source."""
    cone = Cone(capping=False)
    js_source = cone.generate_vtk_js_source(0)

    assert "false" in js_source


def test_cone_mapper_setup() -> None:
    """Test that Cone mapper uses setInputConnection."""
    cone = Cone()
    mapper_code = cone.get_mapper_setup(0)

    assert "setInputConnection" in mapper_code
    assert "source0" in mapper_code


def test_line_creation() -> None:
    """Test default Line creation."""
    line = Line()

    assert isinstance(line, PolyData)
    assert line.n_points == 2


def test_line_custom_points() -> None:
    """Test Line with custom start and end points."""
    line = Line(pointa=(0, 0, 0), pointb=(2, 0, 0))

    assert np.allclose(line.points[0], [0, 0, 0])
    assert np.allclose(line.points[-1], [2, 0, 0])


def test_line_resolution() -> None:
    """Test Line with custom resolution produces correct number of points."""
    line = Line(resolution=5)

    assert line.n_points == 6  # resolution + 1


def test_line_invalid_resolution() -> None:
    """Test that resolution < 1 raises ValueError."""
    with pytest.raises(ValueError, match="resolution must be >= 1"):
        Line(resolution=0)
    with pytest.raises(ValueError, match="resolution must be >= 1"):
        Line(resolution=-1)


def test_line_vtk_js_source() -> None:
    """Test that Line generates correct vtk.js source code."""
    line = Line(pointa=(0, 0, 0), pointb=(1, 0, 0), resolution=3)
    js_source = line.generate_vtk_js_source(0)

    assert "vtkLineSource" in js_source
    assert "0.0" in js_source
    assert "1.0" in js_source
    assert "3" in js_source
    assert "source0" in js_source


def test_line_mapper_setup() -> None:
    """Test that Line mapper uses setInputConnection."""
    line = Line()
    mapper_code = line.get_mapper_setup(0)
    assert "setInputConnection" in mapper_code
    assert "source0" in mapper_code


def test_plane_creation() -> None:
    """Test plane primitive creation with default parameters."""
    plane = Plane()

    assert isinstance(plane, PolyData)
    assert plane.n_points == 121  # (10+1) * (10+1)
    assert plane.n_faces == 100  # 10 * 10
    assert plane.points.shape[1] == 3


def test_plane_custom_resolution() -> None:
    """Test plane with custom resolution."""
    plane = Plane(i_resolution=5, j_resolution=4)

    assert plane.n_points == 30  # (5+1) * (4+1)
    assert plane.n_faces == 20  # 5 * 4


def test_plane_center() -> None:
    """Test plane is centered at the specified center."""
    plane = Plane(center=(1.0, 2.0, 0.0))
    centroid = np.mean(plane.points, axis=0)
    assert np.allclose(centroid, [1.0, 2.0, 0.0], atol=1e-10)


def test_plane_size() -> None:
    """Test plane size in i and j directions."""
    plane = Plane(center=(0.0, 0.0, 0.0), direction=(0.0, 0.0, 1.0), i_size=2.0, j_size=4.0)
    x_extent = np.max(plane.points[:, 0]) - np.min(plane.points[:, 0])
    y_extent = np.max(plane.points[:, 1]) - np.min(plane.points[:, 1])
    assert np.isclose(x_extent, 2.0, atol=1e-10)
    assert np.isclose(y_extent, 4.0, atol=1e-10)


def test_plane_default_in_xy_plane() -> None:
    """Test that the default plane lies in the XY plane (direction=(0,0,1))."""
    plane = Plane()
    assert np.allclose(plane.points[:, 2], 0.0, atol=1e-10)


def test_plane_vtk_js_source() -> None:
    """Test that Plane generates vtk.js source code with PlaneSource."""
    plane = Plane(i_resolution=5, j_resolution=5)
    js_source = plane.generate_vtk_js_source(0)
    assert "vtkPlaneSource" in js_source
    assert "xResolution" in js_source
    assert "5" in js_source


def test_plane_mapper_setup() -> None:
    """Test that Plane mapper uses setInputConnection."""
    plane = Plane()
    mapper_code = plane.get_mapper_setup(0)
    assert "setInputConnection" in mapper_code
    assert "source0" in mapper_code


meshio = pytest.importorskip("meshio")


def test_save_obj(tmp_path) -> None:
    """Test that save writes a valid OBJ file via meshio."""
    cube = Cube()
    out = tmp_path / "cube.obj"
    cube.save(out)
    assert out.exists()
    loaded = meshio.read(str(out))
    assert len(loaded.points) == cube.n_points
    assert sum(len(b.data) for b in loaded.cells) == cube.n_faces


def test_save_obj_vertex_coords(tmp_path) -> None:
    """Test that saved vertex coordinates match original points."""
    points = np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]])
    mesh = PolyData(points)
    out = tmp_path / "mesh.obj"
    mesh.save(out)
    loaded = meshio.read(str(out))
    assert np.allclose(loaded.points, points)


def test_save_vtk(tmp_path) -> None:
    """Test that save can write VTK format via meshio."""
    cube = Cube()
    out = tmp_path / "cube.vtk"
    cube.save(out)
    assert out.exists()
    loaded = meshio.read(str(out))
    assert len(loaded.points) == cube.n_points


def test_save_no_meshio(tmp_path, monkeypatch) -> None:
    """Test that save raises ImportError when meshio is not installed."""
    real_import = builtins.__import__

    def mock_import(name, *args, **kwargs):
        if name == "meshio":
            raise ImportError
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", mock_import)
    sphere = Sphere()
    with pytest.raises(ImportError, match="meshio is required"):
        sphere.save(tmp_path / "sphere.obj")


def test_save_string_path(tmp_path) -> None:
    """Test that save accepts a string path."""
    cube = Cube()
    out = str(tmp_path / "cube.obj")
    cube.save(out)
    assert Path(out).exists()
