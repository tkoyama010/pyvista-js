Mesh
====

.. autoclass:: pyvista_js.Mesh
   :members:
   :undoc-members:
   :show-inheritance:

.. autofunction:: pyvista_js.Sphere

Interactive Example
-------------------

.. replite::
   :kernel: pyolite
   :height: 500px

   import sys
   sys.path.insert(0, '/drive/src')
   import pyvista_js as pv

   plotter = pv.Plotter()
   plotter.add_mesh(pv.Sphere(radius=1.0), color='cyan')
   plotter.show()

.. autofunction:: pyvista_js.Cube

Interactive Example
-------------------

.. replite::
   :kernel: pyolite
   :height: 500px

   import sys
   sys.path.insert(0, '/drive/src')
   import pyvista_js as pv

   plotter = pv.Plotter()
   plotter.add_mesh(pv.Cube(), color='orange')
   plotter.show()

.. autofunction:: pyvista_js.Cylinder

Interactive Example
-------------------

.. replite::
   :kernel: pyolite
   :height: 500px

   import sys
   sys.path.insert(0, '/drive/src')
   import pyvista_js as pv

   plotter = pv.Plotter()
   plotter.add_mesh(pv.Cylinder(radius=0.5, height=2.0), color='green')
   plotter.show()
