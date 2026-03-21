# Configuration file for the Sphinx documentation builder.  # noqa: INP001, D100
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

# Copy source code to JupyterLite content directory
docs_dir = Path(__file__).parent
project_root = docs_dir.parent
src_dir = project_root / "src" / "pyvista_js"
content_dir = docs_dir / "content" / "src"

# Create content directory and copy source
content_dir.mkdir(parents=True, exist_ok=True)
dest_dir = content_dir / "pyvista_js"
if dest_dir.exists():
    shutil.rmtree(dest_dir)
shutil.copytree(src_dir, dest_dir)

# Configure JupyterLite to pre-load jinja2 and set up sys.path
# so that examples work without explicit micropip or sys.path calls.
_jupyterlite_config = docs_dir / "content" / "jupyter-lite.json"
_jupyterlite_config.write_text(
    json.dumps(
        {
            "jupyter-lite-schema-version": 0,
            "jupyter-config-data": {
                "litePluginSettings": {
                    "@jupyterlite/pyodide-kernel-extension:kernel": {
                        "loadPyodideOptions": {"packages": ["Jinja2"]},
                        "pipliteUrls": [],
                    },
                },
            },
        },
        indent=2,
    )
    + "\n",
)

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "pyvista-js"
copyright = "2024, Tetsuo Koyama"  # noqa: A001
author = "Tetsuo Koyama"
release = "0.2.dev0"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "atsphinx.stlite",
    "myst_parser",
    "jupyterlite_sphinx",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinxcontrib.typer",
    "sphinx_design",
]

# -- Options for autodoc -----------------------------------------------------
autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "show-inheritance": True,
}
autosummary_generate = True

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# Suppress warnings for missing cross-references in included README
# and pre-existing duplicate object description warnings
suppress_warnings = [
    "myst.xref_missing",
    "app.add_directive",  # Suppress duplicate object warnings
]

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_book_theme"
html_static_path = ["_static"]
html_css_files = ["custom.css"]

# -- Options for MyST parser -------------------------------------------------
myst_enable_extensions = [
    "colon_fence",
    "deflist",
]

# -- Options for jupyterlite-sphinx ------------------------------------------
jupyterlite_dir = ".jupyterlite"
jupyterlite_contents = ["content"]
global_enable_try_examples = True
try_examples_global_warning_text = (
    "pyvista-js's interactive examples are experimental and may not always work as expected."
)
try_examples_preamble = (
    "import micropip\n"
    "await micropip.install('jinja2')\n"
    "await micropip.install('lazy-loader')\n"
    "import sys\n"
    "sys.path.insert(0, '/drive/src')\n"
    "import pyvista_js as pv\n"
)

# -- Build development wheel for stlite demo --------------------------------
_wheel_dir = docs_dir / "_static"
subprocess.run(  # noqa: S603
    [sys.executable, "-m", "pip", "wheel", "--no-deps", "-w", str(_wheel_dir), str(project_root)],
    check=True,
)
_wheel_files = list(_wheel_dir.glob("pyvista_js-*.whl"))
_rtd_url = os.environ.get("READTHEDOCS_CANONICAL_URL", "")
stlite_wheel_url = f"{_rtd_url}_static/{_wheel_files[0].name}" if _wheel_files else ""

# Generate stlite demo page with the correct wheel URL
_stlite_demo = docs_dir / "stlite_demo.md"
_stlite_demo.write_text(f"""\
# stlite Demo

This is an interactive demo using [stlite](https://github.com/whitphx/stlite),
the WASM-powered in-browser version of Streamlit.

```{{eval-rst}}
.. stlite::
   :requirements: {stlite_wheel_url}

   import streamlit as st
   import streamlit.components.v1 as components

   import pyvista_js as pv

   st.title("pyvista-js Demo")

   geometry = st.selectbox("Geometry", ["Sphere", "Cube", "Cylinder"])

   color = st.selectbox("Color", ["red", "green", "blue", "yellow", "cyan", "magenta"])

   opacity = st.slider("Opacity", min_value=0.0, max_value=1.0, value=0.8, step=0.1)

   plotter = pv.Plotter()

   if geometry == "Sphere":
       mesh = pv.Sphere(radius=1.0)
   elif geometry == "Cube":
       mesh = pv.Cube()
   else:
       mesh = pv.Cylinder(radius=0.5, height=2.0)

   plotter.add_mesh(mesh, color=color, opacity=opacity)

   html = plotter._renderer._generate_standalone_html()
   components.html(html, height=600)
```
""")
