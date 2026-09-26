"""Test vtk.js rendering backend."""

import importlib.util
import json
import logging
import re
import sys
import types
from pathlib import Path

import numpy as np
import pytest

from pyvista_js import Cube, Cylinder, Plotter, PolyData, Sphere, rendering
from pyvista_js.rendering import BrowserRenderer, MockRenderer, get_renderer, scene_to_json


def test_get_renderer_returns_browser() -> None:
    """Test that get_renderer returns BrowserRenderer in standard Python env."""
    renderer = get_renderer()
    assert isinstance(renderer, BrowserRenderer)


@pytest.mark.parametrize("shell", [None, object()])
def test_ipython_needs_a_running_shell(shell, monkeypatch) -> None:
    """Test IPython counts as available only when running, not just installed."""
    ipython = types.ModuleType("IPython")
    ipython.get_ipython = lambda: shell  # type: ignore[attr-defined]
    display = types.ModuleType("IPython.display")
    display.HTML = display.Javascript = display.display = None  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "IPython", ipython)
    monkeypatch.setitem(sys.modules, "IPython.display", display)
    # a fresh copy, since reloading the module would swap classes under other tests
    spec = importlib.util.spec_from_file_location("pyvista_js._rendering_copy", rendering.__file__)
    module = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    assert module.IPYTHON_AVAILABLE is (shell is not None)


def test_mock_renderer_creation() -> None:
    """Test MockRenderer initialization."""
    renderer = MockRenderer()
    assert renderer is not None
    assert len(renderer.actors) == 0


def test_mock_add_mesh(caplog) -> None:
    """Test adding mesh to MockRenderer."""
    with caplog.at_level(logging.INFO):
        renderer = MockRenderer()
        mesh = Sphere()

        actor = renderer.add_mesh_actor(mesh, color="red", opacity=0.8)

        assert len(renderer.actors) == 1
        assert actor["color"] == "red"
        assert actor["opacity"] == 0.8

        assert "Added mesh with" in caplog.text


def test_mock_render(caplog) -> None:
    """Test MockRenderer render method."""
    with caplog.at_level(logging.INFO):
        renderer = MockRenderer()
        renderer.add_mesh_actor(Sphere())

        renderer.render()

        assert "Rendering 1 actors" in caplog.text


def test_mock_clear(caplog) -> None:
    """Test MockRenderer clear method."""
    with caplog.at_level(logging.INFO):
        renderer = MockRenderer()
        renderer.add_mesh_actor(Sphere())
        renderer.add_mesh_actor(Sphere())

        assert len(renderer.actors) == 2

        renderer.clear()

        assert len(renderer.actors) == 0
        assert "Cleared all actors" in caplog.text


def test_mock_create_container(caplog) -> None:
    """Test MockRenderer container creation."""
    with caplog.at_level(logging.INFO):
        renderer = MockRenderer()

        container = renderer.create_container("test-container")

        assert container is None
        assert "Created container 'test-container'" in caplog.text


@pytest.mark.parametrize(
    ("mesh_factory", "expected_n_points"),
    [
        (
            lambda: Sphere(radius=2.0, center=(1, 2, 3), theta_resolution=40, phi_resolution=50),
            2 + 40 * (50 - 2),
        ),
        (
            lambda: Cube(center=(1, 1, 1), x_length=2.0, y_length=3.0, z_length=4.0),
            24,
        ),
        (
            lambda: Cylinder(center=(0, 0, 0), radius=1.5, height=3.0, resolution=50),
            4 * 50,
        ),
    ],
)
def test_mesh_type_rendering(mesh_factory, expected_n_points) -> None:
    """Test that different mesh types render correctly."""
    renderer = MockRenderer()
    mesh = mesh_factory()

    actor = renderer.add_mesh_actor(mesh, color=(1, 0, 0), opacity=0.9)

    assert actor["mesh"] is mesh
    assert isinstance(mesh, PolyData)
    assert mesh.n_points == expected_n_points


