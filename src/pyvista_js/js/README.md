# JavaScript Templates

This directory contains JavaScript and HTML templates used by pyvista-js to generate vtk.js visualizations.

## Files

- **rendering.html** - Main HTML template for vtk.js rendering in IPython/Jupyter
- **actor.js** - Template for creating vtk.js actors (renderer objects)
- **mesh_source.js** - Template for generic mesh polydata sources
- **sphere_source.js** - Template for vtk.js sphere sources
- **cube_source.js** - Template for vtk.js cube sources
- **cylinder_source.js** - Template for vtk.js cylinder sources
- **streamlit.html** - Complete HTML template for Streamlit integration

## Template Variables

Templates use a simple `{{VARIABLE}}` placeholder syntax that is replaced by Python code:

### Common Variables
- `{{INDEX}}` - Index of the mesh/actor in the rendering pipeline
- `{{COLOR_R}}`, `{{COLOR_G}}`, `{{COLOR_B}}` - RGB color components (0-1)
- `{{OPACITY}}` - Opacity value (0-1)

### Mesh-Specific Variables
- `{{CENTER_X}}`, `{{CENTER_Y}}`, `{{CENTER_Z}}` - Center coordinates
- `{{RADIUS}}` - Radius for sphere/cylinder
- `{{HEIGHT}}` - Height for cylinder
- `{{X_LENGTH}}`, `{{Y_LENGTH}}`, `{{Z_LENGTH}}` - Dimensions for cube
- `{{THETA_RESOLUTION}}`, `{{PHI_RESOLUTION}}` - Resolution for sphere
- `{{RESOLUTION}}` - Resolution for cylinder
- `{{POINTS_DATA}}` - Flattened point data for generic meshes

### Rendering Variables
- `{{CONTAINER_ID}}` - HTML element ID for the visualization container
- `{{BACKGROUND_R}}`, `{{BACKGROUND_G}}`, `{{BACKGROUND_B}}` - Background color
- `{{ACTORS_CODE}}` - Combined JavaScript code for all actors
- `{{SOURCE_CODE}}` - JavaScript code for mesh source
- `{{MAPPER_SETUP}}` - JavaScript code to configure the mapper

## Usage

Templates are loaded at module import time and stored as module-level constants:

```python
from pathlib import Path

_JS_DIR = Path(__file__).parent / "js"
_RENDERING_TEMPLATE = (_JS_DIR / "rendering.html").read_text()
```

Then they are populated with values using `.replace()`:

```python
html = _RENDERING_TEMPLATE.replace("{{CONTAINER_ID}}", container_id)
```

## Modifying Templates

When modifying these templates:

1. Keep the placeholder syntax consistent: `{{VARIABLE_NAME}}`
2. Ensure all placeholders are replaced in the Python code
3. Test changes with the existing test suite
4. Maintain vtk.js API compatibility
