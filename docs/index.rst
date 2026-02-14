pyvista-js Documentation
========================

Welcome to pyvista-js documentation!

Overview
--------

pyvista-js is a PyVista-like API for vtk.js, bringing the intuitive PyVista interface to JavaScript-based 3D visualization.

Installation
------------

.. code-block:: bash

   pip install pyvista-js

Quick Start
-----------

.. replite::
   :kernel: pyolite
   :height: 600px

   import micropip
   await micropip.install('pyvista-js')

   import pyvista_js as pv

   # Test basic functionality
   print("pyvista-js imported successfully!")
   print(f"pyvista-js version: {pv.__version__ if hasattr(pv, '__version__') else 'unknown'}")

   # Try to create a simple sphere
   try:
       sphere = pv.Sphere()
       print(f"Sphere created: {sphere}")
   except Exception as e:
       print(f"Error creating sphere: {e}")
       import traceback
       traceback.print_exc()

Features
--------

- PyVista-like API for familiar usage
- Integration with vtk.js for web-based visualization
- Support for JupyterLite and Streamlit

Links
-----

- `GitHub Repository <https://github.com/tkoyama010/pyvista-js>`_
- `Issue Tracker <https://github.com/tkoyama010/pyvista-js/issues>`_
