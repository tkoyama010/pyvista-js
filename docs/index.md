# pyvista-js Documentation

Welcome to pyvista-js documentation!

## Overview

pyvista-js is a PyVista-like API for vtk.js, bringing the intuitive PyVista interface to JavaScript-based 3D visualization.

## Installation

```bash
pip install pyvista-js
```

## Quick Start

```{replite}
:kernel: python
:height: 600px

import pyvista_js as pv

# Create a simple sphere
sphere = pv.Sphere()

# Visualize it
plotter = pv.Plotter()
plotter.add_mesh(sphere)
plotter.show()
```

## Features

- PyVista-like API for familiar usage
- Integration with vtk.js for web-based visualization
- Support for JupyterLite and Streamlit

## Links

- [GitHub Repository](https://github.com/tkoyama010/pyvista-js)
- [Issue Tracker](https://github.com/tkoyama010/pyvista-js/issues)
