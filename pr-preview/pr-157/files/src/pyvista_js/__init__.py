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
        import numpy as np  # noqa: F401
    except ImportError:
        import asyncio

        import micropip  # type: ignore[import-not-found]

        asyncio.get_event_loop().run_until_complete(micropip.install("numpy"))

from . import examples
from .camera import Camera
from .light import Light
from .mesh import Circle, Cone, Cube, Cylinder, Mesh, PolyData, Sphere
from .plotter import Plotter
from .readers import OBJReader, PLYReader, PolyDataReader
from .texture import Texture

# Streamlit integration (optional)
try:
    from .streamlit_integration import pyvista_chart

    __all__ = [
        "Camera",
        "Circle",
        "Cone",
        "Cube",
        "Cylinder",
        "Light",
        "Mesh",
        "OBJReader",
        "PLYReader",
        "Plotter",
        "PolyData",
        "PolyDataReader",
        "Sphere",
        "Texture",
        "__version__",
        "examples",
        "pyvista_chart",
    ]
except ImportError:
    # Streamlit not available
    __all__ = [
        "Camera",
        "Circle",
        "Cone",
        "Cube",
        "Cylinder",
        "Light",
        "Mesh",
        "OBJReader",
        "PLYReader",
        "Plotter",
        "PolyData",
        "PolyDataReader",
        "Sphere",
        "Texture",
        "__version__",
        "examples",
    ]
