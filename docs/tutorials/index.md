# Tutorials

Topic driven themed lessons to help you get started with pyvista-js.

## Quick Start

```{eval-rst}
.. replite::
   :kernel: pyolite
   :height: 600px

   import micropip
   await micropip.install("jinja2")

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

## glTF Rendering

### Using GLTFReader

```{eval-rst}
.. replite::
   :kernel: pyolite
   :height: 600px

   import micropip
   await micropip.install("jinja2")

   import sys
   sys.path.insert(0, '/drive/src')

   import pyvista_js as pv
   from pyvista_js.examples import _GLTF_SAMPLE_BASE, _download_url

   _URL = f"{_GLTF_SAMPLE_BASE}/DamagedHelmet/glTF-Embedded/DamagedHelmet.gltf"
   gltf_path = _download_url(_URL, "DamagedHelmet.gltf")

   reader = pv.GLTFReader(gltf_path)
   mesh = reader.read()

   plotter = pv.Plotter()
   plotter.add_mesh(mesh, pbr=True, metallic=0.5, roughness=0.3)
   plotter.view_isometric()
   plotter.show()
```

### Using download_damaged_helmet

```{eval-rst}
.. replite::
   :kernel: pyolite
   :height: 600px

   import micropip
   await micropip.install("jinja2")

   import sys
   sys.path.insert(0, '/drive/src')

   import pyvista_js as pv
   from pyvista_js import examples

   mesh = examples.download_damaged_helmet()
   cubemap = examples.download_sky_box_cube_map()

   plotter = pv.Plotter()
   plotter.set_environment_texture(cubemap)
   plotter.add_mesh(mesh, pbr=True, metallic=0.5, roughness=0.3)
   plotter.view_isometric()
   plotter.show()
```

## Physically Based Rendering

```{eval-rst}
.. replite::
   :kernel: pyolite
   :height: 600px

   import micropip
   await micropip.install("jinja2")

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
