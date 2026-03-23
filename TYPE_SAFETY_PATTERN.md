# Type Safety Pattern for pyvista-js

This document describes the "Plotly-like" specification pattern used for data transfer between Jinja2 templates and TypeScript fragments.

## Overview

The pattern separates concerns into:
- **Library** (TypeScript fragments): Clean, type-safe, testable functions
- **Config** (Jinja2 templates): Dynamic data injection as JSON

## Architecture

### 1. Type Definitions (`globals.d.ts`)

Define TypeScript interfaces for configuration objects:

```typescript
interface SphereSourceConfig {
  centerX: number;
  centerY: number;
  centerZ: number;
  radius: number;
  thetaResolution: number;
  phiResolution: number;
}

declare const CONFIG: SphereSourceConfig;
```

### 2. TypeScript Fragment (`.ts` file)

Pure JavaScript/TypeScript with no Jinja2 syntax:

```typescript
function createSphere(config) {
  const source = vtk.Filters.Sources.vtkSphereSource.newInstance({
    center: [config.centerX, config.centerY, config.centerZ],
    radius: config.radius,
    thetaResolution: config.thetaResolution,
    phiResolution: config.phiResolution,
  });
  const texMapSphere = vtk.Filters.Texture.vtkTextureMapToSphere.newInstance();
  texMapSphere.setInputConnection(source.getOutputPort());
  return { source, texMapSphere };
}

const { source: _source, texMapSphere: _texMapSphere } = createSphere(CONFIG);
```

### 3. Jinja2 Template (`.html` file)

Injects CONFIG and includes the TypeScript fragment:

```html
<script>
{
const CONFIG = {{ CONFIG }};
{% include "sphere_source.ts" %}
var {{ SOURCE }} = _source;
var {{ TEX_MAP_SPHERE }} = _texMapSphere;
}
</script>
```

### 4. Python Side (`mesh.py`)

Creates config dictionary and serializes to JSON:

```python
def _vtk_js_source(idx: int) -> str:
    config = {
        "centerX": center[0],
        "centerY": center[1],
        "centerZ": center[2],
        "radius": radius,
        "thetaResolution": theta_resolution,
        "phiResolution": phi_resolution,
    }
    return _render(
        _SPHERE_SOURCE_TEMPLATE,
        SOURCE=f"source{idx}",
        TEX_MAP_SPHERE=f"texMapSphere{idx}",
        CONFIG=json.dumps(config),
    )
```

## Benefits

1. **Type Safety**: IDE autocompletion and type checking in TypeScript fragments
2. **Maintainability**: Clear separation between data (Python) and logic (TypeScript)
3. **Formatting**: TypeScript files remain valid and can be formatted with Prettier
4. **Testability**: Functions can be tested independently
5. **Documentation**: Types serve as API documentation

## Implementation Status

- ✅ SphereSource: Fully refactored
- ⬜ Other sources: Can be migrated following the same pattern

## Reference Implementation

See:
- `globals.d.ts` - Type definitions
- `src/pyvista_js/templates/sphere_source.ts` - TypeScript fragment
- `src/pyvista_js/templates/sphere_source.html` - Jinja2 template
- `src/pyvista_js/mesh.py` (Sphere function) - Python implementation
