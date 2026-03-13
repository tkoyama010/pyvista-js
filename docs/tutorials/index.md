# Tutorials

Topic driven themed lessons to help you get started with pyvista-js.

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
