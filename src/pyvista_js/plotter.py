"""Plotter class for pyvista-js.

The Plotter provides the main interface for creating 3D visualizations
using vtk.js in browser environments.
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any

from .rendering import get_renderer

if TYPE_CHECKING:
    from .camera import Camera
    from .examples import CubeMap
    from .light import Light
    from .mesh import PolyData
    from .texture import Texture


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
        self._camera: Camera | None = None

    def add_mesh(  # noqa: PLR0913
        self,
        mesh: PolyData,
        color: str | tuple[float, float, float] | None = None,
        opacity: float = 1.0,
        pbr: bool = False,  # noqa: FBT001 FBT002
        metallic: float = 0.0,
        roughness: float = 0.5,
        texture: Texture | None = None,
        show_edges: bool = False,  # noqa: FBT001 FBT002
        edge_color: str | tuple[float, float, float] | None = None,
        style: str = "surface",
        scalars: str | None = None,
        cmap: str = "viridis",
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
        texture : Texture, optional
            Surface texture to apply to the mesh. Create one with
            :class:`~pyvista_js.Texture`. The mesh should have texture
            coordinates set (e.g., via
            :meth:`~pyvista_js.PolyData.texture_map_to_plane`) or use a
            primitive (Sphere, Cube, Cylinder) that generates them automatically.
        show_edges : bool, optional
            Show the edges of the mesh. Default is False.
        edge_color : str or tuple, optional
            Color of the edges when ``show_edges=True``. Can be a color name
            or RGB tuple. If not specified, defaults to black.
        style : str, optional
            Visualization style of the mesh. One of ``'surface'`` (default),
            ``'wireframe'``, or ``'points'``.
        scalars : str, optional
            Name of the scalar array to use for coloring. The array must exist
            in ``mesh.point_data``.
        cmap : str, optional
            Name of the colormap to use when rendering scalars. Default is 'viridis'.
            Supported colormaps: 'viridis', 'plasma', 'inferno', 'magma', 'jet',
            'rainbow', 'turbo', 'coolwarm'.
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

        Texture example:

        >>> from pyvista_js import examples
        >>> plotter = pv.Plotter()
        >>> sphere = pv.Sphere()
        >>> texture = examples.download_masonry_texture()
        >>> plotter.add_mesh(sphere, texture=texture)
        >>> plotter.show()

        Show edges:

        >>> plotter = pv.Plotter()
        >>> mesh = pv.Sphere()
        >>> plotter.add_mesh(mesh, show_edges=True, edge_color='black')
        >>> plotter.show()

        Wireframe rendering:

        >>> plotter = pv.Plotter()
        >>> mesh = pv.Cube()
        >>> plotter.add_mesh(mesh, style='wireframe')
        >>> plotter.show()

        Surface with edges:

        >>> plotter = pv.Plotter()
        >>> mesh = pv.Cube()
        >>> plotter.add_mesh(mesh, style='surface', show_edges=True)
        >>> plotter.show()

        Scalar coloring:

        >>> import pyvista_js as pv
        >>> mesh = pv.Sphere()
        >>> mesh['elevation'] = mesh.points[:, 2]
        >>> plotter = pv.Plotter()
        >>> plotter.add_mesh(mesh, scalars='elevation', cmap='viridis')
        >>> plotter.show()

        """
        # Add mesh to vtk.js renderer
        actor = self._renderer.add_mesh_actor(
            mesh,
            color=color,
            opacity=opacity,
            pbr=pbr,
            metallic=metallic,
            roughness=roughness,
            texture=texture,
            show_edges=show_edges,
            edge_color=edge_color,
            style=style,
            scalars=scalars,
            cmap=cmap,
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
                "texture": texture,
                "show_edges": show_edges,
                "edge_color": edge_color,
                "style": style,
                "scalars": scalars,
                "cmap": cmap,
                "actor": actor,
                "kwargs": kwargs,
            },
        )

        return actor

    def show(
        self,
        container_id: str | None = None,
        cpos: str
        | tuple[float, float, float]
        | tuple[
            tuple[float, float, float],
            tuple[float, float, float],
            tuple[float, float, float],
        ]
        | list[float]
        | list[tuple[float, float, float]]
        | list[list[float]]
        | None = None,
    ) -> None:
        """Display the visualization.

        In browser environments, this will render the scene using vtk.js.

        Parameters
        ----------
        container_id : str, optional
            HTML element ID for the visualization container.
            Defaults to a unique ID generated per Plotter instance to avoid
            conflicts when calling show() multiple times in the same session.
        cpos : str, tuple, or list, optional
            Camera position specification. Can be:

            - String shortcut: 'xy', 'xz', 'yz', 'yx', 'zx', 'zy', or 'iso'
            - Direction vector: 3-element tuple/list (x, y, z)
            - Full camera spec: 3-tuple/list of 3-tuples/lists:
              [(position), (focal_point), (view_up)]

        Examples
        --------
        Basic usage:

        >>> plotter = pv.Plotter()
        >>> plotter.add_mesh(pv.Sphere())
        >>> plotter.show()

        With camera position string shortcut:

        >>> plotter = pv.Plotter()
        >>> plotter.add_mesh(pv.Sphere())
        >>> plotter.show(cpos='xy')

        With direction vector:

        >>> plotter = pv.Plotter()
        >>> plotter.add_mesh(pv.Sphere())
        >>> plotter.show(cpos=(1, 0, 0))

        With full camera specification:

        >>> plotter = pv.Plotter()
        >>> plotter.add_mesh(pv.Sphere())
        >>> plotter.show(cpos=[(2.0, 5.0, 13.0), (0.0, 0.0, 0.0), (0.0, 1.0, 0.0)])

        """
        # Set camera position if provided
        if cpos is not None:
            self.camera_position = cpos

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

    def view_xy(self, negative: bool = False) -> None:  # noqa: FBT001 FBT002
        """View the XY plane.

        Look down the Z-axis, with the positive Z-axis pointing toward
        the camera.

        Parameters
        ----------
        negative : bool, optional
            Look in the negative Z direction (down the +Z axis). Default is
            False (look down the -Z axis).

        Examples
        --------
        >>> import pyvista_js as pv
        >>> plotter = pv.Plotter()
        >>> plotter.add_mesh(pv.Sphere())
        >>> plotter.view_xy()
        >>> plotter.show()

        View from the negative Z direction:

        >>> plotter = pv.Plotter()
        >>> plotter.add_mesh(pv.Cube())
        >>> plotter.view_xy(negative=True)
        >>> plotter.show()

        """
        vector = (0.0, 0.0, -1.0) if negative else (0.0, 0.0, 1.0)
        self.view_vector(vector)

    def view_xz(self, negative: bool = False) -> None:  # noqa: FBT001 FBT002
        """View the XZ plane.

        Look down the Y-axis, with the positive Y-axis pointing toward
        the camera.

        Parameters
        ----------
        negative : bool, optional
            Look in the negative Y direction (down the +Y axis). Default is
            False (look down the -Y axis).

        Examples
        --------
        >>> import pyvista_js as pv
        >>> plotter = pv.Plotter()
        >>> plotter.add_mesh(pv.Sphere())
        >>> plotter.view_xz()
        >>> plotter.show()

        View from the negative Y direction:

        >>> plotter = pv.Plotter()
        >>> plotter.add_mesh(pv.Cube())
        >>> plotter.view_xz(negative=True)
        >>> plotter.show()

        """
        vector = (0.0, -1.0, 0.0) if negative else (0.0, 1.0, 0.0)
        self.view_vector(vector, viewup=(0.0, 0.0, 1.0))

    def view_yz(self, negative: bool = False) -> None:  # noqa: FBT001 FBT002
        """View the YZ plane.

        Look down the X-axis, with the positive X-axis pointing toward
        the camera.

        Parameters
        ----------
        negative : bool, optional
            Look in the negative X direction (down the +X axis). Default is
            False (look down the -X axis).

        Examples
        --------
        >>> import pyvista_js as pv
        >>> plotter = pv.Plotter()
        >>> plotter.add_mesh(pv.Sphere())
        >>> plotter.view_yz()
        >>> plotter.show()

        View from the negative X direction:

        >>> plotter = pv.Plotter()
        >>> plotter.add_mesh(pv.Cube())
        >>> plotter.view_yz(negative=True)
        >>> plotter.show()

        """
        vector = (-1.0, 0.0, 0.0) if negative else (1.0, 0.0, 0.0)
        self.view_vector(vector)

    def view_yx(self, negative: bool = False) -> None:  # noqa: FBT001 FBT002
        """View the YX plane (inverse of XY).

        Look down the Z-axis from below, with the negative Z-axis pointing
        toward the camera.

        Parameters
        ----------
        negative : bool, optional
            Look in the negative Z direction (down the +Z axis). Default is
            False (look down the -Z axis).

        Examples
        --------
        >>> import pyvista_js as pv
        >>> plotter = pv.Plotter()
        >>> plotter.add_mesh(pv.Sphere())
        >>> plotter.view_yx()
        >>> plotter.show()

        """
        vector = (0.0, 0.0, 1.0) if negative else (0.0, 0.0, -1.0)
        self.view_vector(vector)

    def view_zx(self, negative: bool = False) -> None:  # noqa: FBT001 FBT002
        """View the ZX plane (inverse of XZ).

        Look down the Y-axis from below, with the negative Y-axis pointing
        toward the camera.

        Parameters
        ----------
        negative : bool, optional
            Look in the negative Y direction (down the +Y axis). Default is
            False (look down the -Y axis).

        Examples
        --------
        >>> import pyvista_js as pv
        >>> plotter = pv.Plotter()
        >>> plotter.add_mesh(pv.Sphere())
        >>> plotter.view_zx()
        >>> plotter.show()

        """
        vector = (0.0, 1.0, 0.0) if negative else (0.0, -1.0, 0.0)
        self.view_vector(vector, viewup=(0.0, 0.0, 1.0))

    def view_zy(self, negative: bool = False) -> None:  # noqa: FBT001 FBT002
        """View the ZY plane (inverse of YZ).

        Look down the X-axis from the left, with the negative X-axis pointing
        toward the camera.

        Parameters
        ----------
        negative : bool, optional
            Look in the negative X direction (down the +X axis). Default is
            False (look down the -X axis).

        Examples
        --------
        >>> import pyvista_js as pv
        >>> plotter = pv.Plotter()
        >>> plotter.add_mesh(pv.Sphere())
        >>> plotter.view_zy()
        >>> plotter.show()

        """
        vector = (1.0, 0.0, 0.0) if negative else (-1.0, 0.0, 0.0)
        self.view_vector(vector)

    def view_isometric(self) -> None:
        """View the scene from an isometric angle.

        The isometric view shows all three axes equally, looking from the
        (1, 1, 1) direction.

        Examples
        --------
        >>> import pyvista_js as pv
        >>> plotter = pv.Plotter()
        >>> plotter.add_mesh(pv.Cube())
        >>> plotter.view_isometric()
        >>> plotter.show()

        """
        self.view_vector((1.0, 1.0, 1.0))

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

    def add_light(self, light: Light) -> None:
        """Add a light source to the scene.

        Parameters
        ----------
        light : Light
            The :class:`~pyvista_js.light.Light` to add.

        Examples
        --------
        >>> import pyvista_js as pv
        >>> plotter = pv.Plotter()
        >>> plotter.add_mesh(pv.Sphere(), color='white')
        >>> light = pv.Light(position=(5, 5, 5), color='white', intensity=2.0)
        >>> plotter.add_light(light)
        >>> plotter.show()

        """
        self._renderer.add_light(light)

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
    def camera(self) -> Camera | None:
        """Get or set the camera for the plotter.

        Parameters
        ----------
        cam : Camera
            The camera object to use for rendering.

        Returns
        -------
        Camera or None
            The current camera, or None if not set.

        Examples
        --------
        >>> import pyvista_js as pv
        >>> plotter = pv.Plotter()
        >>> plotter.add_mesh(pv.Sphere())
        >>> camera = pv.Camera()
        >>> camera.position = (5, 5, 5)
        >>> camera.focal_point = (0, 0, 0)
        >>> plotter.camera = camera
        >>> plotter.show()

        """
        return self._camera

    @camera.setter
    def camera(self, cam: Camera) -> None:
        """Set the camera."""
        self._camera = cam
        self._renderer.camera = cam

    @property
    def camera_position(
        self,
    ) -> tuple[float, float, float] | tuple[
        tuple[float, float, float],
        tuple[float, float, float],
        tuple[float, float, float],
    ] | None:
        """Get the camera position.

        Returns
        -------
        tuple or None
            If a camera is set, returns a 3-tuple of 3-tuples:
            (position, focal_point, view_up).
            Otherwise returns None.

        Examples
        --------
        >>> import pyvista_js as pv
        >>> plotter = pv.Plotter()
        >>> plotter.camera_position = [(2.0, 5.0, 13.0), (0.0, 0.0, 0.0), (0.0, 1.0, 0.0)]
        >>> plotter.camera_position
        ((2.0, 5.0, 13.0), (0.0, 0.0, 0.0), (0.0, 1.0, 0.0))

        """
        if self._camera is not None:
            return (
                self._camera.position,
                self._camera.focal_point,
                self._camera.view_up,
            )
        return None

    @camera_position.setter
    def camera_position(
        self,
        cpos: str
        | tuple[float, float, float]
        | tuple[
            tuple[float, float, float],
            tuple[float, float, float],
            tuple[float, float, float],
        ]
        | list[float]
        | list[tuple[float, float, float]]
        | list[list[float]],
    ) -> None:
        """Set the camera position.

        Parameters
        ----------
        cpos : str, tuple, or list
            Camera position specification. Can be:

            - String shortcut: 'xy', 'xz', 'yz', 'yx', 'zx', 'zy', or 'iso'
            - Direction vector: 3-element tuple/list (x, y, z)
            - Full camera spec: 3-tuple/list of 3-tuples/lists:
              [(position), (focal_point), (view_up)]

        Examples
        --------
        Using string shortcuts:

        >>> plotter = pv.Plotter()
        >>> plotter.camera_position = 'xy'
        >>> plotter.camera_position = 'iso'

        Using direction vector:

        >>> plotter = pv.Plotter()
        >>> plotter.camera_position = (1, 0, 0)

        Using full camera specification:

        >>> plotter = pv.Plotter()
        >>> plotter.camera_position = [(2.0, 5.0, 13.0), (0.0, 0.0, 0.0), (0.0, 1.0, 0.0)]

        """
        # Handle string shortcuts
        if isinstance(cpos, str):
            cpos_lower = cpos.lower()
            if cpos_lower == "xy":
                self.view_xy()
            elif cpos_lower == "xz":
                self.view_xz()
            elif cpos_lower == "yz":
                self.view_yz()
            elif cpos_lower == "yx":
                self.view_yx()
            elif cpos_lower == "zx":
                self.view_zx()
            elif cpos_lower == "zy":
                self.view_zy()
            elif cpos_lower == "iso":
                self.view_isometric()
            else:
                msg = (
                    f"Unknown camera position string: '{cpos}'. "
                    "Supported: 'xy', 'xz', 'yz', 'yx', 'zx', 'zy', 'iso'"
                )
                raise ValueError(msg)
            return

        # Handle tuple/list input
        if isinstance(cpos, (tuple, list)):
            # Check if it's a direction vector (3 numbers)
            if (
                len(cpos) == 3
                and all(isinstance(x, (int, float)) for x in cpos)
            ):
                # Direction vector
                self.view_vector((float(cpos[0]), float(cpos[1]), float(cpos[2])))
                return

            # Check if it's full camera specification (3 tuples/lists of 3 numbers each)
            if len(cpos) == 3 and all(
                isinstance(item, (tuple, list))
                and len(item) == 3
                and all(isinstance(x, (int, float)) for x in item)
                for item in cpos
            ):
                # Full camera specification
                position = (float(cpos[0][0]), float(cpos[0][1]), float(cpos[0][2]))
                focal_point = (float(cpos[1][0]), float(cpos[1][1]), float(cpos[1][2]))
                view_up = (float(cpos[2][0]), float(cpos[2][1]), float(cpos[2][2]))

                from .camera import Camera

                camera = Camera(
                    position=position,
                    focal_point=focal_point,
                    view_up=view_up,
                )
                self.camera = camera
                return

            msg = (
                "Invalid camera position format. Expected: "
                "3-element direction vector or 3x3 camera specification"
            )
            raise ValueError(msg)

        msg = (
            f"Invalid camera position type: {type(cpos)}. "
            "Expected string, tuple, or list"
        )
        raise TypeError(msg)

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
