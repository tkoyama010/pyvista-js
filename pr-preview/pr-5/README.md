# pyvista-js Demo

Live demo: [https://tkoyama010.github.io/pyvista-js/](https://tkoyama010.github.io/pyvista-js/)

## About

This demo showcases pyvista-js running in stlite (serverless Streamlit).

The demo runs entirely in your browser using:
- **Pyodide**: Python in WebAssembly
- **stlite**: Serverless Streamlit
- **pyvista-js**: PyVista-like API for vtk.js

## Files

- `index.html`: stlite mountable entry point
- `app.py`: Streamlit application code

## Local Development

To run the demo locally:

```bash
# Serve the demo directory
python -m http.server 8000 --directory demo

# Open http://localhost:8000
```

Or from repository root:

```bash
cd demo
python -m http.server 8000
```

## Deployment

The demo is automatically deployed to GitHub Pages when changes are pushed to the main branch.

See `.github/workflows/deploy-demo.yml` for deployment configuration.
