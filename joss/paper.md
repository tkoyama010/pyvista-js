---
title: 'pyvista-js: A PyVista-like API for 3D visualization in the browser'
tags:
  - Python
  - JavaScript
  - 3D visualization
  - WebAssembly
  - scientific computing
authors:
  - name: Tetsuo Koyama
    orcid: 0000-0001-7955-5947
    affiliation: 1
affiliations:
  - name: Independent Researcher, Japan
    index: 1
date: 11 March 2026
bibliography: paper.bib

---

# Summary

`pyvista-js` is an open-source Python package that provides a
[PyVista](https://pyvista.org)-like API [@pyvista] for 3D visualization
running entirely in the web browser. By bridging the familiar PyVista interface
with [vtk.js](https://kitware.github.io/vtk-js) [@vtkjs] — the JavaScript
port of the Visualization Toolkit (VTK) [@vtk] — `pyvista-js` enables
researchers and engineers to create interactive 3D visualizations without
requiring a local VTK installation. The package integrates with
[JupyterLite](https://jupyterlite.readthedocs.io) [@jupyterlite], a
WebAssembly-powered Jupyter environment that runs entirely in the browser,
allowing zero-install interactive notebooks to be shared as static web pages.

# Statement of need

PyVista [@pyvista] has become a widely adopted tool for 3D scientific
visualization in the Python ecosystem, offering a high-level interface to VTK.
However, sharing interactive 3D visualizations with collaborators or in
educational settings often requires recipients to install VTK and PyVista
locally, which can be a significant barrier. While Jupyter notebooks
[@jupyter] partially address reproducibility concerns, they still require a
running Python kernel.

`pyvista-js` addresses this gap by targeting vtk.js [@vtkjs] as the rendering
backend, allowing the same PyVista-style code to run directly in the browser
via JupyterLite [@jupyterlite]. This approach enables:

- **Zero-install notebooks**: Users can open and interact with 3D
  visualizations through a URL, with no local software installation required.
- **Familiar API**: Researchers already using PyVista can reuse their
  knowledge, with `pyvista-js` following the same class and method naming
  conventions.
- **Lightweight deployment**: Static websites can host fully interactive 3D
  visualization notebooks, making it easier to publish reproducible scientific
  figures and educational materials.
- **NumPy compatibility**: The package uses NumPy [@numpy] arrays as the
  primary data structure, consistent with the scientific Python ecosystem.

`pyvista-js` is designed for researchers who want to share 3D scientific
visualizations as interactive web content, educators who want to distribute
runnable notebooks without infrastructure overhead, and developers building
browser-based scientific applications with a Python-first workflow.

# Acknowledgements

We acknowledge the PyVista [@pyvista] and vtk.js [@vtkjs] communities whose
foundational work made `pyvista-js` possible.

# References
