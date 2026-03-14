"""Light class for pyvista-js.

This module provides the Light class for adding light sources to 3D scenes.
"""

from __future__ import annotations

SCENE_LIGHT = "SceneLight"
CAMERA_LIGHT = "CameraLight"
HEADLIGHT = "Headlight"

_LIGHT_TYPES = (SCENE_LIGHT, CAMERA_LIGHT, HEADLIGHT)


class Light:
    """A light source for 3D rendering.

    Wraps ``vtk.Rendering.Core.vtkLight`` and supports three placement modes:

    - **SceneLight** - fixed in world space (default).
    - **CameraLight** - moves with the camera.
    - **Headlight** - always at the camera position, shining toward the focal point.

    Parameters
    ----------
    position : tuple of float, optional
        (x, y, z) position in world space. Default is ``(0, 0, 1)``.
    focal_point : tuple of float, optional
        (x, y, z) point the light shines toward. Default is ``(0, 0, 0)``.
    color : tuple of float or str, optional
        RGB color with values between 0 and 1, or a color name. Default is white.
    intensity : float, optional
        Brightness of the light. Default is ``1.0``.
    light_type : str, optional
        One of ``'SceneLight'``, ``'CameraLight'``, or ``'Headlight'``.
        Default is ``'SceneLight'``.
    positional : bool, optional
        If ``True``, the light acts as a spotlight using ``cone_angle`` and
        ``cone_falloff``. Default is ``False``.
    cone_angle : float, optional
        Half-angle (degrees) of the spotlight cone. Values >= 90 disable
        spot-lighting. Default is ``30.0``.
    cone_falloff : float, optional
        Exponent controlling how sharply the light falls off at the cone edge.
        Default is ``5.0``.
    attenuation_values : tuple of float, optional
        ``(constant, linear, quadratic)`` attenuation coefficients.
        Default is ``(1.0, 0.0, 0.0)``.

    Examples
    --------
    Add a white scene light:

    >>> import pyvista_js as pv
    >>> plotter = pv.Plotter()
    >>> plotter.add_mesh(pv.Sphere(), color='white')
    >>> light = pv.Light(position=(1, 1, 1), color='white', intensity=1.5)
    >>> plotter.add_light(light)
    >>> plotter.show()

    Spotlight example:

    >>> light = pv.Light(
    ...     position=(0, 5, 0),
    ...     focal_point=(0, 0, 0),
    ...     positional=True,
    ...     cone_angle=20.0,
    ... )

    """

    def __init__(  # noqa: PLR0913
        self,
        position: tuple[float, float, float] = (0.0, 0.0, 1.0),
        focal_point: tuple[float, float, float] = (0.0, 0.0, 0.0),
        color: tuple[float, float, float] | str = (1.0, 1.0, 1.0),
        intensity: float = 1.0,
        light_type: str = SCENE_LIGHT,
        positional: bool = False,  # noqa: FBT001 FBT002
        cone_angle: float = 30.0,
        cone_falloff: float = 5.0,
        attenuation_values: tuple[float, float, float] = (1.0, 0.0, 0.0),
    ) -> None:
        """Initialize a Light instance."""
        if light_type not in _LIGHT_TYPES:
            msg = f"light_type must be one of {_LIGHT_TYPES}, got '{light_type}'"
            raise ValueError(msg)

        self.position = (float(position[0]), float(position[1]), float(position[2]))
        self.focal_point = (
            float(focal_point[0]),
            float(focal_point[1]),
            float(focal_point[2]),
        )
        if isinstance(color, str):
            color = _color_name_to_rgb(color)
        self.color: tuple[float, float, float] = color
        self.intensity = float(intensity)
        self.light_type = light_type
        self.positional = bool(positional)
        self.cone_angle = float(cone_angle)
        self.cone_falloff = float(cone_falloff)
        self.attenuation_values = (
            float(attenuation_values[0]),
            float(attenuation_values[1]),
            float(attenuation_values[2]),
        )

    # ------------------------------------------------------------------
    # Convenience setters matching vtk.js / PyVista naming
    # ------------------------------------------------------------------

    def set_light_type_to_scene_light(self) -> None:
        """Set light type to SceneLight (fixed in world space)."""
        self.light_type = SCENE_LIGHT

    def set_light_type_to_camera_light(self) -> None:
        """Set light type to CameraLight (moves with the camera)."""
        self.light_type = CAMERA_LIGHT

    def set_light_type_to_headlight(self) -> None:
        """Set light type to Headlight (at camera position)."""
        self.light_type = HEADLIGHT

    # ------------------------------------------------------------------
    # JavaScript code generation
    # ------------------------------------------------------------------

    def generate_vtk_js_code(self, idx: int) -> str:
        """Generate vtk.js JavaScript code for this light.

        Parameters
        ----------
        idx : int
            Unique index used to avoid variable name collisions in JavaScript.

        Returns
        -------
        str
            JavaScript code that creates and configures the light.

        """
        px, py, pz = self.position
        fx, fy, fz = self.focal_point
        cr, cg, cb = self.color
        av0, av1, av2 = self.attenuation_values
        positional_js = "true" if self.positional else "false"

        light_type_call = {
            SCENE_LIGHT: "light{idx}.setLightTypeToSceneLight();",
            CAMERA_LIGHT: "light{idx}.setLightTypeToCameraLight();",
            HEADLIGHT: "light{idx}.setLightTypeToHeadLight();",
        }[self.light_type].format(idx=idx)

        lines = [
            f"const light{idx} = vtk.Rendering.Core.vtkLight.newInstance();",
            light_type_call,
            f"light{idx}.setPosition({px}, {py}, {pz});",
            f"light{idx}.setFocalPoint({fx}, {fy}, {fz});",
            f"light{idx}.setColor({cr}, {cg}, {cb});",
            f"light{idx}.setIntensity({self.intensity});",
            f"light{idx}.setPositional({positional_js});",
            f"light{idx}.setConeAngle({self.cone_angle});",
            f"light{idx}.setExponent({self.cone_falloff});",
            f"light{idx}.setAttenuationValues({av0}, {av1}, {av2});",
            f"renderer.addLight(light{idx});",
        ]
        return "\n".join(lines)


def _color_name_to_rgb(color_name: str) -> tuple[float, float, float]:
    """Convert a color name to an RGB tuple."""
    colors = {
        "red": (1.0, 0.0, 0.0),
        "green": (0.0, 1.0, 0.0),
        "blue": (0.0, 0.0, 1.0),
        "yellow": (1.0, 1.0, 0.0),
        "cyan": (0.0, 1.0, 1.0),
        "magenta": (1.0, 0.0, 1.0),
        "white": (1.0, 1.0, 1.0),
        "black": (0.0, 0.0, 0.0),
        "orange": (1.0, 0.647, 0.0),
        "purple": (0.5, 0.0, 0.5),
    }
    result = colors.get(color_name.lower())
    if result is None:
        msg = f"Unknown color name: '{color_name}'. Supported: {', '.join(colors)}"
        raise ValueError(msg)
    return result
