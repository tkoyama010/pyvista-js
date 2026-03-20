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
import micropip

await micropip.install("jinja2")  # noqa: F704, PLE1142

import sys  # noqa: E402

sys.path.insert(0, "/drive/src")

# %%
import pyvista_js as pv  # noqa: E402
from pyvista_js import examples  # noqa: E402

plotter = pv.Plotter()
mesh = examples.download_bunny()
plotter.add_mesh(mesh)
plotter.show()
