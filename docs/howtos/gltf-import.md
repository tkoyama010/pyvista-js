# Render glTF/GLB Files

Load 3D assets in glTF 2.0 format (`.gltf` JSON or `.glb` binary container) with {class}`~pyvista_js.GLTFReader`. The browser renderer uses vtk.js's `vtkGLTFImporter`, so geometry, PBR materials, texture images, and embedded lights are rendered automatically.

## Read and render

```python
import pyvista_js as pv

mesh = pv.examples.download_damaged_helmet()

plotter = pv.Plotter()
plotter.add_mesh(mesh)
plotter.show()
```

For local files, pass the path directly:

```python
reader = pv.GLTFReader("model.gltf")
mesh = reader.read()
```

The same call works for `.glb` files; Python-side point extraction handles both the JSON and binary container layouts.

## Render by URL

Override the embedded base64 data with a URL of the glTF asset, so large models are fetched by the renderer instead of inlined:

```python
mesh = pv.GLTFReader("model.gltf", gltf_url="https://example.com/model.gltf").read()
```

## Animations

When the file contains animation clips, the first clip plays automatically in a `requestAnimationFrame` loop. The loop stops once the scene container leaves the page.

## Examples

`examples.download_damaged_helmet` uses this API to fetch and render a glTF asset; see {ref}`using-download-damaged-helmet` for the interactive browser tutorial.

```python
from pyvista_js import examples

mesh = examples.download_damaged_helmet()
```