def test_multiple_mesh_types_rendering() -> None:
    """Test rendering multiple different mesh types together."""
    renderer = MockRenderer()

    sphere = Sphere(radius=1.0, center=(0, 0, 0))
    cube = Cube(center=(3, 0, 0), x_length=1.5)
    cylinder = Cylinder(center=(6, 0, 0), radius=0.5, height=2.0)

    renderer.add_mesh_actor(sphere, color=(1, 0, 0))
    renderer.add_mesh_actor(cube, color=(0, 1, 0))
    renderer.add_mesh_actor(cylinder, color=(0, 0, 1))

    assert len(renderer.actors) == 3
    assert all(isinstance(actor["mesh"], PolyData) for actor in renderer.actors)


@pytest.mark.parametrize(
    ("mesh_factory", "vtk_source_name"),
    [
        (lambda: Sphere(radius=1.0), "vtkSphereSource"),
        (lambda: Cube(x_length=2.0), "vtkCubeSource"),
        (lambda: Cylinder(radius=0.5, height=2.0), "vtkCylinderSource"),
    ],
)
def test_html_generation_mesh_sources(mesh_factory, vtk_source_name, monkeypatch) -> None:
    """Test that HTML generation includes correct vtk.js source types."""
    # Mock IPython availability
    monkeypatch.setattr(rendering, "IPYTHON_AVAILABLE", True)

    renderer = rendering.VTKJSRenderer()
    mesh = mesh_factory()
    renderer.add_mesh_actor(mesh, color="red")

    html = renderer._repr_html_()

    assert vtk_source_name in html
    assert "vtkMapper" in html
    assert "vtkActor" in html


def test_mesh_parameters_in_html(monkeypatch) -> None:
    """Test that mesh parameters are correctly passed to HTML/JS."""
    from tests.conftest import extract_scene_data  # noqa: PLC0415

    # Mock IPython availability
    monkeypatch.setattr(rendering, "IPYTHON_AVAILABLE", True)

    renderer = rendering.VTKJSRenderer()
    sphere = Sphere(radius=2.5, center=(1, 2, 3), theta_resolution=60)
    renderer.add_mesh_actor(sphere, color="blue")

    html = renderer._repr_html_()
    scene = extract_scene_data(html)

    # Verify parameters are in the scene data
    source = scene["actors"][0]["source"]
    assert source["radius"] == 2.5
    assert source["center"] == [1, 2, 3]
    assert source["thetaResolution"] == 60


def test_view_vector_in_html(monkeypatch) -> None:
    """Test that view_vector generates correct camera data in HTML output."""
    from tests.conftest import extract_scene_data  # noqa: PLC0415

    monkeypatch.setattr(rendering, "IPYTHON_AVAILABLE", True)

    renderer = rendering.VTKJSRenderer()
    renderer.add_mesh_actor(Sphere(), color="red")
    renderer.view_vector((1.0, 2.0, 3.0))

    html = renderer._repr_html_()
    scene = extract_scene_data(html)

    camera = scene["camera"]
    assert camera["viewVector"] == [1.0, 2.0, 3.0]
    assert camera["viewUp"] == [0.0, 1.0, 0.0]


def test_view_vector_default_viewup_in_html(monkeypatch) -> None:
    """Test that the default viewup (0, 1, 0) appears in scene data when not specified."""
    from tests.conftest import extract_scene_data  # noqa: PLC0415

    monkeypatch.setattr(rendering, "IPYTHON_AVAILABLE", True)

    renderer = rendering.VTKJSRenderer()
    renderer.add_mesh_actor(Sphere())
    renderer.view_vector((0.0, 0.0, 1.0))

    html = renderer._repr_html_()
    scene = extract_scene_data(html)

    assert scene["camera"]["viewUp"] == [0.0, 1.0, 0.0]


def test_view_vector_custom_viewup_in_html(monkeypatch) -> None:
    """Test that a custom viewup appears correctly in scene data."""
    from tests.conftest import extract_scene_data  # noqa: PLC0415

    monkeypatch.setattr(rendering, "IPYTHON_AVAILABLE", True)

    renderer = rendering.VTKJSRenderer()
    renderer.add_mesh_actor(Sphere())
    renderer.view_vector((1.0, 0.0, 0.0), viewup=(0.0, 0.0, 1.0))

    html = renderer._repr_html_()
    scene = extract_scene_data(html)

    assert scene["camera"]["viewVector"] == [1.0, 0.0, 0.0]
    assert scene["camera"]["viewUp"] == [0.0, 0.0, 1.0]


