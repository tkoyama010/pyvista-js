# Dual-Mode Support: Standard Server and WASM

This document explains how pyvista-js now supports both Standard Server (FastAPI) and WASM-based (JupyterLite/stlite) environments through abstracted data access and type-safe configuration.

## Overview

The implementation provides:

1. **Abstract Data Access**: Decouples TypeScript rendering logic from how data is fetched
2. **Standard Server Path**: Supports Jinja2 `tojson` injection for server-side rendering
3. **WASM Path**: TypeScript code can be invoked via JavaScript bridge (like Pyodide) using `initViewer(config)`
4. **Type Safety**: OpenAPI-compatible interfaces shared between Python (TypedDict) and TypeScript

## Architecture

### Type Definitions

**TypeScript** (`src/pyvista_js/templates/globals.d.ts`):
```typescript
export interface ViewerConfig {
  containerId: string;
  backgroundColor?: RGBColor;
  width?: number;
  height?: number;
  actors?: ActorConfig[];
  lights?: LightConfig[];
  camera?: CameraConfig;
  // ... more options
}
```

**Python** (`src/pyvista_js/config_types.py`):
```python
class ViewerConfig(TypedDict, total=False):
    containerId: str
    backgroundColor: RGBColor
    width: float
    height: float
    actors: list[ActorConfig]
    lights: list[LightConfig]
    camera: CameraConfig
    # ... more options
```

### Core Function

The `initViewer(config)` function in `viewer_init.ts` initializes a vtk.js viewer from a configuration object. It works in both modes:

1. **Server Mode**: Config is generated from Jinja2 templates
2. **WASM Mode**: Config is passed programmatically from Python

## Usage Examples

### 1. Standard Server Mode (Backward Compatible)

This is the existing mode that continues to work without changes:

```python
from pyvista_js import Sphere
from pyvista_js.rendering import get_renderer

# Create renderer and add mesh
renderer = get_renderer()
sphere = Sphere()
renderer.add_mesh_actor(sphere, color='red', opacity=0.8)

# Render using Jinja2 templates (existing behavior)
renderer.render()
```

The renderer generates HTML with embedded JavaScript using Jinja2 template variables.

### 2. WASM Mode (New)

For WASM environments like Pyodide, JupyterLite, or stlite:

```python
import json
from pyvista_js import Sphere
from pyvista_js.rendering import get_renderer

# Create renderer and add mesh
renderer = get_renderer()
sphere = Sphere()
renderer.add_mesh_actor(sphere, color='red', opacity=0.8)

# Generate configuration object
config = renderer.generate_config_object()

# Serialize to JSON
json_config = json.dumps(config)

# Pass to JavaScript
from js import initViewer  # In Pyodide environment
import js
config_js = js.JSON.parse(json_config)
initViewer(config_js)
```

### 3. FastAPI Server Example

Using the config object with FastAPI for server-side rendering:

```python
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pyvista_js import Sphere
from pyvista_js.rendering import MockRenderer

app = FastAPI()

@app.get("/viewer")
def get_viewer():
    # Create visualization
    renderer = MockRenderer()
    sphere = Sphere()
    renderer.add_mesh_actor(sphere, color='blue')

    # Generate config as JSON
    config = renderer.generate_config_object()

    # Return HTML with config embedded
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://unpkg.com/vtk.js@29.5.0"></script>
        <script>
            const PYVISTA_CONFIG = {json.dumps(config)};
        </script>
    </head>
    <body>
        <div id="pyvista-container"></div>
        <script>
            // Use the dual-mode template or initViewer directly
            if (typeof initViewer !== 'undefined') {{
                initViewer(PYVISTA_CONFIG);
            }}
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html)
```

## Configuration Object Structure

The config object includes all necessary data for rendering:

