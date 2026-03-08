# pyvista-js Documentation

Welcome to pyvista-js documentation!

## Overview

pyvista-js is a PyVista-like API for vtk.js, bringing the intuitive PyVista interface to JavaScript-based 3D visualization.

## Installation

```bash
pip install pyvista-js
```

## Quick Start

```{eval-rst}
.. replite::
   :kernel: pyolite
   :height: 600px

   import sys
   sys.path.insert(0, '/drive/src')

   import pyvista_js as pv

   # Create a simple sphere
   sphere = pv.Sphere()

   # Visualize it
   plotter = pv.Plotter()
   plotter.add_mesh(sphere)
   plotter.show()
```

## Physically Based Rendering

```{eval-rst}
.. replite::
   :kernel: pyolite
   :height: 600px

   import sys
   sys.path.insert(0, '/drive/src')

   import pyvista_js as pv

   # Vary metallic and roughness across a grid of spheres
   plotter = pv.Plotter()
   colors = ['red', 'green', 'blue', 'yellow', 'cyan']
   for i in range(5):
       for j in range(6):
           sphere = pv.Sphere(radius=0.4, center=(0.0, 4 - i, j))
           plotter.add_mesh(
               sphere,
               color=colors[i],
               pbr=True,
               metallic=i / 4,
               roughness=j / 5,
           )
   plotter.show()
```

## Features

- PyVista-like API for familiar usage
- Integration with vtk.js for web-based visualization
- Support for JupyterLite and Streamlit

## Links

- [GitHub Repository](https://github.com/tkoyama010/pyvista-js)
- [Issue Tracker](https://github.com/tkoyama010/pyvista-js/issues)
