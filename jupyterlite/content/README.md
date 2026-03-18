# JupyterLite Content

This directory contains demo notebooks for the pyvista-js JupyterLite environment.

## Working with Notebooks

The notebooks in this directory are managed using [jupytext](https://jupytext.readthedocs.io/), which allows us to maintain Python scripts as the source of truth while automatically generating the `.ipynb` notebook files.

### Source Files

- `*.py` - Python scripts in [percent format](https://jupytext.readthedocs.io/en/latest/formats-scripts.html) (version controlled)
- `*.ipynb` - Generated notebook files (gitignored, auto-generated from `.py` files)

### Editing Notebooks

To edit a notebook:

1. Edit the `.py` file directly (e.g., `simple_demo.py`)
1. Sync to generate the `.ipynb` file:
   ```bash
   jupytext --sync jupyterlite/content/*.py
   ```

The `.ipynb` files are automatically generated during the CI build process and should not be committed to the repository.

### Why Jupytext?

Using jupytext provides several benefits:

- **Clean diffs**: Python scripts produce much cleaner git diffs than JSON-based `.ipynb` files
- **Easy review**: Code changes are easier to review as plain Python
- **No output noise**: Output cells and execution metadata don't clutter version control
- **Standard Python tooling**: Python scripts work with linters, formatters, and other Python tools

### Configuration

Jupytext pairing is configured in `pyproject.toml`:

```toml
[tool.jupytext]
formats = "ipynb,py:percent"
```

This tells jupytext to maintain both `.ipynb` and `.py` files in sync, with the `.py` file using the percent format.
