"""Example demonstrating the MCP server for embodied simulation.

This example shows how to create a 3D scene and interact with it using
the MCP (Model Context Protocol) server, which enables AI agents to
perceive and manipulate the 3D visualization.

The MCP server exposes two tools:
- see: Capture the current state of the scene
- move: Manipulate the camera position and orientation

Usage:
    python examples/mcp_server_example.py

Note: This requires the MCP optional dependency:
    pip install pyvista-js[mcp]
"""

import asyncio

import pyvista_js as pv


async def main() -> None:
    """Run the MCP server example."""
    # Check if MCP is available
    if not pv.MCP_AVAILABLE:
        print("MCP server not available. Install with: pip install pyvista-js[mcp]")
        return

    # Create a simple scene with multiple objects
    plotter = pv.Plotter()

    # Add a red sphere at the origin
    plotter.add_mesh(pv.Sphere(center=(0, 0, 0), radius=1), color="red")

    # Add a blue cube offset to the right
    plotter.add_mesh(pv.Cube(center=(3, 0, 0), x_length=1.5), color="blue")

    # Add a green cylinder offset to the left
    plotter.add_mesh(pv.Cylinder(center=(-3, 0, 0), radius=0.5, height=2), color="green")

    # Set an isometric view for better visualization
    plotter.view_isometric()

    # Create MCP server
    print("Starting MCP server for embodied simulation...")
    print("Available tools:")
    print("  - see: Capture scene state (camera, objects, metadata)")
    print("  - move: Manipulate camera position and orientation")
    print("\nThe server will handle MCP requests via stdio.")
    print("Press Ctrl+C to stop the server.\n")

    server = pv.MCPServer(plotter, name="pyvista-js-embodied-sim")

    # Run the MCP server (this will block until interrupted)
    try:
        await server.run()
    except KeyboardInterrupt:
        print("\nMCP server stopped.")


if __name__ == "__main__":
    asyncio.run(main())
