"""pyvista-js: PyVista-like API for vtk.js

This package provides a familiar PyVista interface for 3D visualization
in browser environments using vtk.js as the rendering backend.
"""

__version__ = "0.1.0"
__author__ = "Tetsuo Koyama"
__license__ = "BSD-3-Clause"

from .plotter import Plotter
from .mesh import Mesh, Sphere, Cube, Cylinder

__all__ = [
    "__version__",
    "Plotter",
    "Mesh",
    "Sphere",
    "Cube",
    "Cylinder",
]
