"""Type definitions for pyvista-js viewer configuration.

This module provides Python type definitions that mirror the TypeScript interfaces
defined in globals.d.ts. These types can be used to create configuration objects
that are compatible with both server-side (Jinja2) and WASM-based rendering.

The types are designed to be compatible with Pydantic models for OpenAPI generation.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from typing import NotRequired


class RGBColor(TypedDict):
    """RGB color representation with values in range [0, 1]."""

    r: float
    g: float
    b: float


class Vector3(TypedDict):
    """3D point or vector."""

    x: float
    y: float
    z: float


class CameraConfig(TypedDict, total=False):
    """Camera configuration."""

    position: Vector3
    focalPoint: Vector3
    viewUp: Vector3
    viewAngle: float
    parallelProjection: bool


class LightConfig(TypedDict, total=False):
    """Light configuration."""

    position: Vector3
    focalPoint: Vector3
    intensity: float
    color: RGBColor


class ActorConfig(TypedDict, total=False):
    """Actor (mesh) configuration."""

    sourceCode: str  # Required, but TypedDict doesn't support mixing required/optional well
    mapperClass: str
    mapperSetup: str
    color: RGBColor
    opacity: float
    showEdges: bool
    edgeColor: RGBColor
    style: str  # "surface" | "wireframe" | "points"
    smoothShading: bool
    pbr: bool
    metallic: float
    roughness: float
    textureCode: str
    normalsCode: str
    scalarCode: str


class TextConfig(TypedDict, total=False):
    """Text actor configuration."""

    text: str  # Required
    position: Vector3
    fontSize: float
    color: RGBColor


class ScalarBarConfig(TypedDict, total=False):
    """Scalar bar configuration."""

    title: str
    numberOfLabels: int
    automated: bool


class EnvironmentConfig(TypedDict, total=False):
    """Environment texture configuration."""

    textureUrl: str


class AxesConfig(TypedDict, total=False):
    """Axes configuration."""

    enabled: bool  # Required
    xAxisColor: RGBColor
    yAxisColor: RGBColor
    zAxisColor: RGBColor


class ViewerConfig(TypedDict, total=False):
    """Main viewer configuration object.

    This is the primary interface for initializing a pyvista-js viewer.
    It can be provided either through:
    - Server-side: Jinja2 template generates JS code that creates this object
    - WASM-side: JavaScript code directly creates and passes this object
    """

    containerId: str  # Required
    backgroundColor: RGBColor
    width: float
    height: float
    actors: list[ActorConfig]
    lights: list[LightConfig]
    camera: CameraConfig
    textActors: list[TextConfig]
    scalarBar: ScalarBarConfig
    environment: EnvironmentConfig
    axes: AxesConfig
    vtkjsCdnUrl: str


def color_tuple_to_rgb(color: tuple[float, float, float]) -> RGBColor:
    """Convert a color tuple (r, g, b) to RGBColor dict.

    Parameters
    ----------
    color : tuple of float
        RGB color as (r, g, b) with values in range [0, 1].

    Returns
    -------
    RGBColor
        Color as a dictionary with keys 'r', 'g', 'b'.

    """
    return {"r": color[0], "g": color[1], "b": color[2]}


def vector_tuple_to_vector3(vec: tuple[float, float, float]) -> Vector3:
    """Convert a vector tuple (x, y, z) to Vector3 dict.

    Parameters
    ----------
    vec : tuple of float
        3D vector as (x, y, z).

    Returns
    -------
    Vector3
        Vector as a dictionary with keys 'x', 'y', 'z'.

    """
    return {"x": vec[0], "y": vec[1], "z": vec[2]}
