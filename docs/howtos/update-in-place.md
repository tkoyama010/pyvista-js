# Update a rendered scene in place

When data changes over time, such as colors that follow a time slider,
rendering the whole scene again re-sends geometry that has not changed and
rebuilds the render window. Instead, update just the actors that changed with
{meth}`~pyvista_js.Plotter.update_actor`.

## In a notebook

Show the scene once:

```python
import numpy as np
import pyvista_js as pv

sphere = pv.Sphere()
sphere.point_data["colors"] = np.zeros((sphere.n_points, 3), np.uint8)

plotter = pv.Plotter()
plotter.add_mesh(sphere, scalars="colors")
plotter.show()
```

Then, in a later cell, send new colors to it:

```python
red = np.tile(np.array([255, 0, 0], np.uint8), (sphere.n_points, 1))
plotter.update_actor(0, point_data={"colors": red})
```

Actors are numbered in the order they were added. An update can:

- add or replace point-data arrays with `point_data`,
- color by a different point-data array with `scalars`,
- move the points of a mesh given by points and faces with `points`.

The number of points cannot change. The mesh is updated in Python too, so a
page generated later shows the new data.

## In a page you embed yourself

If you put the page from
{meth}`~pyvista_js.Plotter.generate_standalone_html` somewhere yourself, for
example in an `<iframe>`, deliver the updates yourself as well. Pass
`send=False` and serialize the message with
{func}`~pyvista_js.rendering.scene_to_json`:

```python
from pyvista_js.rendering import scene_to_json

html = plotter.generate_standalone_html()
container_id = plotter.container_id

# ... later, for each change
update = plotter.update_actor(0, point_data={"colors": red}, send=False)
message = scene_to_json(update)
```

Then apply the message with `pvjsApplyUpdate`, which the page defines:

```javascript
// e.g. for a same-origin <iframe srcdoc="...">
iframe.contentWindow.pvjsApplyUpdate(containerId, JSON.parse(message));
```

How the message gets to the page is up to you: a `postMessage` handler, a
widget, or any other channel you already have.

## Limitations

- Updates reach the rendered mesh through smooth-shading normals, but not
  through filters such as {meth}`~pyvista_js.PolyData.clip` or
  {meth}`~pyvista_js.PolyData.contour`, which are computed when the page loads.
- `points` can only be updated for meshes given by points and faces, not for
  generated shapes such as {func}`~pyvista_js.Sphere`.

## Faster serialization

Scenes and update messages with large meshes are written several times faster
when [orjson](https://github.com/ijl/orjson) is installed:

```bash
pip install "pyvista-js[fast]"
```

In Pyodide, run `await micropip.install("orjson")`.
