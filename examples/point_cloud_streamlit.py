"""Interactive 3D point cloud visualization with Streamlit.

This Streamlit application demonstrates interactive 3D point cloud visualization
similar to the VGGT (Visual Geometry Grounded Transformer) demo, featuring:
- Multiple 3D reconstructions/point clouds
- Model switching via thumbnails/selector
- Interactive camera controls (orbit, zoom, pan)
- Scalar coloring with different colormaps
- Dense point cloud rendering
"""

import numpy as np
import streamlit as st

import pyvista_js as pv


def generate_sphere_point_cloud(n_points: int = 5000, noise: float = 0.1) -> tuple:
    """Generate a sphere-shaped point cloud."""
    theta = np.random.uniform(0, 2 * np.pi, n_points)
    phi = np.random.uniform(0, np.pi, n_points)
    r = np.random.normal(1.0, noise, n_points)

    x = r * np.sin(phi) * np.cos(theta)
    y = r * np.sin(phi) * np.sin(theta)
    z = r * np.cos(phi)

    return np.column_stack([x, y, z])


def generate_torus_point_cloud(n_points: int = 5000, R: float = 1.0, r: float = 0.3) -> tuple:
    """Generate a torus-shaped point cloud."""
    theta = np.random.uniform(0, 2 * np.pi, n_points)
    phi = np.random.uniform(0, 2 * np.pi, n_points)

    x = (R + r * np.cos(theta)) * np.cos(phi)
    y = (R + r * np.cos(theta)) * np.sin(phi)
    z = r * np.sin(theta)

    return np.column_stack([x, y, z])


def generate_bunny_point_cloud(n_points: int = 5000) -> tuple:
    """Generate a bunny-like shaped point cloud."""
    # Body (ellipsoid)
    n_body = int(n_points * 0.5)
    theta = np.random.uniform(0, 2 * np.pi, n_body)
    phi = np.random.uniform(0, np.pi, n_body)
    r = np.random.normal(1.0, 0.05, n_body)

    x_body = 0.6 * r * np.sin(phi) * np.cos(theta)
    y_body = 0.8 * r * np.sin(phi) * np.sin(theta)
    z_body = 0.7 * r * np.cos(phi) - 0.2

    # Head (sphere)
    n_head = int(n_points * 0.3)
    theta = np.random.uniform(0, 2 * np.pi, n_head)
    phi = np.random.uniform(0, np.pi, n_head)
    r = np.random.normal(0.4, 0.03, n_head)

    x_head = r * np.sin(phi) * np.cos(theta)
    y_head = r * np.sin(phi) * np.sin(theta)
    z_head = r * np.cos(phi) + 0.5

    # Ears (elongated ellipsoids)
    n_ear = int(n_points * 0.1)
    # Left ear
    theta = np.random.uniform(0, 2 * np.pi, n_ear)
    phi = np.random.uniform(0, np.pi, n_ear)
    r = np.random.normal(0.15, 0.02, n_ear)

    x_left_ear = 0.2 * r * np.sin(phi) * np.cos(theta) - 0.25
    y_left_ear = 0.2 * r * np.sin(phi) * np.sin(theta)
    z_left_ear = 0.8 * r * np.cos(phi) + 0.9

    # Right ear
    x_right_ear = 0.2 * r * np.sin(phi) * np.cos(theta) + 0.25
    y_right_ear = 0.2 * r * np.sin(phi) * np.sin(theta)
    z_right_ear = 0.8 * r * np.cos(phi) + 0.9

    # Combine all parts
    x = np.concatenate([x_body, x_head, x_left_ear, x_right_ear])
    y = np.concatenate([y_body, y_head, y_left_ear, y_right_ear])
    z = np.concatenate([z_body, z_head, z_left_ear, z_right_ear])

    return np.column_stack([x, y, z])


