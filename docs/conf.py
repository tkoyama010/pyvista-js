# Configuration file for the Sphinx documentation builder.  # noqa: INP001, D100
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

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
    "pyvista_js.ext",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_book_theme"
html_static_path = []

# -- Options for MyST parser -------------------------------------------------
myst_enable_extensions = [
    "colon_fence",
]
