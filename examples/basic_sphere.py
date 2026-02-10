"""Basic example: Creating and displaying a sphere."""

import pyvista_js as pv

# Create a plotter
plotter = pv.Plotter()

# Create a sphere
sphere = pv.Sphere(radius=1.0, center=(0, 0, 0))

print(f"Sphere has {sphere.n_points} points")

# Add the sphere to the plotter
plotter.add_mesh(sphere, color="red", opacity=0.8)

# Display the visualization
plotter.show()