def test_no_view_vector_no_camera_code(monkeypatch) -> None:
    """Test that no camera data is generated when view_vector is not called."""
    from tests.conftest import extract_scene_data  # noqa: PLC0415

    monkeypatch.setattr(rendering, "IPYTHON_AVAILABLE", True)

    renderer = rendering.VTKJSRenderer()
    renderer.add_mesh_actor(Sphere(), color="blue")

    html = renderer._repr_html_()
    scene = extract_scene_data(html)

    assert scene["camera"] is None


def test_mock_renderer_view_vector(caplog) -> None:
    """Test that MockRenderer.view_vector logs the call."""
    with caplog.at_level(logging.INFO):
        renderer = MockRenderer()
        renderer.view_vector((1.0, 0.0, 0.0))

        assert "Set view vector" in caplog.text
        assert "(1.0, 0.0, 0.0)" in caplog.text


def test_mock_renderer_view_vector_with_viewup(caplog) -> None:
    """Test that MockRenderer.view_vector logs vector and viewup."""
    with caplog.at_level(logging.INFO):
        renderer = MockRenderer()
        renderer.view_vector((0.0, 1.0, 0.0), viewup=(0.0, 0.0, 1.0))

        assert "Set view vector" in caplog.text


def test_multiple_meshes_unique_variables(monkeypatch) -> None:
    """Test that multiple meshes produce unique actor entries in scene data."""
    from tests.conftest import extract_scene_data  # noqa: PLC0415

    # Mock IPython availability
    monkeypatch.setattr(rendering, "IPYTHON_AVAILABLE", True)

    renderer = rendering.VTKJSRenderer()
    mesh1 = Sphere()
    mesh2 = Cube()
    renderer.add_mesh_actor(mesh1, color="red", opacity=0.8)
    renderer.add_mesh_actor(mesh2, color="blue", opacity=0.8)

    html = renderer._repr_html_()
    scene = extract_scene_data(html)

    # Verify two actors exist in scene data
    assert len(scene["actors"]) == 2
    assert scene["actors"][0]["source"]["type"] == "sphere"
    assert scene["actors"][1]["source"]["type"] == "cube"


def test_generate_standalone_html(monkeypatch) -> None:
    """Test that generate_standalone_html produces a complete HTML page with scene data."""
    from tests.conftest import extract_scene_data  # noqa: PLC0415

    monkeypatch.setattr(rendering, "IPYTHON_AVAILABLE", True)

    renderer = rendering.VTKJSRenderer()
    renderer.add_mesh_actor(Sphere(), color="red")

    html = renderer.generate_standalone_html()

    assert "<!DOCTYPE html>" in html
    assert 'id="scene-data"' in html
    scene = extract_scene_data(html)
    assert len(scene["actors"]) == 1
    assert scene["actors"][0]["source"]["type"] == "sphere"


def test_generate_render_js(monkeypatch) -> None:
    """Test that _generate_render_js produces valid JavaScript with scene data."""
    from tests.conftest import extract_scene_data_from_js  # noqa: PLC0415

    monkeypatch.setattr(rendering, "IPYTHON_AVAILABLE", True)

    renderer = rendering.VTKJSRenderer()
    renderer.add_mesh_actor(Sphere(), color="red")

    js = renderer._generate_render_js()

    assert "<script>" not in js
    assert "</script>" not in js
    assert "<div" not in js
    # Scene data is embedded as JSON in the JS
    scene = extract_scene_data_from_js(js)
    assert len(scene["actors"]) == 1
    assert scene["actors"][0]["source"]["type"] == "sphere"


