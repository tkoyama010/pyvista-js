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
from .mesh import (
    Arrow,
    Circle,
    Cone,
    Cube,
    Cylinder,
    Disc,
    Line,
    Plane,
    PointData,
    PolyData,
    Sphere,
)
from .plotter import Plotter
from .readers import OBJReader, PLYReader, PolyDataReader, STLReader
from .texture import Texture

# MCP server (optional)
try:
    from .mcp_server import MCPServer

    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    MCPServer = None  # type: ignore[assignment,misc]

# Streamlit integration (optional)
try:
    from .streamlit_integration import pyvista_chart

    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False
    pyvista_chart = None  # type: ignore[assignment]

# Build __all__ list dynamically
__all__ = [
    "Arrow",
    "Camera",
    "Circle",
    "Cone",
    "Cube",
    "Cylinder",
    "Disc",
    "Light",
    "Line",
    "OBJReader",
    "PLYReader",
    "Plane",
    "Plotter",
    "PointData",
    "PolyData",
    "PolyDataReader",
    "STLReader",
    "Sphere",
    "Texture",
    "__version__",
    "examples",
]

if STREAMLIT_AVAILABLE:
    __all__ += ["pyvista_chart"]

if MCP_AVAILABLE:
    __all__ += ["MCPServer"]
