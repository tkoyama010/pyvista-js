"""Example demonstrating scalar array support in pyvista-js.

This example shows how to add scalar data to a mesh and visualize it
with different colormaps, similar to PyVista's scalar coloring API.
"""

import numpy as np

import pyvista_js as pv

# Create a sphere mesh
mesh = pv.Sphere(radius=1.0, theta_resolution=50, phi_resolution=50)

# Add scalar data using dictionary-style access
# Elevation: Z-coordinate of each point
mesh["elevation"] = mesh.points[:, 2]

# Temperature: Synthetic temperature data based on distance from center
center = np.array([0.0, 0.0, 0.0])
distances = np.linalg.norm(mesh.points - center, axis=1)
mesh["temperature"] = 100.0 * (1.0 - distances / distances.max())

# Example 1: Visualize elevation with viridis colormap
print("Creating elevation plot with viridis colormap...")
plotter1 = pv.Plotter()
plotter1.add_mesh(mesh, scalars="elevation", cmap="viridis")
plotter1.show()

# Example 2: Visualize temperature with plasma colormap
print("Creating temperature plot with plasma colormap...")
plotter2 = pv.Plotter()
plotter2.add_mesh(mesh, scalars="temperature", cmap="plasma")
plotter2.show()

# Example 3: Visualize elevation with jet colormap
print("Creating elevation plot with jet colormap...")
plotter3 = pv.Plotter()
plotter3.add_mesh(mesh, scalars="elevation", cmap="jet")
plotter3.show()

# Example 4: Check point_data interface
print(f"\nAvailable scalar arrays: {mesh.point_data.keys()}")
print(f"Number of points: {mesh.n_points}")
print(f"Elevation range: [{mesh['elevation'].min():.2f}, {mesh['elevation'].max():.2f}]")
print(f"Temperature range: [{mesh['temperature'].min():.2f}, {mesh['temperature'].max():.2f}]")
