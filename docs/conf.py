# Configuration file for the Sphinx documentation builder.  # noqa: INP001, D100
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import subprocess
from pathlib import Path

# Build wheel for JupyterLite
try:
    docs_dir = Path(__file__).parent
    project_root = docs_dir.parent
    pypi_dir = docs_dir / ".jupyterlite" / "pypi"
    pypi_dir.mkdir(parents=True, exist_ok=True)

    subprocess.run(  # noqa: S603
        ["python", "-m", "build", "--wheel", "--outdir", str(pypi_dir)],  # noqa: S607
        cwd=project_root,
        check=True,
        capture_output=True,
    )
except Exception:  # noqa: BLE001, S110
    # Fail silently - wheel may already exist or build may not be needed
    pass

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
    "deflist",
]

# -- Options for jupyterlite-sphinx ------------------------------------------
jupyterlite_config = "jupyterlite_config.json"
jupyterlite_dir = ".jupyterlite"
jupyterlite_contents = []
