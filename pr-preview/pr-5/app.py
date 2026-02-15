"""pyvista-js stlite demo application."""

import streamlit as st

st.title("🌐 pyvista-js Demo")

st.markdown("""
**pyvista-js** brings PyVista-like 3D visualization to the browser!

### Technology Stack
- 🐍 **Pyodide**: Python in WebAssembly
- 🎨 **stlite**: Serverless Streamlit
- 📊 **pyvista-js**: 3D visualization with vtk.js
""")

st.info("📦 Demo coming soon after PyPI publication!")

# Example code
st.header("📝 Example Usage")

st.code(
    """import pyvista_js as pv
import streamlit as st

# Create a plotter
plotter = pv.Plotter()

# Add a sphere mesh
mesh = pv.Sphere(radius=1.0)
plotter.add_mesh(mesh, color='red', opacity=0.8)

# Display in Streamlit/stlite
pv.pyvista_chart(plotter, height=600)
""",
    language="python",
)

# Features
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
- [stlite](https://github.com/whitphx/stlite)
""")
