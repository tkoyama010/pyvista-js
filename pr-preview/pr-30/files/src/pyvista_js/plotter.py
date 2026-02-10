"""Plotter class for pyvista-js.

The Plotter provides the main interface for creating 3D visualizations
using vtk.js in browser environments.
"""

from typing import Optional, Tuple, Union

from .rendering import get_renderer


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

    def __init__(self):
        """Initialize a new Plotter instance."""
        self._actors = []
        self._renderer = get_renderer()
        self._background_color = (0.2, 0.3, 0.4)  # Default background color

    def add_mesh(
        self,
        mesh,
        color: Optional[Union[str, Tuple[float, float, float]]] = None,
        opacity: float = 1.0,
        **kwargs,
    ):
        """Add a mesh to the plotter.

        Parameters
        ----------
        mesh : Mesh
            The mesh object to add to the scene.
        color : str or tuple, optional
            Color of the mesh. Can be a color name or RGB tuple.
        opacity : float, optional
            Opacity of the mesh, between 0 (transparent) and 1 (opaque).
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
        """
        # Add mesh to vtk.js renderer
        actor = self._renderer.add_mesh_actor(mesh, color=color, opacity=opacity)

        # Store reference
        self._actors.append(
            {"mesh": mesh, "color": color, "opacity": opacity, "actor": actor, "kwargs": kwargs}
        )

        return actor

    def show(self, container_id: str = "pyvista-container"):
        """Display the visualization.

        In browser environments, this will render the scene using vtk.js.

        Parameters
        ----------
        container_id : str, optional
            HTML element ID for the visualization container.
            Default is "pyvista-container".

        Examples
        --------
        >>> plotter = pv.Plotter()
        >>> plotter.add_mesh(pv.Sphere())
        >>> plotter.show()
        """
        # Create container if needed
        self._renderer.create_container(container_id)

        # Render the scene
        self._renderer.render()

    def clear(self):
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
    def actors(self):
        """Return the list of actors in the plotter."""
        return self._actors

    @property
    def background_color(self):
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
    def background_color(self, color):
        """Set the background color."""
        self._background_color = self._parse_color(color)
        # Update renderer's background color
        self._renderer.set_background(self._background_color)

    def _parse_color(self, color):
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
            else:
                raise ValueError(
                    f"Unknown color name: '{color}'. "
                    f"Supported colors: {', '.join(color_map.keys())}"
                )
        elif isinstance(color, (tuple, list)):
            if len(color) != 3:
                raise ValueError(f"RGB color must have 3 values, got {len(color)}")
            # Validate values are between 0 and 1
            for val in color:
                if not 0 <= val <= 1:
                    raise ValueError(f"RGB values must be between 0 and 1, got {val}")
            return tuple(color)
        else:
            raise TypeError(f"Color must be a string or RGB tuple, got {type(color)}")
