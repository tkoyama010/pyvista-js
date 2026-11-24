# View meshes in JupyterLab with JupyterView

pyvista-js draws a scene inside an output cell. [JupyterView] adds
a file viewer to JupyterLab that renders VTK files (`.vtk`, `.vtp`, `.vtu`,
`.pvd`) and the formats supported by [meshio]. Installing both lets you
keep the notebook view and open the same mesh in its own JupyterLab tab.

## Install the extension

```bash
pip install "pyvista-js[jupyter]"
```

The `jupyter` extra installs pyvista-js and JupyterView together. JupyterView
ships as a prebuilt extension for JupyterLab 3.0 and later, so no `jupyter lab build` step is needed. Restart JupyterLab after the install.

Saving a mesh needs meshio, which the `io` extra provides:

```bash
pip install "pyvista-js[io]"
```

## Save a mesh and open it

```python
import pyvista_js as pv

mesh = pv.Sphere()
mesh.save("sphere.vtp")
```

Then open `sphere.vtp` from the JupyterLab file browser, or drag it onto the
workspace. JupyterView renders it with vtk.js, the same engine pyvista-js uses.

## In JupyterLite

JupyterView is a pure frontend extension, so it also runs in JupyterLite. Add
`jupyterview` to the requirements of the JupyterLite build and it becomes
available in the deployed site. JupyterView publishes an online demo at
<https://trungleduc.github.io/jupyterview>.

[jupyterview]: https://github.com/trungleduc/jupyterview
[meshio]: https://github.com/nschloe/meshio
