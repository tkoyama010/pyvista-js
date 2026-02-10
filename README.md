# pyvista-js

[![PyPI](https://img.shields.io/pypi/v/pyvista-js.svg)](https://pypi.org/project/pyvista-js/)
[![License](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/tkoyama010/pyvista-js/main.svg)](https://results.pre-commit.ci/latest/github/tkoyama010/pyvista-js/main)
[![JupyterLite](https://jupyterlite.rtfd.io/en/latest/_static/badge.svg)](https://tkoyama010.github.io/pyvista-js/)

PyVista-like API for vtk.js - Bring intuitive 3D visualization to the browser.

## Vision

Provide a familiar PyVista interface that works seamlessly in browser environments (Pyodide, stlite, JupyterLite) by leveraging vtk.js under the hood.

## Quick Example (Goal)

```python
import pyvista_js as pv
import streamlit as st

# Create a plotter
plotter = pv.Plotter()

# Add a mesh
mesh = pv.Sphere()
plotter.add_mesh(mesh, color='red', opacity=0.8)

# Display in browser
plotter.show()
```

## Features (Planned)

- 🎨 **PyVista-like API** - Familiar interface for PyVista users
- 🌐 **Browser-native** - Runs entirely in the browser via Pyodide
- ⚡ **vtk.js powered** - Leverages the power of vtk.js for rendering
- 📊 **Streamlit/stlite support** - Easy integration with web frameworks
- 🔧 **Lightweight** - No server required, pure client-side
- 🖥️ **Desktop window support** - Electron renderer for non-notebook environments

## Installation

```bash
pip install pyvista-js
```

For Streamlit support:
```bash
pip install pyvista-js[streamlit]
```

For Pyodide/stlite:
```python
import micropip
await micropip.install('pyvista-js')
```

## Usage

### Basic Example

```python
import pyvista_js as pv

# Create a plotter
plotter = pv.Plotter()

# Add a mesh
mesh = pv.Sphere(radius=1.0)
plotter.add_mesh(mesh, color='red', opacity=0.8)

# Display (in Pyodide/browser environment)
plotter.show()
```

### Streamlit/stlite Example

```python
import streamlit as st
import pyvista_js as pv

st.title("3D Visualization")

# Create visualization
plotter = pv.Plotter()
sphere = pv.Sphere()
plotter.add_mesh(sphere, color='blue')

# Display in Streamlit
pv.pyvista_chart(plotter, height=600)
```

### Desktop Window (Electron) Example

For standard Python scripts (not in notebooks), you can use the Electron backend to display visualizations in a desktop window:

```python
import os
os.environ['PYVISTA_JS_BACKEND'] = 'electron'

import pyvista_js as pv

# Create visualization
plotter = pv.Plotter()
sphere = pv.Sphere()
plotter.add_mesh(sphere, color='red')

# Opens in Electron desktop window
plotter.show()
```

**Requirements for Electron backend:**
- Node.js installed on your system
- Electron will be installed automatically on first use

**Note:** If Electron is not available, the renderer will fall back to opening the visualization in your default web browser.

## API Design

### Core Classes

```python
# Plotter - Main visualization interface
plotter = pv.Plotter()
plotter.add_mesh(mesh, **kwargs)
plotter.show()

# Geometric objects
sphere = pv.Sphere(radius=1.0, center=(0, 0, 0))
cube = pv.Cube()
cylinder = pv.Cylinder()

# Mesh operations
mesh.points  # NumPy array of vertices
mesh.faces   # Cell connectivity
```

### Backend Selection

pyvista-js automatically selects the appropriate rendering backend based on the environment:

- **Jupyter/JupyterLite**: Uses `VTKJSRenderer` (vtk.js in notebook)
- **Streamlit/stlite**: Uses `pyvista_chart` integration
- **Standard Python**: Uses `MockRenderer` (testing) by default

You can explicitly select a backend using the `PYVISTA_JS_BACKEND` environment variable:

```python
import os

# Use Electron for desktop window
os.environ['PYVISTA_JS_BACKEND'] = 'electron'

# Use mock renderer (for testing)
os.environ['PYVISTA_JS_BACKEND'] = 'mock'

# Auto-detect (default)
os.environ['PYVISTA_JS_BACKEND'] = 'auto'
```

## Comparison with PyVista

| Feature | PyVista | pyvista-js |
|---------|---------|------------|
| Backend | VTK (C++) | vtk.js (WebGL) |
| Environment | Desktop | Browser + Desktop (Electron) |
| Installation | `pip install pyvista` | `pip install pyvista-js` |
| Rendering | Native OpenGL | WebGL / Electron |
| Server Required | Optional | No |
| Node.js Required | No | Only for Electron backend |

## Status

🚀 **Beta** - Core functionality implemented!

- [x] Core Plotter API
- [x] Basic geometric primitives (Sphere, Cube, Cylinder)
- [x] Mesh rendering with vtk.js
- [x] PyVista compatibility layer
- [x] Streamlit/stlite integration
- [x] Electron desktop window support
- [ ] Advanced mesh operations
- [ ] Comprehensive documentation
- [ ] More examples

## Contributing

Contributions are welcome! This project aims to:

1. Provide PyVista-like API for browser environments
2. Leverage vtk.js for efficient WebGL rendering
3. Enable 3D visualization in Pyodide/stlite applications

## Related Projects

- [PyVista](https://github.com/pyvista/pyvista) - 3D plotting and mesh analysis
- [vtk.js](https://github.com/Kitware/vtk-js) - VTK for the Web
- [stlite](https://github.com/whitphx/stlite) - Serverless Streamlit

## License

BSD 3-Clause License - See [LICENSE](LICENSE) for details.

This project uses vtk.js which is also licensed under BSD 3-Clause License.

## Acknowledgments

- Built on top of [vtk.js](https://kitware.github.io/vtk-js/)
- Inspired by [PyVista](https://www.pyvista.org/)
- Designed for [Pyodide](https://pyodide.org/) environments
