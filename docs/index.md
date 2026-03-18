# pyvista-js Documentation

Welcome to the `pyvista-js` documentation!

## What is pyvista-js?

`pyvista-js` is a PyVista-like API for [vtk.js](https://github.com/Kitware/vtk-js), bringing the intuitive [PyVista](https://github.com/pyvista/pyvista) interface to JavaScript-based 3D visualization in browser environments.

### Key Features

- **PyVista-style API**: Familiar interface for PyVista users
- **Browser-native 3D visualization**: Powered by vtk.js for WebGL rendering
- **JupyterLite support**: Run interactive 3D examples directly in the browser
- **Streamlit integration**: Build web apps with 3D visualization
- **Physically Based Rendering (PBR)**: Advanced materials and lighting
- **No server required**: Pure client-side rendering with Pyodide

### Use Cases

- **Interactive documentation**: Embed 3D visualizations in browser-based docs
- **Educational materials**: Create interactive 3D tutorials that run without installation
- **Web applications**: Build 3D visualization tools with Streamlit or custom web frameworks
- **Rapid prototyping**: Test visualization ideas quickly in JupyterLite

## Installation

Install from PyPI:

```bash
pip install pyvista-js
```

For browser environments (JupyterLite, Pyodide, stlite):

```python
import micropip
await micropip.install("pyvista-js")
```

**Prerequisites**: Python 3.10 or higher

## Quick Start Example

Here's a simple example to create and visualize a 3D sphere:

```python
import pyvista_js as pv

# Create a plotter
plotter = pv.Plotter()

# Add a red sphere
plotter.add_mesh(pv.Sphere(), color="red")

# Display the visualization
plotter.show()
```

This code works in both standard Python environments and browser-based environments like JupyterLite.

______________________________________________________________________

## Documentation Structure

::::{grid} 1 1 2 2
:gutter: 2

:::{grid-item-card} 📚 Tutorials
:link: tutorials/index
:link-type: doc
:class-card: sd-rounded-3

**Learning-oriented lessons** that guide you through using pyvista-js step-by-step. Perfect for getting started with 3D visualization in the browser.
:::

:::{grid-item-card} 🔧 How-To Guides
:link: howtos/index
:link-type: doc
:class-card: sd-rounded-3

**Problem-oriented guides** for accomplishing specific tasks. Find practical solutions to common visualization challenges.
:::

:::{grid-item-card} 💡 Explanation
:link: explanation/index
:link-type: doc
:class-card: sd-rounded-3

**Understanding-oriented discussions** about the architecture and design decisions behind pyvista-js. Learn how and why it works.
:::

:::{grid-item-card} 📖 API Reference
:link: api/index
:link-type: doc
:class-card: sd-rounded-3

**Information-oriented technical descriptions** of classes, methods, and functions. Complete API documentation for all components.
:::

::::

Our documentation follows the [Diátaxis](https://diataxis.fr/) framework to help you find the right content for your needs.

______________________________________________________________________

## Additional Resources

- **[GitHub Repository](https://github.com/tkoyama010/pyvista-js)** - Source code and development
- **[Issue Tracker](https://github.com/tkoyama010/pyvista-js/issues)** - Bug reports and feature requests
- **[GitHub Discussions](https://github.com/tkoyama010/pyvista-js/discussions)** - Ask questions and share ideas
- **[Try it in your browser](https://tkoyama010.github.io/pyvista-js/)** - Interactive JupyterLite demo
- **[PyVista Documentation](https://docs.pyvista.org/)** - Learn more about the original PyVista project
- **[vtk.js Documentation](https://kitware.github.io/vtk-js/)** - The underlying JavaScript library

```{toctree}
:maxdepth: 1
:hidden:
:caption: Getting Started

Installation <self>
```

```{toctree}
:maxdepth: 1
:hidden:
:caption: Contents

tutorials/index
howtos/index
explanation/index
api/index
```

```{toctree}
:maxdepth: 1
:hidden:
:caption: Demos

stlite_demo
```
