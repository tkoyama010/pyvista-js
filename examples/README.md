# pyvista-js Examples

This directory contains examples demonstrating various features of pyvista-js for 3D visualization in the browser.

## Available Examples

### Basic Examples

#### `basic_sphere.py`
A simple example showing how to create and display a sphere using pyvista-js.

**Features:**
- Creating a basic 3D geometry
- Adding mesh to plotter
- Displaying visualization

**Run:**
```bash
python examples/basic_sphere.py
```

#### `point_cloud.py`
Demonstrates 3D point cloud visualization with interactive controls.

**Features:**
- Creating point clouds from NumPy arrays
- Scalar coloring based on elevation
- Interactive camera controls (orbit, zoom, pan)
- Dense point cloud rendering

**Run:**
```bash
python examples/point_cloud.py
```

**Inspiration:** This example demonstrates capabilities similar to the [VGGT (Visual Geometry Grounded Transformer)](https://vgg-t.github.io/) demo, which was the CVPR 2025 Best Paper Award winner for 3D reconstruction from images.

### Streamlit Examples

#### `streamlit_app.py`
Interactive Streamlit application with geometry selection and styling controls.

**Features:**
- Multiple geometry types (Sphere, Cube, Cylinder)
- Color and opacity controls
- Live updates based on user input

**Run:**
```bash
streamlit run examples/streamlit_app.py
```

#### `point_cloud_streamlit.py`
Advanced 3D point cloud visualization with Streamlit, featuring multiple models and interactive controls.

**Features:**
- Multiple 3D point cloud models:
  - Sphere: Spherical point cloud with noise
  - Torus: Donut-shaped point cloud
  - Bunny: Bunny-like figure (body, head, ears)
  - Double Helix: DNA-like double helix structure
- Model switching via dropdown selector
- Adjustable point density (1,000 - 20,000 points)
- Multiple coloring modes:
  - Elevation (Z coordinate)
  - Distance from origin
  - X/Y coordinate coloring
- Multiple colormaps (viridis, plasma, inferno, magma, coolwarm, etc.)
- Real-time statistics and bounds information
- Interactive camera controls (orbit, zoom, pan)

**Run:**
```bash
# Install streamlit dependency first
pip install pyvista-js[streamlit]

# Run the app
streamlit run examples/point_cloud_streamlit.py
```

**Inspiration:** This example is inspired by the [VGGT demo](https://vgg-t.github.io/), showcasing pyvista-js's capabilities in scientific visualization and computer vision domains.

## Requirements

All examples require:
- Python 3.10+
- pyvista-js
- numpy

Streamlit examples additionally require:
- streamlit >= 1.30

Install with:
```bash
# Basic examples
pip install pyvista-js

# Streamlit examples
pip install pyvista-js[streamlit]
```

## Features Demonstrated

### Point Cloud Visualization
- Creating point clouds from NumPy arrays
- Rendering thousands of points efficiently
- Scalar coloring with multiple colormaps
- Interactive camera controls

### Interactive Controls
- Orbit: Rotate around the scene
- Zoom: Adjust viewing distance
- Pan: Move the camera position
- All controls work with mouse/touch

### Scalar Coloring
- Assign per-point attributes
- Apply colormaps (viridis, plasma, etc.)
- Visualize data distributions

### Multiple Rendering Styles
- Surface rendering (default)
- Wireframe rendering
- Point cloud rendering

## Browser Compatibility

All examples generate HTML that works in modern browsers:
- Chrome/Edge (recommended)
- Firefox
- Safari
- Mobile browsers (iOS/Android)

No plugins or extensions required - pure WebGL rendering via vtk.js.

## References

- **pyvista-js**: [github.com/tkoyama010/pyvista-js](https://github.com/tkoyama010/pyvista-js)
- **PyVista**: [pyvista.org](https://www.pyvista.org/)
- **vtk.js**: [kitware.github.io/vtk-js](https://kitware.github.io/vtk-js/)
- **VGGT**: [vgg-t.github.io](https://vgg-t.github.io/) | [arxiv.org/abs/2503.11651](https://arxiv.org/abs/2503.11651)

## Contributing

Have an idea for a new example? Contributions are welcome! Please open an issue or pull request on [GitHub](https://github.com/tkoyama010/pyvista-js/issues).