def test_render_with_ipython_calls_display(monkeypatch) -> None:
    """Test that VTKJSRenderer.render() calls display(Javascript(...)) in IPython mode."""
    monkeypatch.setattr(rendering, "IPYTHON_AVAILABLE", True)

    displayed = []

    def mock_display(obj) -> None:
        displayed.append(obj)

    class MockJavascript:
        def __init__(self, code: str) -> None:
            self.code = code

    monkeypatch.setattr(rendering, "display", mock_display)
    monkeypatch.setattr(rendering, "Javascript", MockJavascript)

    renderer = rendering.VTKJSRenderer()
    renderer.add_mesh_actor(Sphere(), color="blue")
    renderer.render()

    js_displays = [d for d in displayed if isinstance(d, MockJavascript)]
    assert len(js_displays) == 1
    assert "vtkRenderer" in js_displays[0].code


def test_create_container_with_ipython(monkeypatch) -> None:
    """Test that create_container returns None in IPython mode."""
    monkeypatch.setattr(rendering, "IPYTHON_AVAILABLE", True)

    renderer = rendering.VTKJSRenderer()
    result = renderer.create_container("test-id")

    assert result is None


def test_clear_with_ipython(monkeypatch) -> None:
    """Test that VTKJSRenderer.clear() clears actors in IPython mode."""
    monkeypatch.setattr(rendering, "IPYTHON_AVAILABLE", True)

    renderer = rendering.VTKJSRenderer()
    renderer.add_mesh_actor(Sphere(), color="red")
    renderer.add_mesh_actor(Cube(), color="blue")

    assert len(renderer.actors) == 2

    renderer.clear()

    assert len(renderer.actors) == 0


def test_base_html_renderer_screenshot_raises() -> None:
    """Test that _BaseHTMLRenderer.screenshot() raises NotImplementedError."""
    from pyvista_js.rendering import _BaseHTMLRenderer  # noqa: PLC0415

    renderer = _BaseHTMLRenderer()
    with pytest.raises(NotImplementedError):
        renderer.screenshot()


def test_points_actor_html_no_spheres(monkeypatch) -> None:
    """Test scene data for point cloud with render_points_as_spheres=False."""
    import numpy as np  # noqa: PLC0415

    from tests.conftest import extract_scene_data  # noqa: PLC0415

    monkeypatch.setattr(rendering, "IPYTHON_AVAILABLE", True)
    renderer = rendering.VTKJSRenderer()
    points = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
    renderer.add_points_actor(points, color="red", point_size=10.0, render_points_as_spheres=False)

    html = renderer._repr_html_()
    scene = extract_scene_data(html)

    actor = scene["actors"][0]
    assert actor["mapper"]["class"] == "vtkMapper"
    assert actor["pointSize"] == 10.0
    assert actor["renderPointsAsSpheres"] is False


def test_points_actor_html_with_spheres(monkeypatch) -> None:
    """Test scene data for point cloud with render_points_as_spheres=True."""
    import numpy as np  # noqa: PLC0415

    from tests.conftest import extract_scene_data  # noqa: PLC0415

    monkeypatch.setattr(rendering, "IPYTHON_AVAILABLE", True)
    renderer = rendering.VTKJSRenderer()
    points = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
    renderer.add_points_actor(points, color="blue", point_size=20.0, render_points_as_spheres=True)

    html = renderer._repr_html_()
    scene = extract_scene_data(html)

    actor = scene["actors"][0]
    assert actor["mapper"]["class"] == "vtkSphereMapper"
    assert actor["renderPointsAsSpheres"] is True


def test_mock_renderer_add_points_actor(caplog) -> None:
    """Test MockRenderer.add_points_actor with numpy array."""
    import logging  # noqa: PLC0415

    import numpy as np  # noqa: PLC0415

    with caplog.at_level(logging.INFO):
        renderer = MockRenderer()
        points = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
        actor = renderer.add_points_actor(points, color="red", point_size=5.0)

    assert len(renderer.actors) == 1
    assert actor["type"] == "points"
    assert actor["point_size"] == 5.0
    assert actor["render_points_as_spheres"] is False
    assert "Added point cloud" in caplog.text


def test_mock_renderer_add_points_actor_with_spheres() -> None:
    """Test MockRenderer.add_points_actor with render_points_as_spheres=True."""
    import numpy as np  # noqa: PLC0415

    renderer = MockRenderer()
    points = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]])
    actor = renderer.add_points_actor(points, color="green", render_points_as_spheres=True)

    assert actor["render_points_as_spheres"] is True
    assert actor["color"] == (0.0, 1.0, 0.0)


