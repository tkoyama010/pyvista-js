"""Plotter class for pyvista-js.

The Plotter provides the main interface for creating 3D visualizations
using vtk.js in browser environments.
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any

from .rendering import get_renderer

if TYPE_CHECKING:
    from .examples import CubeMap
    from .mesh import Mesh


class Plotter:
    """Main plotting interface for pyvista-js.

    This class provides a PyVista-like API for creating 3D visualizations
    in the browser using vtk.js as the rendering backend.

    Examples
    --------
    >>> import pyvista_js as pv
    >>> plotter = pv.Plotter()
    >>> mesh = pv.Sphere()
    >>> plotter.add_mesh(mesh, color='red')
    >>> plotter.show()

    """

    def __init__(self) -> None:
        """Initialize a new Plotter instance."""
        self._actors: list[dict[str, object]] = []
        self._renderer = get_renderer()
        self._background_color = (1.0, 1.0, 1.0)  # Default background color
        self._container_id = f"pyvista-container-{uuid.uuid4().hex[:8]}"

    def add_mesh(  # noqa: PLR0913
        self,
        mesh: Mesh,
        color: str | tuple[float, float, float] | None = None,
        opacity: float = 1.0,
        pbr: bool = False,  # noqa: FBT001 FBT002
        metallic: float = 0.0,
        roughness: float = 0.5,
        **kwargs: object,
    ) -> dict[str, object]:
        """Add a mesh to the plotter.

        Parameters
        ----------
        mesh : Mesh
            The mesh object to add to the scene.
        color : str or tuple, optional
            Color of the mesh. Can be a color name or RGB tuple.
        opacity : float, optional
            Opacity of the mesh, between 0 (transparent) and 1 (opaque).
        pbr : bool, optional
            Enable physically based rendering (PBR). Default is False.
        metallic : float, optional
            Metallic factor for PBR, between 0 (non-metallic) and 1 (fully
            metallic). Only used when ``pbr=True``. Default is 0.0.
        roughness : float, optional
            Roughness factor for PBR, between 0 (mirror-like) and 1 (fully
            rough). Only used when ``pbr=True``. Default is 0.5.
        **kwargs
            Additional rendering options.

        Returns
        -------
        actor
            The vtk.js actor representing the mesh.

        Examples
        --------
        >>> plotter = pv.Plotter()
        >>> mesh = pv.Sphere()
        >>> plotter.add_mesh(mesh, color='red', opacity=0.8)

        PBR example:

        >>> plotter = pv.Plotter()
        >>> mesh = pv.Sphere()
        >>> plotter.add_mesh(mesh, color='white', pbr=True, metallic=0.8, roughness=0.1)

        """
        # Add mesh to vtk.js renderer
        actor = self._renderer.add_mesh_actor(
            mesh,
            color=color,
            opacity=opacity,
            pbr=pbr,
            metallic=metallic,
            roughness=roughness,
        )

        # Store reference
        self._actors.append(
            {
                "mesh": mesh,
                "color": color,
                "opacity": opacity,
                "pbr": pbr,
                "metallic": metallic,
                "roughness": roughness,
                "actor": actor,
                "kwargs": kwargs,
            },
        )

        return actor

    def show(self, container_id: str | None = None) -> None:
        """Display the visualization.

        In browser environments, this will render the scene using vtk.js.

        Parameters
        ----------
        container_id : str, optional
            HTML element ID for the visualization container.
            Defaults to a unique ID generated per Plotter instance to avoid
            conflicts when calling show() multiple times in the same session.

        Examples
        --------
        >>> plotter = pv.Plotter()
        >>> plotter.add_mesh(pv.Sphere())
        >>> plotter.show()

        """
        # Create container if needed
        self._renderer.create_container(container_id or self._container_id)

        # Render the scene
        self._renderer.render()

    def view_vector(
        self,
        vector: tuple[float, float, float],
        viewup: tuple[float, float, float] | None = None,
    ) -> None:
        """Point the camera in the direction of the given vector.

        Parameters
        ----------
        vector : tuple of float
            Direction to point the camera in, given as (vx, vy, vz).
        viewup : tuple of float, optional
            View-up vector. Defaults to (0, 1, 0).

        Examples
        --------
        >>> import pyvista_js as pv
        >>> plotter = pv.Plotter()
        >>> plotter.add_mesh(pv.Sphere())
        >>> plotter.view_vector((1, 0, 0))
        >>> plotter.show()

        View from an isometric angle:

        >>> plotter = pv.Plotter()
        >>> plotter.add_mesh(pv.Cube())
        >>> plotter.view_vector((1, 1, 1))
        >>> plotter.show()

        """
        self._renderer.view_vector(vector, viewup=viewup)

    def set_environment_texture(self, texture: str | CubeMap) -> None:
        """Set the environment texture for image-based lighting (IBL).

        Used with PBR materials to provide realistic reflections and lighting.

        Parameters
        ----------
        texture : str or CubeMap
            Either a URL string pointing to an equirectangular image, or a
            :class:`~pyvista_js.examples.CubeMap` returned by
            :func:`~pyvista_js.examples.download_sky_box_cube_map`.

        Examples
        --------
        URL string:

        >>> plotter = pv.Plotter()
        >>> plotter.add_mesh(pv.Sphere(), color='white', pbr=True, metallic=1.0, roughness=0.1)
        >>> plotter.set_environment_texture('https://example.com/env.jpg')
        >>> plotter.show()

        CubeMap:

        >>> from pyvista_js import examples
        >>> cubemap = examples.download_sky_box_cube_map()
        >>> plotter = pv.Plotter()
        >>> plotter.add_mesh(pv.Sphere(), color='white', pbr=True, metallic=1.0, roughness=0.1)
        >>> plotter.set_environment_texture(cubemap)
        >>> plotter.show()

        """
        self._renderer.set_environment_texture(texture)

    def clear(self) -> None:
        """Clear all actors from the plotter.

        Examples
        --------
        >>> plotter = pv.Plotter()
        >>> plotter.add_mesh(pv.Sphere())
        >>> plotter.clear()

        """
        self._actors = []
        self._renderer.clear()

    @property
    def actors(self) -> list[dict[str, Any]]:
        """Return the list of actors in the plotter."""
        return self._actors

    @property
    def background_color(self) -> tuple[float, float, float]:
        """Get or set the background color.

        Parameters
        ----------
        color : str or tuple
            Color name (e.g., 'white', 'black', 'red') or RGB tuple
            with values between 0 and 1 (e.g., (1.0, 1.0, 1.0) for white).

        Returns
        -------
        tuple
            RGB color tuple with values between 0 and 1.

        Examples
        --------
        >>> plotter = pv.Plotter()
        >>> plotter.background_color = 'white'
        >>> plotter.background_color
        (1.0, 1.0, 1.0)
        >>> plotter.background_color = (0.5, 0.5, 0.5)

        """
        return self._background_color

    @background_color.setter
    def background_color(self, color: str | tuple[float, float, float]) -> None:
        """Set the background color."""
        self._background_color = self._parse_color(color)
        # Update renderer's background color
        self._renderer.set_background(self._background_color)

    def _parse_color(
        self,
        color: str | tuple[float, float, float] | list[float],
    ) -> tuple[float, float, float]:
        """Parse color input to RGB tuple.

        Parameters
        ----------
        color : str or tuple
            Color as string name or RGB tuple.

        Returns
        -------
        tuple
            RGB color tuple with values between 0 and 1.

        """
        # Common color names
        color_map = {
            "white": (1.0, 1.0, 1.0),
            "black": (0.0, 0.0, 0.0),
            "red": (1.0, 0.0, 0.0),
            "green": (0.0, 1.0, 0.0),
            "blue": (0.0, 0.0, 1.0),
            "yellow": (1.0, 1.0, 0.0),
            "cyan": (0.0, 1.0, 1.0),
            "magenta": (1.0, 0.0, 1.0),
            "gray": (0.5, 0.5, 0.5),
            "grey": (0.5, 0.5, 0.5),
            "orange": (1.0, 0.647, 0.0),
            "purple": (0.5, 0.0, 0.5),
            "pink": (1.0, 0.753, 0.796),
            "brown": (0.647, 0.165, 0.165),
        }

        if isinstance(color, str):
            color_lower = color.lower()
            if color_lower in color_map:
                return color_map[color_lower]
            msg = f"Unknown color name: '{color}'. Supported colors: {', '.join(color_map.keys())}"
            raise ValueError(
                msg,
            )
        if isinstance(color, (tuple, list)):
            rgb_size = 3
            if len(color) != rgb_size:
                msg = f"RGB color must have 3 values, got {len(color)}"
                raise ValueError(msg)
            # Validate values are between 0 and 1
            for val in color:
                if not 0 <= val <= 1:
                    msg = f"RGB values must be between 0 and 1, got {val}"
                    raise ValueError(msg)
            return (color[0], color[1], color[2])
        msg = f"Color must be a string or RGB tuple, got {type(color)}"  # type: ignore[unreachable]
        raise TypeError(msg)
