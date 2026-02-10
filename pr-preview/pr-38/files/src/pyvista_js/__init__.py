"""pyvista-js: PyVista-like API for vtk.js.

This package provides a familiar PyVista interface for 3D visualization
in browser environments using vtk.js as the rendering backend.
"""

__version__ = "0.2.dev0"
__author__ = "Tetsuo Koyama"
__license__ = "BSD-3-Clause"

from .mesh import Cube, Cylinder, Mesh, Sphere
from .plotter import Plotter
from .rendering import ElectronRenderer

# Streamlit integration (optional)
try:
    from .streamlit_integration import pyvista_chart

    __all__ = [
        "Cube",
        "Cylinder",
        "ElectronRenderer",
        "Mesh",
        "Plotter",
        "Sphere",
        "__version__",
        "pyvista_chart",
    ]
except ImportError:
    # Streamlit not available
    __all__ = [
        "Cube",
        "Cylinder",
        "ElectronRenderer",
        "Mesh",
        "Plotter",
        "Sphere",
        "__version__",
    ]
