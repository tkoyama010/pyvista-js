Examples
========

.. autoclass:: pyvista_js.examples.CubeMap
   :members:
   :undoc-members:
   :show-inheritance:

.. autofunction:: pyvista_js.examples.download_sky_box_cube_map

Interactive Example
-------------------

.. replite::
   :kernel: pyolite
   :height: 500px

   import sys
   sys.path.insert(0, '/drive/src')
   import pyvista_js as pv
   from pyvista_js import examples

   cubemap = examples.download_sky_box_cube_map()
   plotter = pv.Plotter()
   plotter.set_environment_texture(cubemap)
   plotter.add_mesh(pv.Sphere(), color='white', pbr=True, metallic=0.8, roughness=0.1)
   plotter.show()