def generate_double_helix_point_cloud(n_points: int = 5000) -> tuple:
    """Generate a double helix (DNA-like) point cloud."""
    t = np.linspace(0, 4 * np.pi, n_points // 2)
    r = 0.5

    # First helix
    x1 = r * np.cos(t)
    y1 = r * np.sin(t)
    z1 = t * 0.3

    # Second helix (180 degrees out of phase)
    x2 = r * np.cos(t + np.pi)
    y2 = r * np.sin(t + np.pi)
    z2 = t * 0.3

    # Add some noise
    noise = 0.05
    x1 += np.random.normal(0, noise, len(x1))
    y1 += np.random.normal(0, noise, len(y1))
    x2 += np.random.normal(0, noise, len(x2))
    y2 += np.random.normal(0, noise, len(y2))

    x = np.concatenate([x1, x2])
    y = np.concatenate([y1, y2])
    z = np.concatenate([z1, z2])

    return np.column_stack([x, y, z])


# Page configuration
st.set_page_config(
    page_title="3D Point Cloud Visualization",
    page_icon="🌐",
    layout="wide"
)

st.title("🌐 3D Point Cloud Visualization")

st.markdown("""
Interactive 3D point cloud viewer demonstrating capabilities similar to the
[VGGT (Visual Geometry Grounded Transformer)](https://vgg-t.github.io/) demo.

**Features:**
- 🎯 Interactive camera controls (orbit, zoom, pan)
- 🎨 Scalar coloring with multiple colormaps
- 🔄 Multiple model switching
- 📊 Dense point cloud rendering
""")

# Sidebar controls
st.sidebar.header("⚙️ Controls")

# Model selection
model_options = {
    "Sphere": "A spherical point cloud",
    "Torus": "A torus (donut) shaped point cloud",
    "Bunny": "A bunny-like figure",
    "Double Helix": "DNA-like double helix structure"
}

selected_model = st.sidebar.selectbox(
    "Select 3D Model",
    options=list(model_options.keys()),
    help="Choose a point cloud model to visualize"
)

st.sidebar.info(model_options[selected_model])

# Point cloud density
density = st.sidebar.slider(
    "Point Density",
    min_value=1000,
    max_value=20000,
    value=5000,
    step=1000,
    help="Number of points in the cloud"
)

# Colormap selection
colormaps = ["viridis", "plasma", "inferno", "magma", "coolwarm", "turbo", "jet", "rainbow"]
selected_cmap = st.sidebar.selectbox(
    "Colormap",
    options=colormaps,
    index=0,
    help="Color scheme for scalar data"
)

# Coloring mode
coloring_mode = st.sidebar.selectbox(
    "Coloring Mode",
    options=["Elevation (Z)", "Distance from Origin", "X Coordinate", "Y Coordinate"],
    help="How to color the points"
)

# Point size hint
st.sidebar.markdown("---")
st.sidebar.markdown("""
**💡 Tip:** Use mouse/touch to:
- **Rotate**: Left click + drag
- **Zoom**: Scroll wheel
- **Pan**: Right click + drag
""")

# Generate point cloud based on selection
with st.spinner(f"Generating {selected_model} point cloud with {density} points..."):
    if selected_model == "Sphere":
        points = generate_sphere_point_cloud(n_points=density)
    elif selected_model == "Torus":
        points = generate_torus_point_cloud(n_points=density)
    elif selected_model == "Bunny":
        points = generate_bunny_point_cloud(n_points=density)
    else:  # Double Helix
        points = generate_double_helix_point_cloud(n_points=density)

    # Create PolyData
    point_cloud = pv.PolyData(points)

    # Add scalar values based on coloring mode
    if coloring_mode == "Elevation (Z)":
        point_cloud.point_data['scalars'] = points[:, 2]
    elif coloring_mode == "Distance from Origin":
        point_cloud.point_data['scalars'] = np.linalg.norm(points, axis=1)
    elif coloring_mode == "X Coordinate":
        point_cloud.point_data['scalars'] = points[:, 0]
    else:  # Y Coordinate
        point_cloud.point_data['scalars'] = points[:, 1]

# Main visualization area
col1, col2 = st.columns([3, 1])

with col1:
    st.header("📊 Visualization")

    # Create plotter
    plotter = pv.Plotter()

    # Add point cloud
    plotter.add_mesh(
        point_cloud,
        scalars='scalars',
        cmap=selected_cmap,
        style='points',
        opacity=1.0,
    )

    # Display
    pv.pyvista_chart(plotter, height=700)

with col2:
    st.header("📈 Statistics")
    st.metric("Points", f"{point_cloud.n_points:,}")
    st.metric("Model", selected_model)

    # Bounds information
    bounds = point_cloud.points
    st.markdown("**Bounds:**")
    st.markdown(f"- X: [{bounds[:, 0].min():.2f}, {bounds[:, 0].max():.2f}]")
    st.markdown(f"- Y: [{bounds[:, 1].min():.2f}, {bounds[:, 1].max():.2f}]")
    st.markdown(f"- Z: [{bounds[:, 2].min():.2f}, {bounds[:, 2].max():.2f}]")

    # Scalar statistics
    scalars = point_cloud.point_data['scalars']
    st.markdown("**Scalar Values:**")
    st.markdown(f"- Min: {scalars.min():.3f}")
    st.markdown(f"- Max: {scalars.max():.3f}")
    st.markdown(f"- Mean: {scalars.mean():.3f}")

# Footer
st.markdown("---")
st.markdown("""
### 🔗 References

- **VGGT Demo**: [vgg-t.github.io](https://vgg-t.github.io/)
- **VGGT Paper**: [arxiv.org/abs/2503.11651](https://arxiv.org/abs/2503.11651)
- **pyvista-js**: [github.com/tkoyama010/pyvista-js](https://github.com/tkoyama010/pyvista-js)
- **PyVista**: [pyvista.org](https://www.pyvista.org/)
- **vtk.js**: [kitware.github.io/vtk-js](https://kitware.github.io/vtk-js/)

### 🎯 About This Demo

This demonstration showcases pyvista-js's capabilities in scientific visualization and computer vision domains.
The interactive 3D point cloud viewer provides features similar to the VGGT (Visual Geometry Grounded Transformer)
demo, which was the CVPR 2025 Best Paper Award winner for 3D reconstruction from images.
""")
