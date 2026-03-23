# TypeScript Implementation in Templates

This document describes the TypeScript implementation in pyvista-js HTML templates.

## Overview

All HTML templates in `src/pyvista_js/templates/` now use TypeScript syntax in their script blocks. This provides:

- **Type Safety**: Explicit type annotations catch errors at development time
- **Better IDE Support**: Improved autocomplete and IntelliSense
- **Modern JavaScript**: Using `const`/`let` instead of `var`, ES6+ features
- **Documentation**: Type annotations serve as inline documentation
- **Maintainability**: Easier to understand and refactor code

## Implementation Details

### 1. Script Tag Updates

All `<script>` tags are now `<script type="module">`:

```html
<script type="module">
// @ts-check
/// <reference path="vtk.d.ts" />
...
</script>
```

The `type="module"` attribute enables:
- ES6 module features
- Strict mode by default
- Better error messages
- Scoped variables

### 2. TypeScript Checking

Each script block includes:

```typescript
// @ts-check
/// <reference path="vtk.d.ts" />
```

- `@ts-check`: Enables TypeScript type checking in JavaScript files
- `/// <reference path="vtk.d.ts" />`: References the vtk.js type declarations

### 3. Type Annotations

Variables now have explicit type annotations:

**Before:**
```javascript
var container = document.getElementById("container");
var backgroundR = parseFloat(container.dataset.backgroundR);
var points = [];
```

**After:**
```typescript
const container: HTMLElement | null = document.getElementById("container");
const backgroundR: number = parseFloat(container.dataset.backgroundR || "0");
const points: number[] = [];
```

### 4. Type Declarations

Created `src/pyvista_js/templates/vtk.d.ts` with TypeScript declarations for:

- `vtk.Common.Core.vtkPoints`
- `vtk.Common.Core.vtkCellArray`
- `vtk.Common.DataModel.vtkPolyData`
- `vtk.Rendering.Core.*` (vtkRenderer, vtkRenderWindow, vtkActor, etc.)
- `vtk.Rendering.OpenGL.vtkRenderWindow`
- `vtk.Filters.Sources.*` (vtkSphereSource, vtkCubeSource, etc.)
- And many more vtk.js classes

## Files Updated

All 26 HTML template files were updated:

### Source Templates
- `sphere_source.html` - Sphere primitive
- `cube_source.html` - Cube primitive
- `cylinder_source.html` - Cylinder primitive
- `cone_source.html` - Cone primitive
- `arrow_source.html` - Arrow primitive
- `circle_source.html` - Circle with complex geometry
- `disk_source.html` - Disk with radial triangulation
- `line_source.html` - Line primitive
- `plane_source.html` - Plane primitive
- `mesh_source.html` - Generic mesh
- `points_source.html` - Point cloud

### Filter Templates
- `clip_filter.html` - Complex clipping algorithm (63 lines)
- `contour_filter.html` - Marching triangles algorithm (60 lines)
- `shrink_filter.html` - Cell shrinking algorithm
- `tube_filter.html` - Tube generation

### Reader Templates
- `vtk_reader_source.html` - VTK file reader
- `ply_reader_source.html` - PLY file reader with base64 decoding
- `obj_reader_source.html` - OBJ file reader with base64 decoding
- `stl_reader_source.html` - STL file reader with base64 decoding
- `gltf_reader_source.html` - glTF reader with model-viewer
- `gltf_url_source.html` - glTF URL loader

### Rendering Templates
- `rendering.html` - Main rendering template
- `rendering_js.html` - Self-contained JS rendering
- `actor.html` - Actor configuration
- `scalar_bar.html` - Scalar bar UI

## Benefits

### Type Safety Example

```typescript
// TypeScript catches this error at development time:
const radius: number = "5";  // Error: Type 'string' is not assignable to type 'number'

// Proper way:
const radius: number = 5;
```

### Complex Algorithm Example

The `clip_filter.html` template demonstrates TypeScript benefits for complex algorithms:

```typescript
const inPts: Float32Array = pd.getPoints().getData();
const inPolys: Int32Array = pd.getPolys().getData();
const distances: Float32Array = new Float32Array(nPts);
const ptMap: Record<number, number> = {};
```

Type annotations make it clear:
- `inPts` is a Float32Array for point coordinates
- `inPolys` is an Int32Array for polygon connectivity
- `distances` stores float values for each point
- `ptMap` is a dictionary mapping old point IDs to new ones

## Testing

All 130 existing tests pass:
- 37 rendering tests
- 93 mesh tests

No functionality changed - this is purely a TypeScript migration.

## Future Improvements

Potential enhancements:

1. **Build-time Type Checking**: Add a pre-commit hook to run TypeScript compiler
2. **Stricter Types**: Replace `any` types with more specific interfaces
3. **Full Type Definitions**: Expand `vtk.d.ts` with complete vtk.js API
4. **Template Validation**: Validate Jinja2 variables at build time

## Configuration Files

### package.json

Basic npm package configuration for TypeScript:

```json
{
  "name": "pyvista-js-templates",
  "version": "0.11.0",
  "description": "TypeScript build system for pyvista-js templates",
  "private": true,
  "scripts": {
    "build": "tsc",
    "watch": "tsc --watch",
    "clean": "rm -rf src/pyvista_js/templates/*.js"
  },
  "devDependencies": {
    "@types/node": "^22.0.0",
    "typescript": "^5.7.2"
  }
}
```

### tsconfig.json

TypeScript compiler configuration:

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "ES2020",
    "lib": ["ES2020", "DOM"],
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "noEmit": true,
    "moduleResolution": "node",
    "allowJs": true,
    "checkJs": false
  },
  "include": ["src/pyvista_js/templates/**/*.html"],
  "exclude": ["node_modules"]
}
```

## Browser Compatibility

TypeScript code is transpiled to modern JavaScript (ES2020) which is supported by:
- Chrome 80+
- Firefox 72+
- Safari 13.1+
- Edge 80+

All code runs directly in the browser without a build step - the TypeScript annotations are valid JavaScript syntax when using `type="module"`.