```python
{
    "containerId": "pyvista-container",
    "backgroundColor": {"r": 1.0, "g": 1.0, "b": 1.0},
    "vtkjsCdnUrl": "https://unpkg.com/vtk.js@29.5.0",
    "actors": [
        {
            "sourceCode": "const _source0 = vtk.Filters.Sources.vtkSphereSource.newInstance({...});",
            "color": {"r": 1.0, "g": 0.0, "b": 0.0},
            "opacity": 0.8,
            "style": "surface",
            "smoothShading": True,
            "pbr": False,
            # ... more actor properties
        }
    ],
    "lights": [
        {
            "position": {"x": 1.0, "y": 1.0, "z": 1.0},
            "focalPoint": {"x": 0.0, "y": 0.0, "z": 0.0},
            "intensity": 1.0,
            "color": {"r": 1.0, "g": 1.0, "b": 1.0}
        }
    ],
    "camera": {
        "position": {"x": 0.0, "y": 0.0, "z": 5.0},
        "focalPoint": {"x": 0.0, "y": 0.0, "z": 0.0},
        "viewUp": {"x": 0.0, "y": 1.0, "z": 0.0},
        "viewAngle": 30.0,
        "parallelProjection": False
    }
}
```

## Advantages

### 1. Separation of Concerns
- **Data Layer**: Python generates configuration data
- **Rendering Layer**: TypeScript handles vtk.js rendering
- No tight coupling between layers

### 2. Flexibility
- **Server-side**: Pre-render config in Jinja2 templates
- **Client-side**: Generate config dynamically in WASM
- **Hybrid**: Mix both approaches as needed

### 3. Type Safety
- **Python**: TypedDict provides IDE autocomplete and type checking
- **TypeScript**: Interfaces ensure type correctness
- **OpenAPI**: Can generate API schemas from Python types

### 4. Testing
- Config objects are easy to test (just dictionaries)
- No need to parse HTML/JavaScript in tests
- Can mock/stub configurations easily

## Implementation Details

### Files Modified/Created

1. **`src/pyvista_js/templates/globals.d.ts`**
   - TypeScript interface definitions
   - Compatible with OpenAPI generation

2. **`src/pyvista_js/templates/viewer_init.ts`**
   - Core `initViewer(config)` function
   - Works in both browser and WASM environments

3. **`src/pyvista_js/templates/rendering_dual_mode.html`**
   - Template that checks for `PYVISTA_CONFIG` global
   - Falls back to traditional Jinja2 mode if not present

4. **`src/pyvista_js/config_types.py`**
   - Python type definitions mirroring TypeScript
   - Helper functions for conversion

5. **`src/pyvista_js/rendering.py`**
   - Added `generate_config_object()` method to `_BaseHTMLRenderer`
   - Added `generate_config_object()` method to `MockRenderer`

### Backward Compatibility

All existing code continues to work without changes. The new functionality is additive:

- Existing templates still work
- `renderer.render()` behaves the same
- No breaking changes to the API

### Testing

Comprehensive test coverage in `tests/test_config_generation.py`:

- Basic config generation ✓
- Actor properties ✓
- Multiple actors ✓
- PBR properties ✓
- Camera configuration ✓
- Lights configuration ✓
- JSON serialization ✓
- Type conversion utilities ✓

All 533 existing tests pass, confirming backward compatibility.

## Future Enhancements

Possible future improvements:

1. **Pydantic Models**: Replace TypedDict with Pydantic for validation and OpenAPI generation
2. **Streaming**: Support streaming large mesh data instead of embedding in config
3. **WebSocket**: Real-time updates for interactive applications
4. **Binary Protocol**: Use binary format (MessagePack, Protocol Buffers) for efficiency
5. **Code Splitting**: Lazy load vtk.js modules based on config requirements

## Migration Guide

### For Existing Code

No changes needed! Your existing code will continue to work.

### To Use New Features

Add one line to use config generation:

```python
# Before (still works)
renderer.render()

# New option (for WASM/API)
config = renderer.generate_config_object()
```

## Conclusion

The dual-mode support provides a clean architecture for both server-side and WASM-based rendering, with type safety and backward compatibility. The abstraction layer allows pyvista-js to work seamlessly in diverse environments while maintaining a consistent Python API.
