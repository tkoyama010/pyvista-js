"""Plotter class for pyvista-js.

The Plotter provides the main interface for creating 3D visualizations
using vtk.js in browser environments.
"""

from typing import Optional, Tuple, Union
import numpy as np

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
        
    def add_mesh(
        self,
        mesh,
        color: Optional[Union[str, Tuple[float, float, float]]] = None,
        opacity: float = 1.0,
        **kwargs
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
        self._actors.append({
            'mesh': mesh,
            'color': color,
            'opacity': opacity,
            'actor': actor,
            'kwargs': kwargs
        })
        
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
