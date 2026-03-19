"""3D point cloud visualization example.

This example demonstrates interactive 3D point cloud visualization
similar to the VGGT (Visual Geometry Grounded Transformer) demo.
Features:
- Interactive 3D point cloud with camera orbit controls
- Colored point cloud rendering
- Scalable to dense point clouds
"""

import numpy as np

import pyvista_js as pv

# Generate a sample 3D point cloud
# Create a bunny-like shape using parametric equations
n_points = 10000

# Create a random point cloud in the shape of a sphere with some noise
theta = np.random.uniform(0, 2 * np.pi, n_points)
phi = np.random.uniform(0, np.pi, n_points)
r = np.random.normal(1.0, 0.1, n_points)

x = r * np.sin(phi) * np.cos(theta)
y = r * np.sin(phi) * np.sin(theta)
z = r * np.cos(phi)

points = np.column_stack([x, y, z])

# Create PolyData from points (no faces needed for point cloud)
point_cloud = pv.PolyData(points)

# Add scalar values for coloring (e.g., height-based coloring)
point_cloud.point_data["elevation"] = points[:, 2]

print(f"Point cloud has {point_cloud.n_points} points")

# Create a plotter
plotter = pv.Plotter()

# Add the point cloud with scalar coloring
plotter.add_mesh(
    point_cloud,
    scalars="elevation",
    cmap="viridis",
    style="points",
    opacity=1.0,
)

# Display the visualization
plotter.show()
