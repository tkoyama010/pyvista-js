"""Streamlit/stlite example for pyvista-js.

This example demonstrates how to use pyvista-js in a Streamlit/stlite application.
"""

import streamlit as st

import pyvista_js as pv
from pyvista_js import examples

st.title("🌐 pyvista-js Demo")

st.markdown("""
This is a demonstration of pyvista-js with Streamlit/stlite.
PyVista-like 3D visualization in the browser using vtk.js!
""")

# Sidebar controls
st.sidebar.header("⚙️ Controls")

geometry = st.sidebar.selectbox("Geometry", ["Bunny", "Sphere", "Cube", "Cylinder"])

color = st.sidebar.selectbox(
    "Color", ["white", "red", "green", "blue", "yellow", "cyan", "magenta"]
)

opacity = st.sidebar.slider("Opacity", min_value=0.0, max_value=1.0, value=0.8, step=0.1)

# Create visualization
st.header("📊 Visualization")

plotter = pv.Plotter()

# Create geometry based on selection
if geometry == "Bunny":
    mesh = examples.download_bunny()
    st.sidebar.info(f"Stanford Bunny with {mesh.n_points} points")
elif geometry == "Sphere":
    mesh = pv.Sphere(radius=1.0)
    st.sidebar.info(f"Sphere with {mesh.n_points} points")
elif geometry == "Cube":
    mesh = pv.Cube()
    st.sidebar.info(f"Cube with {mesh.n_points} points")
else:  # Cylinder
    mesh = pv.Cylinder(radius=0.5, height=2.0)
    st.sidebar.info(f"Cylinder with {mesh.n_points} points")

# Add mesh to plotter
plotter.add_mesh(mesh, color=color, opacity=opacity)

# Display the visualization
pv.pyvista_chart(plotter, height=600)

# Information
st.markdown("""
---
### 🎯 Features
- **Interactive 3D**: Rotate, zoom, and pan with mouse/touch
- **PyVista API**: Familiar interface for PyVista users
- **Browser-native**: No server required, runs entirely in browser
- **Powered by vtk.js**: High-performance WebGL rendering

### 🔗 Links
- [pyvista-js on GitHub](https://github.com/tkoyama010/pyvista-js)
- [PyVista](https://www.pyvista.org/)
- [vtk.js](https://kitware.github.io/vtk-js/)
""")
