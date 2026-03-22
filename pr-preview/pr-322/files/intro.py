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
# # PyVista-js Introduction
#
# This notebook demonstrates the simplified PyVista-js API that works in JupyterLite.
#
# 🌐 **[Try the Streamlit App](../stlite/index.html)** - Interactive 3D visualization with Streamlit!

# %%
import micropip

await micropip.install("pyvista-js")

# %%
import pyvista_js as pv
from pyvista_js import examples

plotter = pv.Plotter()
mesh = examples.download_bunny()
plotter.add_mesh(mesh)
plotter.show()
