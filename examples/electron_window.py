"""Example of using pyvista-js with Electron renderer for desktop windows.

This example demonstrates how to use the Electron backend to display
3D visualizations in a desktop window when not in a notebook environment.

To use this example:
1. Install Node.js on your system
2. Set environment variable: PYVISTA_JS_BACKEND=electron
3. Run this script: python examples/electron_window.py

The first run will automatically install Electron via npm.
"""

import os

# Enable Electron backend
os.environ["PYVISTA_JS_BACKEND"] = "electron"

import pyvista_js as pv

# Create a plotter
plotter = pv.Plotter()

# Add multiple meshes
sphere = pv.Sphere(radius=1.0, center=(0, 0, 0))
plotter.add_mesh(sphere, color="red", opacity=0.8)

cube = pv.Cube(center=(3, 0, 0), x_length=1.5, y_length=1.5, z_length=1.5)
plotter.add_mesh(cube, color="green", opacity=0.8)

cylinder = pv.Cylinder(center=(-3, 0, 0), radius=0.5, height=2.0)
plotter.add_mesh(cylinder, color="blue", opacity=0.8)

# Set background color
plotter.background_color = "white"

# Show in Electron window
print("Opening Electron window...")
print("Note: First run may take time to install Electron.")
plotter.show()

print("Visualization window opened. The window will stay open until you close it.")
