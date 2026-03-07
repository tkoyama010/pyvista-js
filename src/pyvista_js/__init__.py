"""pyvista-js: PyVista-like API for vtk.js.

This package provides a familiar PyVista interface for 3D visualization
in browser environments using vtk.js as the rendering backend.
"""

import sys

__version__ = "0.2.dev0"
__author__ = "Tetsuo Koyama"
__license__ = "BSD-3-Clause"

if sys.platform == "emscripten":
    try:
        import numpy  # noqa: F401
    except ImportError:
        import asyncio

        import micropip  # type: ignore[import-not-found]

        asyncio.get_event_loop().run_until_complete(micropip.install("numpy"))

from .mesh import Cube, Cylinder, Mesh, Sphere
from .plotter import Plotter

# Streamlit integration (optional)
try:
    from .streamlit_integration import pyvista_chart

    __all__ = [
        "Cube",
        "Cylinder",
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
        "Mesh",
        "Plotter",
        "Sphere",
        "__version__",
    ]
