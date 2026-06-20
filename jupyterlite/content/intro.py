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

# %%
import micropip

await micropip.install("pyvista-js")

sys.path.insert(0, "/drive/src")

# %%
import pyvista_js as pv
from pyvista_js import examples

plotter = pv.Plotter()
mesh = examples.download_bunny()
plotter.add_mesh(mesh)
plotter.show()