def test_mock_renderer_add_points_actor_polydata() -> None:
    """Test MockRenderer.add_points_actor with PolyData input."""
    import numpy as np  # noqa: PLC0415

    renderer = MockRenderer()
    points = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]])
    polydata = PolyData(points)
    actor = renderer.add_points_actor(polydata, color=(0.5, 0.5, 0.5))

    assert actor["type"] == "points"


def test_base_html_renderer_color_name_to_rgb() -> None:
    """Test _BaseHTMLRenderer._color_name_to_rgb static method."""
    from pyvista_js.rendering import _BaseHTMLRenderer  # noqa: PLC0415

    assert _BaseHTMLRenderer._color_name_to_rgb("red") == (1.0, 0.0, 0.0)
    assert _BaseHTMLRenderer._color_name_to_rgb("blue") == (0.0, 0.0, 1.0)
    assert _BaseHTMLRenderer._color_name_to_rgb("UNKNOWN") == (0.5, 0.5, 0.5)


def test_smooth_shading_default(monkeypatch) -> None:
    """Test smooth shading is enabled by default."""
    monkeypatch.setattr(rendering, "IPYTHON_AVAILABLE", True)
    renderer = rendering.VTKJSRenderer()
    renderer.add_mesh_actor(Sphere())

    html = renderer._repr_html_()
    assert "setInterpolationToGouraud" in html


def test_smooth_shading_enabled(monkeypatch) -> None:
    """Test smooth shading when explicitly enabled."""
    monkeypatch.setattr(rendering, "IPYTHON_AVAILABLE", True)
    renderer = rendering.VTKJSRenderer()
    renderer.add_mesh_actor(Sphere(), smooth_shading=True)

    html = renderer._repr_html_()
    assert "setInterpolationToGouraud" in html


def test_smooth_shading_disabled(monkeypatch) -> None:
    """Test flat shading when smooth shading is disabled."""
    from tests.conftest import extract_scene_data  # noqa: PLC0415

    monkeypatch.setattr(rendering, "IPYTHON_AVAILABLE", True)
    renderer = rendering.VTKJSRenderer()
    renderer.add_mesh_actor(Sphere(), smooth_shading=False)

    html = renderer._repr_html_()
    scene = extract_scene_data(html)

    actor = scene["actors"][0]
    assert actor["shading"] == "flat"
    assert actor["normals"]["computeCellNormals"] is True
    assert actor["normals"]["computePointNormals"] is False


def test_smooth_shading_enabled_with_texmap_recomputes_point_normals(monkeypatch) -> None:
    """Test that smooth shading with texmap recomputes point normals."""
    from tests.conftest import extract_scene_data  # noqa: PLC0415

    monkeypatch.setattr(rendering, "IPYTHON_AVAILABLE", True)
    renderer = rendering.VTKJSRenderer()
    renderer.add_mesh_actor(Sphere(), smooth_shading=True)

    html = renderer._repr_html_()
    scene = extract_scene_data(html)

    actor = scene["actors"][0]
    assert actor["shading"] == "gouraud"
    assert actor["normals"]["computePointNormals"] is True
    assert actor["normals"]["computeCellNormals"] is False


def test_smooth_shading_with_actor_index(monkeypatch) -> None:
    """Test smooth shading uses correct settings per actor."""
    from tests.conftest import extract_scene_data  # noqa: PLC0415

    monkeypatch.setattr(rendering, "IPYTHON_AVAILABLE", True)
    renderer = rendering.VTKJSRenderer()
    renderer.add_mesh_actor(Sphere(), smooth_shading=True)
    renderer.add_mesh_actor(Cube(), smooth_shading=False)

    html = renderer._repr_html_()
    scene = extract_scene_data(html)

    # First actor (Sphere): Gouraud shading + point normals recomputed
    actor0 = scene["actors"][0]
    assert actor0["shading"] == "gouraud"
    assert actor0["normals"]["computePointNormals"] is True
    assert actor0["normals"]["computeCellNormals"] is False
    # Second actor (Cube with smooth_shading=False): flat shading
    actor1 = scene["actors"][1]
    assert actor1["shading"] == "flat"


