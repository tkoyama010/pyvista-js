# Electron Window Output for Non-Notebook Environments

## Overview

The Electron renderer enables desktop window visualization for pyvista-js when running in standard Python environments (not in Jupyter notebooks). This provides a familiar desktop application experience for 3D visualization using Electron + vtk.js.

## Features

- **Desktop Window Output**: Opens a native desktop window for visualization
- **Interactive 3D Rendering**: Full vtk.js rendering with mouse controls
- **Automatic Installation**: Electron is installed automatically via npm on first use
- **Fallback Support**: Falls back to opening HTML in default browser if Electron/Node.js is not available
- **No Server Required**: Pure client-side rendering in Electron

## Requirements

- **Node.js**: Must be installed on your system
- **Electron**: Installed automatically on first use via npm

### Installing Node.js

#### macOS
```bash
brew install node
```

#### Ubuntu/Debian
```bash
sudo apt-get install nodejs npm
```

#### Windows
Download from: https://nodejs.org/

## Usage

### Basic Example

```python
import os
os.environ['PYVISTA_JS_BACKEND'] = 'electron'

import pyvista_js as pv

# Create a plotter
plotter = pv.Plotter()

# Add a mesh
sphere = pv.Sphere()
plotter.add_mesh(sphere, color='red', opacity=0.8)

# Display in Electron window
plotter.show()
```

### Multiple Meshes

```python
import os
os.environ['PYVISTA_JS_BACKEND'] = 'electron'

import pyvista_js as pv

plotter = pv.Plotter()

# Add multiple meshes
sphere = pv.Sphere(radius=1.0, center=(0, 0, 0))
plotter.add_mesh(sphere, color='red')

cube = pv.Cube(center=(3, 0, 0))
plotter.add_mesh(cube, color='green')

cylinder = pv.Cylinder(center=(-3, 0, 0))
plotter.add_mesh(cylinder, color='blue')

# Set background
plotter.background_color = 'white'

# Show in Electron window
plotter.show()
```

See `examples/electron_window.py` for a complete example.

## Mouse Controls

When the Electron window is open, you can interact with the visualization:

- **Left Mouse Button**: Rotate the camera around the scene
- **Middle Mouse Button**: Pan the camera
- **Right Mouse Button**: Zoom in/out
- **Mouse Wheel**: Zoom in/out

## Troubleshooting

### "Node.js not found" Warning

If you see this warning, Node.js is not installed or not in your PATH. Install Node.js from https://nodejs.org/ and ensure it's in your system PATH.

### Fallback to Browser

If Electron cannot be launched, pyvista-js will automatically fall back to opening the visualization in your default web browser.

## License

The Electron renderer is part of pyvista-js and is licensed under BSD-3-Clause.
