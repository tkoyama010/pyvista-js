# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.1
#   kernelspec:
#     display_name: Python (Pyodide)
#     language: python
#     name: python
# ---

# %% [markdown]
# # PyVista-js Simple Demo
#
# This notebook demonstrates the simplified PyVista-js API that works in JupyterLite.

# %%
import sys

sys.path.insert(0, "/drive/src")

# %%
import pyvista_js as pv

plotter = pv.Plotter()
mesh = pv.Sphere()
plotter.add_mesh(mesh, color="red", opacity=0.8)
plotter.show()
