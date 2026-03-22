<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Explanation](#explanation)
  - [Overview](#overview)
  - [Architecture](#architecture)
  - [Features](#features)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Explanation

Deeper understanding of pyvista-js concepts and architecture.

## Overview

pyvista-js is a PyVista-like API for vtk.js, bringing the intuitive PyVista interface
to JavaScript-based 3D visualization. It enables 3D visualization in browser environments
including Pyodide, Jupyter notebooks, and Streamlit applications.

## Architecture

pyvista-js separates concerns between Python and JavaScript:

- **Python side**: Handles geometry preparation, bounding sphere computation, and API surface.
- **JavaScript side (vtk.js)**: Handles the actual geometry parsing and WebGL rendering.

## Features

- PyVista-like API for familiar usage
- Integration with vtk.js for web-based visualization
- Support for JupyterLite and Streamlit
- Physically Based Rendering (PBR) with metallic and roughness controls
- Environment textures for image-based lighting