def _ts_interface_fields(name: str) -> set[str]:
    """Return the field names of a TypeScript interface in ``ts/vtk.d.ts``."""
    source = (Path(__file__).parents[1] / "ts" / "vtk.d.ts").read_text()
    match = re.search(rf"^interface {name} \{{\n(.*?)^\}}", source, re.DOTALL | re.MULTILINE)
    assert match is not None, name
    return set(re.findall(r"^  (\w+)\??:", match.group(1), re.MULTILINE))


def _colored_quad_renderer() -> BrowserRenderer:
    """Return a renderer with one quad colored by a uint8 RGB array."""
    mesh = PolyData(np.array([[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]], float), [4, 0, 1, 2, 3])
    mesh.point_data["colors"] = np.zeros((4, 3), np.uint8)
    renderer = BrowserRenderer()
    renderer.add_mesh_actor(mesh, scalars="colors")
    return renderer


def test_build_update_data_matches_ts_schema() -> None:
    """Test that update messages use exactly the fields the TypeScript side reads."""
    renderer = _colored_quad_renderer()
    points = renderer.actors[0]["mesh"].points + 1
    update = json.loads(
        scene_to_json(
            renderer.build_update_data(
                0,
                points=points,
                point_data={"colors": np.full((4, 3), 255, np.uint8), "t": np.arange(4.0)},
            ),
        ),
    )
    assert set(update) == _ts_interface_fields("ActorUpdate")
    for array in update["pointData"]:
        assert set(array) == _ts_interface_fields("PointDataArray")
    assert set(update["scalars"]) == _ts_interface_fields("ScalarsConfig")
    assert update["actor"] == renderer.actors[0]["id"]
    assert update["points"] == points.ravel().tolist()
    colors, t = update["pointData"]
    assert (colors["dataType"], colors["values"]) == ("Uint8Array", [255] * 12)
    assert (t["dataType"], t["values"]) == ("Float32Array", [0.0, 1.0, 2.0, 3.0])
    assert update["scalars"] == {
        "arrayName": "colors",
        "cmap": "viridis",
        "range": [255.0, 255.0],
        "direct": True,
    }


def test_build_update_data_updates_mesh_and_scene() -> None:
    """Test that an update is kept in the mesh, so later pages show it."""
    renderer = _colored_quad_renderer()
    update = renderer.build_update_data(0, point_data={"t": np.arange(4.0)}, scalars="t")
    assert update["scalars"]["arrayName"] == "t"  # type: ignore[index]
    source = renderer._build_scene_data()["actors"][0]  # type: ignore[index]
    assert source["scalars"]["arrayName"] == "t"
    assert [array["name"] for array in source["source"]["pointData"]] == ["colors", "t"]
    # the coloring is only re-sent when it may have changed
    assert set(renderer.build_update_data(0, point_data={"colors": np.ones((4, 3), np.uint8)})) == {
        "actor",
        "pointData",
    }


def test_generate_update_js() -> None:
    """Test that the update JavaScript calls pvjsApplyUpdate for this container."""
    renderer = _colored_quad_renderer()
    renderer.create_container("my-scene")
    js = renderer._generate_update_js(renderer.build_update_data(0))
    actor_id = renderer.actors[0]["id"]
    assert js == f'window.pvjsApplyUpdate("my-scene", {{"actor":"{actor_id}"}});\n'


def test_plotter_update_actor_requires_html_renderer() -> None:
    """Test that the mock renderer refuses in-place updates."""
    plotter = Plotter()
    plotter._renderer = MockRenderer()
    with pytest.raises(NotImplementedError, match="MockRenderer"):
        plotter.update_actor(0)


