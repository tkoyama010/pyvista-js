# pyvista-js

[![PyPI](https://img.shields.io/pypi/v/pyvista-js.svg)](https://pypi.org/project/pyvista-js/)
[![License](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

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

## Installation (Future)

```bash
pip install pyvista-js
```

For Pyodide/stlite:
```python
import micropip
await micropip.install('pyvista-js')
```

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

## Comparison with PyVista

| Feature | PyVista | pyvista-js |
|---------|---------|------------|
| Backend | VTK (C++) | vtk.js (WebGL) |
| Environment | Desktop | Browser |
| Installation | `pip install pyvista` | `pip install pyvista-js` |
| Rendering | Native OpenGL | WebGL |
| Server Required | Optional | No |

## Status

🚧 **Early Development** - This project is in active development.

- [ ] Core Plotter API
- [ ] Basic geometric primitives
- [ ] Mesh rendering
- [ ] PyVista compatibility layer
- [ ] stlite integration
- [ ] Documentation
- [ ] Examples

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
