"""Test mesh creation and properties."""

import webbrowser

import numpy as np
import pytest

from pyvista_js import Circle, Cube, Cylinder, Mesh, PolyData, Sphere


def test_mesh_creation() -> None:
    """Test basic mesh creation."""
    points = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]])
    mesh = PolyData(points)

    assert mesh.n_points == 3
    assert np.array_equal(mesh.points, points)


def test_mesh_deprecated() -> None:
    """Test that Mesh emits a DeprecationWarning."""
    points = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]])
    with pytest.warns(DeprecationWarning, match="Mesh is deprecated"):
        mesh = Mesh(points)
    assert isinstance(mesh, PolyData)
    assert mesh.n_points == 3


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

    assert cube.n_points == 8
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


def test_save_obj(tmp_path) -> None:
    """Test that save writes a valid OBJ file."""
    cube = Cube()
    out = tmp_path / "cube.obj"
    cube.save(out)
    assert out.exists()
    content = out.read_text()
    lines = content.splitlines()
    v_lines = [l for l in lines if l.startswith("v ")]
    f_lines = [l for l in lines if l.startswith("f ")]
    assert len(v_lines) == cube.n_points
    assert len(f_lines) == cube.n_faces


def test_save_obj_indices_one_based(tmp_path) -> None:
    """Test that OBJ face indices are 1-based as required by the format."""
    cube = Cube()
    out = tmp_path / "cube.obj"
    cube.save(out)
    content = out.read_text()
    for line in content.splitlines():
        if line.startswith("f "):
            indices = [int(x) for x in line.split()[1:]]
            assert all(i >= 1 for i in indices)


def test_save_obj_vertex_coords(tmp_path) -> None:
    """Test that saved vertex coordinates match original points."""
    points = np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]])
    mesh = PolyData(points)
    out = tmp_path / "mesh.obj"
    mesh.save(out)
    content = out.read_text()
    v_lines = [l for l in content.splitlines() if l.startswith("v ")]
    assert len(v_lines) == 3
    for i, line in enumerate(v_lines):
        parts = line.split()
        assert float(parts[1]) == points[i, 0]
        assert float(parts[2]) == points[i, 1]
        assert float(parts[3]) == points[i, 2]


def test_save_unsupported_extension(tmp_path) -> None:
    """Test that save raises ValueError for unsupported extensions."""
    sphere = Sphere()
    with pytest.raises(ValueError, match="Unsupported file format"):
        sphere.save(tmp_path / "sphere.stl")


def test_save_string_path(tmp_path) -> None:
    """Test that save accepts a string path."""
    cube = Cube()
    out = str(tmp_path / "cube.obj")
    cube.save(out)
    from pathlib import Path
    assert Path(out).exists()
