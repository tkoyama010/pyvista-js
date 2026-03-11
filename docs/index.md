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

   from pyvista_js import examples
   cubemap = examples.download_sky_box_cube_map()

   # Vary metallic and roughness across a grid of spheres
   plotter = pv.Plotter()
   plotter.set_environment_texture(cubemap)
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
   plotter.view_vector((-1, 0, 0), (0, 1, 0))
   plotter.show()
```

## Streamlit Demo

```{eval-rst}
.. stlite::
   :requirements: pyvista-js

   import streamlit as st
   import streamlit.components.v1 as components

   import pyvista_js as pv

   st.title("pyvista-js Demo")

   geometry = st.selectbox("Geometry", ["Sphere", "Cube", "Cylinder"])

   color = st.selectbox("Color", ["red", "green", "blue", "yellow", "cyan", "magenta"])

   opacity = st.slider("Opacity", min_value=0.0, max_value=1.0, value=0.8, step=0.1)

   plotter = pv.Plotter()

   if geometry == "Sphere":
       mesh = pv.Sphere(radius=1.0)
   elif geometry == "Cube":
       mesh = pv.Cube()
   else:
       mesh = pv.Cylinder(radius=0.5, height=2.0)

   plotter.add_mesh(mesh, color=color, opacity=opacity)

   html = plotter._renderer._generate_standalone_html()
   components.html(html, height=600)
```

## Features

- PyVista-like API for familiar usage
- Integration with vtk.js for web-based visualization
- Support for JupyterLite and Streamlit

## API Reference

See the full {doc}`API Reference <api/index>` for detailed documentation of all classes and functions.

```{toctree}
:maxdepth: 2
:hidden:

api/index
```

## Links

- [GitHub Repository](https://github.com/tkoyama010/pyvista-js)
- [Issue Tracker](https://github.com/tkoyama010/pyvista-js/issues)
