Plotter
=======

.. autoclass:: pyvista_js.Plotter
   :members:
   :undoc-members:
   :show-inheritance:

Interactive Example
-------------------

.. replite::
   :kernel: pyolite
   :height: 500px

   import sys
   sys.path.insert(0, '/drive/src')
   import pyvista_js as pv

   plotter = pv.Plotter()
   plotter.add_mesh(pv.Sphere(), color='red')
   plotter.show()
