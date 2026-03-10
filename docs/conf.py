# Configuration file for the Sphinx documentation builder.  # noqa: INP001, D100
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import shutil
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

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "pyvista-js"
copyright = "2024, Tetsuo Koyama"  # noqa: A001
author = "Tetsuo Koyama"
release = "0.2.dev0"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "myst_parser",
    "jupyterlite_sphinx",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
]

# -- Options for autodoc -----------------------------------------------------
autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "show-inheritance": True,
}
autosummary_generate = False

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_book_theme"
html_static_path = []

# -- Options for MyST parser -------------------------------------------------
myst_enable_extensions = [
    "colon_fence",
    "deflist",
]

# -- Options for jupyterlite-sphinx ------------------------------------------
jupyterlite_dir = ".jupyterlite"
jupyterlite_contents = ["content"]
