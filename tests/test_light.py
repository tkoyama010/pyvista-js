"""Tests for the Light class."""

import pytest

import pyvista_js as pv
from pyvista_js.light import CAMERA_LIGHT, HEADLIGHT, SCENE_LIGHT, Light


def test_light_defaults() -> None:
    """Test Light default values."""
    light = Light()
    assert light.position == (0.0, 0.0, 1.0)
    assert light.focal_point == (0.0, 0.0, 0.0)
    assert light.color == (1.0, 1.0, 1.0)
    assert light.intensity == 1.0
    assert light.light_type == SCENE_LIGHT
    assert light.positional is False
    assert light.cone_angle == 30.0
    assert light.cone_falloff == 5.0
    assert light.attenuation_values == (1.0, 0.0, 0.0)


def test_light_custom_params() -> None:
    """Test Light with custom parameters."""
    light = Light(
        position=(1, 2, 3),
        focal_point=(0, 0, 0),
        color=(1.0, 0.0, 0.0),
        intensity=2.0,
        light_type=CAMERA_LIGHT,
        positional=True,
        cone_angle=20.0,
        cone_falloff=3.0,
        attenuation_values=(1.0, 0.1, 0.01),
    )
    assert light.position == (1.0, 2.0, 3.0)
    assert light.color == (1.0, 0.0, 0.0)
    assert light.intensity == 2.0
    assert light.light_type == CAMERA_LIGHT
    assert light.positional is True
    assert light.cone_angle == 20.0


def test_light_color_name() -> None:
    """Test Light accepts color names."""
    light = Light(color="red")
    assert light.color == (1.0, 0.0, 0.0)

    light = Light(color="blue")
    assert light.color == (0.0, 0.0, 1.0)


def test_light_color_list_to_tuple() -> None:
    """Test Light converts color lists to tuples."""
    light = Light(color=[0.886, 0.345, 0.133])
    assert isinstance(light.color, tuple), "Color should be converted to tuple"
    assert light.color == (0.886, 0.345, 0.133)

    # Test with integers
    light = Light(color=[1, 0, 0])
    assert light.color == (1.0, 0.0, 0.0)


def test_light_invalid_color_name() -> None:
    """Test Light raises on unknown color name."""
    with pytest.raises(ValueError, match="Unknown color name"):
        Light(color="notacolor")


def test_light_invalid_type() -> None:
    """Test Light raises on unknown light_type."""
    with pytest.raises(ValueError, match="light_type must be one of"):
        Light(light_type="BadType")


def test_light_type_setters() -> None:
    """Test convenience light type setters."""
    light = Light()
    light.set_light_type_to_camera_light()
    assert light.light_type == CAMERA_LIGHT

    light.set_light_type_to_headlight()
    assert light.light_type == HEADLIGHT

    light.set_light_type_to_scene_light()
    assert light.light_type == SCENE_LIGHT


def test_light_generate_vtk_js_code_scene() -> None:
    """Test JavaScript code generation for SceneLight."""
    light = Light(position=(1, 2, 3), intensity=0.5)
    code = light.generate_vtk_js_code(0)
    assert "vtkLight.newInstance()" in code
    assert "setLightTypeToSceneLight" in code
    assert "setPosition(1.0, 2.0, 3.0)" in code
    assert "setIntensity(0.5)" in code
    assert "renderer.addLight(light0)" in code


def test_light_generate_vtk_js_code_headlight() -> None:
    """Test JavaScript code generation for Headlight."""
    light = Light(light_type=HEADLIGHT)
    code = light.generate_vtk_js_code(1)
    assert "setLightTypeToHeadLight" in code
    assert "renderer.addLight(light1)" in code


def test_light_generate_vtk_js_code_spotlight() -> None:
    """Test JavaScript code generation for positional spotlight."""
    light = Light(positional=True, cone_angle=15.0, cone_falloff=2.0)
    code = light.generate_vtk_js_code(0)
    assert "setPositional(true)" in code
    assert "setConeAngle(15.0)" in code
    assert "setExponent(2.0)" in code


def test_plotter_add_light() -> None:
    """Test that add_light stores the light in the renderer."""
    plotter = pv.Plotter()
    light = pv.Light(position=(1, 1, 1), intensity=2.0)
    plotter.add_light(light)
    assert len(plotter._renderer.lights) == 1
    assert plotter._renderer.lights[0] is light


def test_plotter_add_multiple_lights() -> None:
    """Test adding multiple lights."""
    plotter = pv.Plotter()
    plotter.add_light(pv.Light(position=(1, 0, 0), color="red"))
    plotter.add_light(pv.Light(position=(-1, 0, 0), color="blue"))
    assert len(plotter._renderer.lights) == 2


def test_plotter_clear_removes_lights() -> None:
    """Test that clear() removes lights as well as actors."""
    plotter = pv.Plotter()
    plotter.add_mesh(pv.Sphere())
    plotter.add_light(pv.Light())
    plotter.clear()
    assert len(plotter._renderer.lights) == 0
    assert len(plotter.actors) == 0


def test_light_exported_from_package() -> None:
    """Test that Light is accessible from the top-level package."""
    assert hasattr(pv, "Light")
    assert pv.Light is Light