def test_plotter_update_actor_send(monkeypatch) -> None:
    """Test that update_actor sends to the notebook scene unless told not to."""
    from pyvista_js import plotter as plotter_module  # noqa: PLC0415

    shown: list[str] = []
    ipython = types.ModuleType("IPython")
    display = types.ModuleType("IPython.display")
    display.Javascript = lambda code: code  # type: ignore[attr-defined]
    display.display = shown.append  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "IPython", ipython)
    monkeypatch.setitem(sys.modules, "IPython.display", display)
    monkeypatch.setattr(plotter_module, "IPYTHON_AVAILABLE", True)
    plotter = Plotter()
    plotter._renderer = _colored_quad_renderer()
    plotter._renderer.use_ipython = True  # type: ignore[attr-defined]
    colors = {"colors": np.ones((4, 3), np.uint8)}

    plotter.update_actor(0, point_data=colors, send=False)
    assert shown == []
    plotter.update_actor(0, point_data=colors)
    assert len(shown) == 1
    assert shown[0].startswith(f'window.pvjsApplyUpdate("{plotter.container_id}",')


def test_build_update_data_actor_ids() -> None:
    """Test that updates find actors by index, and send IDs that survive clear()."""
    renderer = _colored_quad_renderer()
    renderer.add_mesh_actor(Sphere())
    scene_id = renderer._build_scene_data()["actors"][0]["id"]  # type: ignore[index]
    assert renderer.build_update_data(0)["actor"] == scene_id
    assert renderer.build_update_data(-2)["actor"] == scene_id
    with pytest.raises(IndexError):
        renderer.build_update_data(-3)
    # a mesh given by a source, not its points, cannot have its points replaced
    with pytest.raises(ValueError, match="points must replace"):
        renderer.build_update_data(1, points=renderer.actors[1]["mesh"].points)
    renderer.clear()
    renderer.add_mesh_actor(Sphere())
    assert renderer.build_update_data(0)["actor"] != scene_id


_COLORS = {"colors": np.ones((4, 3), np.uint8)}
_POINTS = np.ones((4, 3))


@pytest.mark.parametrize(
    ("kwargs", "match"),
    [
        ({"points": np.zeros((3, 3))}, "points must replace"),
        ({"points": _POINTS, "point_data": {"t": np.zeros(3)}}, "3 rows"),
        ({"point_data": {**_COLORS, "t": np.zeros((4, 2, 2))}}, "must be"),
        ({"point_data": {**_COLORS, "t": np.array(1.0)}}, "must be"),
        ({"point_data": {"colors": np.ones((4, 0))}}, "must be"),
        ({"point_data": _COLORS, "scalars": "missing"}, "not a point-data"),
        ({"points": _POINTS, "point_data": {"t": [0, 1, np.nan, 3]}}, "NaN"),
        ({"points": np.full((4, 3), np.nan), "point_data": _COLORS}, "NaN"),
        ({"points": _POINTS * 1j, "point_data": _COLORS}, "complex"),
        ({"point_data": {**_COLORS, "t": np.ones(4) * 1j}}, "complex"),
    ],
)
def test_build_update_data_invalid_changes_nothing(kwargs: dict, match: str) -> None:
    """Test that a rejected update leaves the mesh and actor as they were."""
    renderer = _colored_quad_renderer()
    actor = renderer.actors[0]
    mesh = actor["mesh"]
    points, colors = mesh.points.copy(), mesh.point_data["colors"].copy()
    with pytest.raises((ValueError, TypeError), match=match):
        renderer.build_update_data(0, **kwargs)
    np.testing.assert_array_equal(mesh.points, points)
    np.testing.assert_array_equal(mesh.point_data["colors"], colors)
    assert mesh.point_data.keys() == ["colors"]
    assert actor["scalars"] == "colors"


def test_to_scene_data_override_is_rendered() -> None:
    """Test that a mesh subclass overriding the public to_scene_data is still rendered with it."""

    class _CustomMesh(PolyData):
        def to_scene_data(self) -> dict[str, object]:
            return {"type": "sphere", "radius": 2.0}

    renderer = BrowserRenderer()
    renderer.add_mesh_actor(_CustomMesh(np.zeros((1, 3))))
    source = json.loads(scene_to_json(renderer._build_scene_data()))["actors"][0]["source"]
    assert source == {"type": "sphere", "radius": 2.0}
    # the page shows the custom source, not the mesh's points, so those cannot be replaced
    with pytest.raises(ValueError, match="points must replace"):
        renderer.build_update_data(0, points=np.ones((1, 3)))
