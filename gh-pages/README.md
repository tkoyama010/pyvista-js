# GitHub Pages Structure

This directory contains the source files for the pyvista-js GitHub Pages site.

## Structure

The GitHub Pages site is organized into the following structure:

- **`/`** (root) - Landing page with links to JupyterLite and Stlite demos
- **`/jupyterlite/`** - Full JupyterLite environment (built from `jupyterlite/` directory)
- **`/stlite/`** - Standalone Stlite demo page

## Files

- `index.html` - Main landing page
- `stlite/index.html` - Stlite demo page (standalone, using stlite CDN)

## Deployment

The site is deployed via the `.github/workflows/deploy-jupyterlite.yml` workflow, which:

1. Builds JupyterLite and outputs to `_site/jupyterlite/`
2. Copies the landing page to `_site/index.html`
3. Copies the Stlite demo to `_site/stlite/index.html`
4. Deploys the entire `_site/` directory to the `gh-pages` branch

## URLs

When deployed, the site is accessible at:

- Landing page: `https://tkoyama010.github.io/pyvista-js/`
- JupyterLite: `https://tkoyama010.github.io/pyvista-js/jupyterlite/`
- Stlite demo: `https://tkoyama010.github.io/pyvista-js/stlite/`
