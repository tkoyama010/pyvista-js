"""MCP server for embodied simulation with pyvista-js.

This module provides an MCP (Model Context Protocol) server that exposes
embodied simulation capabilities for 3D visualizations:
- `see` tool: Capture the current state of the 3D scene
- `move` tool: Manipulate the camera position and scene objects

The MCP server allows LLM-based tools (like Claude Code) to interact with
pyvista-js visualizations in an intuitive, agent-friendly way.
"""

from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING, Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool

if TYPE_CHECKING:
    from .plotter import Plotter

logger = logging.getLogger(__name__)


class MCPServer:
    """MCP server for embodied simulation with pyvista-js.

    This server exposes two main tools for interacting with 3D scenes:
    - `see`: Capture the current state (camera position, objects, metadata)
    - `move`: Manipulate the camera or scene objects

    Parameters
    ----------
    plotter : Plotter
        The pyvista-js Plotter instance to interact with.
    name : str, optional
        Name of the MCP server. Default is "pyvista-js-embodied-sim".

    Examples
    --------
    >>> import pyvista_js as pv
    >>> plotter = pv.Plotter()
    >>> _ = plotter.add_mesh(pv.Sphere(), color='red')
    >>> server = pv.MCPServer(plotter)
    >>> # Start server (typically in async context)
    >>> # await server.run()  # doctest: +SKIP

    """

    def __init__(self, plotter: Plotter, name: str = "pyvista-js-embodied-sim") -> None:
        """Initialize the MCP server."""
        self.plotter = plotter
        self.server = Server(name)
        self._setup_handlers()

    def _setup_handlers(self) -> None:
        """Set up MCP tool handlers."""

        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List available MCP tools."""
            return [
                Tool(
                    name="see",
                    description=(
                        "Capture the current state of the 3D scene. "
                        "Returns camera position, focal point, view up vector, "
                        "object count, and scene metadata. Use this to understand "
                        "what's currently visible in the visualization."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "include_html": {
                                "type": "boolean",
                                "description": (
                                    "Include the full HTML rendering of the scene. "
                                    "Default is False."
                                ),
                                "default": False,
                            },
                        },
                    },
                ),
                Tool(
                    name="move",
                    description=(
                        "Manipulate the camera position or scene view. "
                        "Supports setting camera position, focal point, or using "
                        "preset views (xy, xz, yz, iso). Use this to change the "
                        "perspective or move around the 3D scene."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "position": {
                                "type": "array",
                                "items": {"type": "number"},
                                "minItems": 3,
                                "maxItems": 3,
                                "description": ("Camera position as [x, y, z]. Example: [5, 5, 5]"),
                            },
                            "focal_point": {
                                "type": "array",
                                "items": {"type": "number"},
                                "minItems": 3,
                                "maxItems": 3,
                                "description": (
                                    "Camera focal point as [x, y, z]. Example: [0, 0, 0]"
                                ),
                            },
                            "view_up": {
                                "type": "array",
                                "items": {"type": "number"},
                                "minItems": 3,
                                "maxItems": 3,
                                "description": (
                                    "Camera view up vector as [x, y, z]. Example: [0, 1, 0]"
                                ),
                            },
                            "preset": {
                                "type": "string",
                                "enum": ["xy", "xz", "yz", "yx", "zx", "zy", "iso"],
                                "description": (
                                    "Use a preset camera view: 'xy', 'xz', 'yz', "
                                    "'yx', 'zx', 'zy', or 'iso' (isometric)"
                                ),
                            },
                        },
                    },
                ),
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict[str, Any]) -> list[dict[str, Any]]:
            """Handle tool calls."""
            if name == "see":
                return await self._handle_see(arguments)
            if name == "move":
                return await self._handle_move(arguments)
            msg = f"Unknown tool: {name}"
            raise ValueError(msg)

    async def _handle_see(self, arguments: dict[str, Any]) -> list[dict[str, Any]]:
        """Handle 'see' tool - capture scene state.

        Parameters
        ----------
        arguments : dict
            Tool arguments with optional 'include_html' boolean.

        Returns
        -------
        list of dict
            Scene state information including camera position, object count, etc.

        """
        include_html = arguments.get("include_html", False)

        # Get camera state
        camera = self.plotter.camera
        if camera is not None:
            camera_info: dict[str, Any] = {
                "position": list(camera.position),
                "focal_point": list(camera.focal_point),
                "view_up": list(camera.view_up),
                "view_angle": float(camera.view_angle),
                "clipping_range": list(camera.clipping_range),
                "parallel_projection": camera.parallel_projection,
            }
        else:
            camera_info = {
                "position": [0, 0, 1],
                "focal_point": [0, 0, 0],
                "view_up": [0, 1, 0],
                "view_angle": 30.0,
                "clipping_range": [0.01, 1000.01],
                "parallel_projection": False,
            }

        # Get scene information
        scene_info: dict[str, Any] = {
            "object_count": len(self.plotter._actors),  # noqa: SLF001
            "background_color": self.plotter._background_color,  # noqa: SLF001
            "container_id": self.plotter._container_id,  # noqa: SLF001
        }

        # Combine information
        result: dict[str, Any] = {
            "camera": camera_info,
            "scene": scene_info,
        }

        # Optionally include HTML rendering
        if include_html:
            try:
                renderer = self.plotter._renderer  # noqa: SLF001
                html_output = renderer._generate_html()  # type: ignore[union-attr]  # noqa: SLF001
                result["html"] = html_output
            except Exception:
                logger.exception("Failed to generate HTML")
                result["html_error"] = "Failed to generate HTML"

        return [
            {
                "type": "text",
                "text": json.dumps(result, indent=2),
            },
        ]

    async def _handle_move(  # noqa: C901
        self,
        arguments: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """Handle 'move' tool - manipulate camera.

        Parameters
        ----------
        arguments : dict
            Tool arguments with position, focal_point, view_up, or preset.

        Returns
        -------
        list of dict
            Confirmation message with new camera state.

        """
        # Ensure camera exists
        if self.plotter.camera is None:
            from .camera import Camera  # noqa: PLC0415

            self.plotter.camera = Camera()

        # Handle preset views
        if "preset" in arguments:
            preset = arguments["preset"]
            preset_views: dict[str, Any] = {
                "xy": self.plotter.view_xy,
                "xz": self.plotter.view_xz,
                "yz": self.plotter.view_yz,
                "yx": self.plotter.view_yx,
                "zx": self.plotter.view_zx,
                "zy": self.plotter.view_zy,
                "iso": self.plotter.view_isometric,
            }
            if preset in preset_views:
                preset_views[preset]()
                camera = self.plotter.camera
                assert camera is not None  # set above if None  # noqa: S101
                return [
                    {
                        "type": "text",
                        "text": json.dumps(
                            {
                                "status": "success",
                                "action": f"Set camera to {preset} view",
                                "camera": {
                                    "position": list(camera.position),
                                    "focal_point": list(camera.focal_point),
                                    "view_up": list(camera.view_up),
                                },
                            },
                            indent=2,
                        ),
                    },
                ]
            msg = f"Unknown preset: {preset}"
            raise ValueError(msg)

        # Handle manual camera positioning
        camera = self.plotter.camera
        assert camera is not None  # set above if None  # noqa: S101
        actions = []

        if "position" in arguments:
            pos = arguments["position"]
            if len(pos) != 3:  # noqa: PLR2004
                msg = "position must be [x, y, z]"
                raise ValueError(msg)
            camera.position = tuple(pos)
            actions.append(f"Set camera position to {pos}")

        if "focal_point" in arguments:
            focal = arguments["focal_point"]
            if len(focal) != 3:  # noqa: PLR2004
                msg = "focal_point must be [x, y, z]"
                raise ValueError(msg)
            camera.focal_point = tuple(focal)
            actions.append(f"Set camera focal point to {focal}")

        if "view_up" in arguments:
            view_up = arguments["view_up"]
            if len(view_up) != 3:  # noqa: PLR2004
                msg = "view_up must be [x, y, z]"
                raise ValueError(msg)
            camera.view_up = tuple(view_up)
            actions.append(f"Set camera view up to {view_up}")

        if not actions:
            msg = "No camera parameters provided"
            raise ValueError(msg)

        return [
            {
                "type": "text",
                "text": json.dumps(
                    {
                        "status": "success",
                        "actions": actions,
                        "camera": {
                            "position": list(camera.position),
                            "focal_point": list(camera.focal_point),
                            "view_up": list(camera.view_up),
                        },
                    },
                    indent=2,
                ),
            },
        ]

    async def run(self) -> None:
        """Run the MCP server.

        This is typically called in an async context to start the server
        and handle incoming MCP requests.
        """
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options(),
            )
