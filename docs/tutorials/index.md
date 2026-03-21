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
   from IPython.display import HTML, display

   _URL = f"{_GLTF_SAMPLE_BASE}/DamagedHelmet/glTF-Embedded/DamagedHelmet.gltf"
   gltf_path = _download_url(_URL, "DamagedHelmet.gltf")

   reader = pv.GLTFReader(gltf_path)
   mesh = reader.read()
   print(f"Loaded GLTF mesh with {mesh.n_points} vertices")

   display(HTML(f"""
   <script type="module" src="https://unpkg.com/@google/model-viewer@3.4.0/dist/model-viewer.min.js"></script>
   <model-viewer src="{_URL}" camera-controls auto-rotate
     style="width:600px;height:400px;border:2px solid #333;display:block;">
   </model-viewer>
   """))
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
   from pyvista_js.examples import _GLTF_SAMPLE_BASE
   from IPython.display import HTML, display

   mesh = examples.download_damaged_helmet()
   print(f"Loaded GLTF mesh with {mesh.n_points} vertices")

   _URL = f"{_GLTF_SAMPLE_BASE}/DamagedHelmet/glTF-Embedded/DamagedHelmet.gltf"
   display(HTML(f"""
   <script type="module" src="https://unpkg.com/@google/model-viewer@3.4.0/dist/model-viewer.min.js"></script>
   <model-viewer src="{_URL}" camera-controls auto-rotate
     style="width:600px;height:400px;border:2px solid #333;display:block;">
   </model-viewer>
   """))
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
