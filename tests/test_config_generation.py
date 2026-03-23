"""Test config object generation for dual-mode support."""

import json

from pyvista_js import Sphere
from pyvista_js.rendering import MockRenderer


def test_generate_config_object_basic() -> None:
    """Test basic config object generation."""
    renderer = MockRenderer()
    mesh = Sphere()
    renderer.add_mesh_actor(mesh, color="red", opacity=0.8)

    config = renderer.generate_config_object()

    assert "containerId" in config
    assert config["containerId"] == "pyvista-container"
    assert "backgroundColor" in config
    assert "actors" in config
    assert len(config["actors"]) == 1  # type: ignore[arg-type]


def test_generate_config_object_actor_properties() -> None:
    """Test that actor properties are correctly included in config."""
    renderer = MockRenderer()
    mesh = Sphere()
    renderer.add_mesh_actor(
        mesh, color=(1.0, 0.0, 0.0), opacity=0.8, style="wireframe", show_edges=True
    )

    config = renderer.generate_config_object()
    actors = config["actors"]
    assert isinstance(actors, list)
    assert len(actors) == 1

    actor = actors[0]
    assert "sourceCode" in actor
    assert "color" in actor
    assert actor["color"] == {"r": 1.0, "g": 0.0, "b": 0.0}  # type: ignore[comparison-overlap]
    assert actor["opacity"] == 0.8  # type: ignore[comparison-overlap]
    assert actor["style"] == "wireframe"  # type: ignore[comparison-overlap]
    assert actor["showEdges"] is True  # type: ignore[comparison-overlap]


def test_generate_config_object_multiple_actors() -> None:
    """Test config generation with multiple actors."""
    renderer = MockRenderer()

    sphere = Sphere(center=(0, 0, 0))
    renderer.add_mesh_actor(sphere, color="red")

    cube_points = [
        [0, 0, 0],
        [1, 0, 0],
        [1, 1, 0],
        [0, 1, 0],
        [0, 0, 1],
        [1, 0, 1],
        [1, 1, 1],
        [0, 1, 1],
    ]
    cube_faces = [
        [4, 0, 1, 2, 3],
        [4, 4, 5, 6, 7],
        [4, 0, 1, 5, 4],
        [4, 2, 3, 7, 6],
        [4, 0, 3, 7, 4],
        [4, 1, 2, 6, 5],
    ]
    from pyvista_js import PolyData

    cube = PolyData(cube_points, cube_faces)
    renderer.add_mesh_actor(cube, color="blue")

    config = renderer.generate_config_object()
    actors = config["actors"]
    assert isinstance(actors, list)
    assert len(actors) == 2


def test_generate_config_object_pbr_properties() -> None:
    """Test PBR properties in config generation."""
    renderer = MockRenderer()
    mesh = Sphere()
    renderer.add_mesh_actor(mesh, color="red", pbr=True, metallic=0.8, roughness=0.2)

    config = renderer.generate_config_object()
    actors = config["actors"]
    assert isinstance(actors, list)
    actor = actors[0]

    assert actor["pbr"] is True  # type: ignore[comparison-overlap]
    assert actor["metallic"] == 0.8  # type: ignore[comparison-overlap]
    assert actor["roughness"] == 0.2  # type: ignore[comparison-overlap]


def test_generate_config_object_camera() -> None:
    """Test camera configuration in config object."""
    from pyvista_js.camera import Camera

    renderer = MockRenderer()
    mesh = Sphere()
    renderer.add_mesh_actor(mesh)

    camera = Camera()
    camera.position = (1.0, 2.0, 3.0)
    camera.focal_point = (0.0, 0.0, 0.0)
    camera.view_up = (0.0, 1.0, 0.0)
    camera.view_angle = 30.0
    renderer.camera = camera

    config = renderer.generate_config_object()

    assert "camera" in config
    camera_config = config["camera"]
    assert isinstance(camera_config, dict)
    assert camera_config["position"] == {"x": 1.0, "y": 2.0, "z": 3.0}  # type: ignore[comparison-overlap]
    assert camera_config["focalPoint"] == {"x": 0.0, "y": 0.0, "z": 0.0}  # type: ignore[comparison-overlap]
    assert camera_config["viewUp"] == {"x": 0.0, "y": 1.0, "z": 0.0}  # type: ignore[comparison-overlap]
    assert camera_config["viewAngle"] == 30.0  # type: ignore[comparison-overlap]


def test_generate_config_object_lights() -> None:
    """Test light configuration in config object."""
    from pyvista_js.light import Light

    renderer = MockRenderer(lighting=None)
    mesh = Sphere()
    renderer.add_mesh_actor(mesh)

    light = Light(position=(1, 1, 1), focal_point=(0, 0, 0), intensity=0.8)
    renderer.add_light(light)

    config = renderer.generate_config_object()

    assert "lights" in config
    lights = config["lights"]
    assert isinstance(lights, list)
    assert len(lights) == 1

    light_config = lights[0]
    assert light_config["position"] == {"x": 1.0, "y": 1.0, "z": 1.0}  # type: ignore[comparison-overlap]
    assert light_config["focalPoint"] == {"x": 0.0, "y": 0.0, "z": 0.0}  # type: ignore[comparison-overlap]
    assert light_config["intensity"] == 0.8  # type: ignore[comparison-overlap]


def test_generate_config_object_json_serializable() -> None:
    """Test that config object can be serialized to JSON."""
    renderer = MockRenderer()
    mesh = Sphere()
    renderer.add_mesh_actor(mesh, color="red", opacity=0.8)

    config = renderer.generate_config_object()

    # This should not raise an exception
    json_str = json.dumps(config)
    assert json_str is not None
    assert len(json_str) > 0

    # Verify we can deserialize it back
    config_back = json.loads(json_str)
    assert config_back["containerId"] == "pyvista-container"


def test_config_types_color_conversion() -> None:
    """Test color tuple to RGBColor conversion."""
    from pyvista_js.config_types import color_tuple_to_rgb

    color = (1.0, 0.5, 0.25)
    rgb = color_tuple_to_rgb(color)

    assert rgb == {"r": 1.0, "g": 0.5, "b": 0.25}


def test_config_types_vector_conversion() -> None:
    """Test vector tuple to Vector3 conversion."""
    from pyvista_js.config_types import vector_tuple_to_vector3

    vec = (1.0, 2.0, 3.0)
    v3 = vector_tuple_to_vector3(vec)

    assert v3 == {"x": 1.0, "y": 2.0, "z": 3.0}
