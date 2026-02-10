"""vtk.js rendering backend for pyvista-js.

This module provides the JavaScript bridge to vtk.js for rendering
in Pyodide/browser environments.

Architecture
------------
pyvista-js uses a backend abstraction to support multiple environments:

1. **VTKJSRenderer**: Used in Pyodide/browser with vtk.js for WebGL rendering
2. **MockRenderer**: Used in standard Python for development/testing

Environment Detection
---------------------
The library automatically detects the runtime:

>>> import sys
>>> PYODIDE_ENV = sys.platform == "emscripten"  # True in Pyodide

If running in Pyodide and vtk.js is available, VTKJSRenderer is used.
Otherwise, MockRenderer provides a fallback for testing.

Data Conversion
---------------
NumPy arrays are converted to JavaScript for vtk.js:

>>> # Python NumPy array (n, 3)
>>> points = mesh.points
>>>
>>> # Convert to JavaScript flat array
>>> points_js = points.flatten().tolist()
>>> polydata.getPoints().setData(points_js, 3)

Loading vtk.js
--------------
vtk.js is automatically loaded when VTKJSRenderer is initialized in
IPython/Jupyter environments. No manual script loading required.

For manual loading or custom versions:

.. code-block:: html

    <script src="https://unpkg.com/vtk.js"></script>
    <script>
      window.vtk = vtk;  // Expose to global scope
    </script>

Examples
--------
Using the renderer (automatically selected):

>>> from pyvista_js.rendering import get_renderer
>>> from pyvista_js import Sphere
>>>
>>> renderer = get_renderer()
>>> mesh = Sphere()
>>> renderer.add_mesh_actor(mesh, color='red', opacity=0.8)
>>> renderer.create_container('viz-container')
>>> renderer.render()

In Pyodide environment, this uses vtk.js. In standard Python,
it uses MockRenderer which prints debug output.

"""

from __future__ import annotations

import json
import logging
import os
import subprocess
import sys
import tempfile
import time
import webbrowser
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing_extensions import Self

    from .mesh import Mesh

# Check if running in Pyodide environment
PYODIDE_ENV = sys.platform == "emscripten"

if PYODIDE_ENV:
    try:
        from js import document  # type: ignore[import-not-found]

        VTK_AVAILABLE = True
    except ImportError:
        VTK_AVAILABLE = False
        document = None  # type: ignore[assignment]
else:
    VTK_AVAILABLE = False
    document = None  # type: ignore[assignment]

# Check if IPython is available
try:
    from IPython.display import HTML, display

    IPYTHON_AVAILABLE = True
except ImportError:
    IPYTHON_AVAILABLE = False


class _VTKJSLoader:
    """Singleton class to manage vtk.js library loading."""

    _instance: _VTKJSLoader | None = None
    _loaded: bool = False

    def __new__(cls) -> Self:
        """Ensure singleton instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def load(self) -> None:
        """Load vtk.js library in IPython/Jupyter/Pyodide environment.

        This function automatically loads the vtk.js library from unpkg CDN
        when working in Jupyter notebooks or JupyterLite. It only loads the
        library once per session and waits for it to be available.
        """
        if self._loaded:
            return

        if IPYTHON_AVAILABLE:
            try:
                display(
                    HTML("""
<script src="https://unpkg.com/vtk.js@29.5.0"></script>
"""),
                )
                # Wait for vtk.js to load from CDN
                time.sleep(2)
                self._loaded = True
            except NameError:
                # display/HTML not available (e.g., in tests)
                pass
        elif PYODIDE_ENV and document is not None:
            # In pure Pyodide environment without IPython
            script = document.createElement("script")
            script.src = "https://unpkg.com/vtk.js@29.5.0"
            document.head.appendChild(script)
            # Wait for vtk.js to load from CDN
            time.sleep(2)
            self._loaded = True


logger = logging.getLogger(__name__)


class VTKJSRenderer:
    """Renderer using vtk.js for browser visualization.

    This class wraps vtk.js rendering components and provides
    a bridge between Python mesh data and JavaScript WebGL rendering.

    Notes
    -----
    This renderer can only be instantiated in a Pyodide environment
    with vtk.js loaded in the page. Use `get_renderer()` to automatically
    get the appropriate renderer for the current environment.

    The renderer creates standard vtk.js objects:
    - vtkRenderer: Scene renderer
    - vtkRenderWindow: Rendering window
    - vtkRenderWindowInteractor: User interaction handler

    Examples
    --------
    >>> # In Pyodide/browser environment
    >>> renderer = VTKJSRenderer()
    >>> renderer.create_container('my-viz')
    >>>
    >>> # Add a mesh
    >>> from pyvista_js import Sphere
    >>> mesh = Sphere()
    >>> actor = renderer.add_mesh_actor(mesh, color='blue')
    >>>
    >>> # Render the scene
    >>> renderer.render()

    """

    def __init__(self) -> None:
        """Initialize the vtk.js renderer.

        Automatically loads vtk.js library if in IPython/Jupyter environment.

        Raises
        ------
        RuntimeError
            If not running in Pyodide environment.
        ImportError
            If vtk.js is not available in the page.

        """
        if not PYODIDE_ENV and not IPYTHON_AVAILABLE:
            msg = "VTKJSRenderer requires either Pyodide environment or IPython"
            raise RuntimeError(msg)

        # Automatically load vtk.js in IPython/Jupyter (including Pyodide)
        if IPYTHON_AVAILABLE or PYODIDE_ENV:
            _VTKJSLoader().load()

        self.container = None
        self.actors = []
        self.use_ipython = IPYTHON_AVAILABLE
        self.background = (0.2, 0.3, 0.4)  # Default background color

    def create_container(self, element_id: str = "pyvista-container") -> object | None:
        """Create a DOM container for rendering.

        Creates a <div> element in the document and configures it for
        vtk.js rendering with mouse/touch interaction support.

        Parameters
        ----------
        element_id : str, default="pyvista-container"
            HTML element ID for the container.

        Returns
        -------
        container
            The created DOM element (if using direct DOM) or None (if using IPython).

        Examples
        --------
        >>> renderer = VTKJSRenderer()
        >>> container = renderer.create_container('my-visualization')

        """
        if self.use_ipython:
            # Store container ID for later HTML generation
            self.container_id = element_id
            return None
        # Create container div directly
        self.container = document.createElement("div")
        self.container.setAttribute("id", element_id)
        self.container.style.width = "100%"
        self.container.style.height = "600px"

        # Append to body
        document.body.appendChild(self.container)

        return self.container

    def add_mesh_actor(
        self,
        mesh: Mesh,
        color: str | tuple[float, float, float] | None = None,
        opacity: float = 1.0,
    ) -> dict[str, object]:
        """Add a mesh to the renderer.

        Converts a pyvista-js Mesh to vtk.js polydata and creates
        an actor for rendering.

        Parameters
        ----------
        mesh : Mesh
            The mesh object to render. Must have a `points` attribute
            containing an (n, 3) NumPy array of vertex coordinates.
        color : tuple or str, optional
            RGB color tuple (0-1) or color name ('red', 'blue', etc.).
            If None, uses default vtk.js coloring.
        opacity : float, default=1.0
            Opacity value between 0 (transparent) and 1 (opaque).

        Returns
        -------
        actor
            The vtk.js vtkActor object representing the mesh (or dict if using IPython).

        Examples
        --------
        >>> from pyvista_js import Sphere
        >>> mesh = Sphere(radius=2.0)
        >>> actor = renderer.add_mesh_actor(mesh, color='red', opacity=0.8)

        """
        # Store actor information for later rendering
        if isinstance(color, str):
            color = self._color_name_to_rgb(color)

        actor_info = {
            "mesh": mesh,
            "color": color,
            "opacity": opacity,
        }
        self.actors.append(actor_info)

        return actor_info

    def render(self) -> None:
        """Render the scene.

        Resets the camera to show all actors and triggers rendering.
        In IPython/Jupyter, generates and displays HTML with vtk.js code.

        Examples
        --------
        >>> renderer.render()  # Display the visualization

        """
        if self.use_ipython:
            # Generate HTML with JavaScript code
            html = self._generate_html()
            display(HTML(html))
        else:
            # Direct rendering
            self.renderer.resetCamera()
            self.render_window.render()

    def _generate_html(self) -> str:
        """Generate HTML and JavaScript for IPython display."""
        container_id = getattr(self, "container_id", "pyvista-container")

        # Generate JavaScript code for each actor
        actor_js_code = []
        for idx, actor_info in enumerate(self.actors):
            mesh = actor_info["mesh"]
            color = actor_info.get("color", (0.5, 0.5, 0.5))
            opacity = actor_info.get("opacity", 1.0)

            # Detect mesh type and get parameters
            mesh_type = getattr(mesh, "_mesh_type", None)
            params = getattr(mesh, "_params", {})

            # Convert mesh points to JavaScript array
            points_flat = mesh.points.flatten().tolist()
            "[" + ",".join(map(str, points_flat)) + "]"

            # Generate appropriate source based on mesh type
            if mesh_type == "Sphere":
                radius = params.get("radius", 1.0)
                center = params.get("center", (0, 0, 0))
                theta_res = params.get("theta_resolution", 30)
                phi_res = params.get("phi_resolution", 30)
                source_code = f"""
      const source{idx} = vtk.Filters.Sources.vtkSphereSource.newInstance({{
        center: [{center[0]}, {center[1]}, {center[2]}],
        radius: {radius},
        thetaResolution: {theta_res},
        phiResolution: {phi_res}
      }});"""
            elif mesh_type == "Cube":
                center = params.get("center", (0, 0, 0))
                x_len = params.get("x_length", 1.0)
                y_len = params.get("y_length", 1.0)
                z_len = params.get("z_length", 1.0)
                source_code = f"""
      const source{idx} = vtk.Filters.Sources.vtkCubeSource.newInstance({{
        center: [{center[0]}, {center[1]}, {center[2]}],
        xLength: {x_len},
        yLength: {y_len},
        zLength: {z_len}
      }});"""
            elif mesh_type == "Cylinder":
                center = params.get("center", (0, 0, 0))
                radius = params.get("radius", 0.5)
                height = params.get("height", 1.0)
                resolution = params.get("resolution", 100)
                source_code = f"""
      const source{idx} = vtk.Filters.Sources.vtkCylinderSource.newInstance({{
        center: [{center[0]}, {center[1]}, {center[2]}],
        radius: {radius},
        height: {height},
        resolution: {resolution}
      }});"""
            else:
                # Generic mesh using polydata
                points_str = ",".join(map(str, points_flat))
                source_code = f"""
      const points{idx} = new Float32Array([{points_str}]);
      const polydata{idx} = vtk.Common.DataModel.vtkPolyData.newInstance();
      polydata{idx}.getPoints().setData(points{idx}, 3);
      const source{idx} = polydata{idx};"""

            # Determine mapper setup based on mesh type
            if mesh_type in ["Sphere", "Cube", "Cylinder"]:
                mapper_setup = f"mapper{idx}.setInputConnection(source{idx}.getOutputPort());"
            else:
                mapper_setup = f"mapper{idx}.setInputData(source{idx});"

            actor_js_code.append(f"""{source_code}

      // Create mapper
      const mapper{idx} = vtk.Rendering.Core.vtkMapper.newInstance();
      {mapper_setup}

      // Create actor
      const actor{idx} = vtk.Rendering.Core.vtkActor.newInstance();
      actor{idx}.setMapper(mapper{idx});
      actor{idx}.getProperty().setColor({color[0]}, {color[1]}, {color[2]});
      actor{idx}.getProperty().setOpacity({opacity});

      // Add actor to renderer
      renderer.addActor(actor{idx});
            """)

        actors_code = "\n".join(actor_js_code)

        return f"""
<div id="{container_id}" style="width:600px;height:400px;border:2px solid #333;"></div>
<script>
(function() {{
  setTimeout(function() {{
    try {{
      const container = document.getElementById('{container_id}');

      // Use the simpler FullScreenRenderWindow helper
      const fullScreenRenderer = vtk.Rendering.Misc.vtkFullScreenRenderWindow.newInstance({{
        container: container,
        background: [{self.background[0]}, {self.background[1]}, {self.background[2]}]
      }});

      const renderer = fullScreenRenderer.getRenderer();
      const renderWindow = fullScreenRenderer.getRenderWindow();

{actors_code}

      // Reset camera and render
      renderer.resetCamera();
      renderWindow.render();

    }} catch(e) {{
      console.error('Error rendering vtk.js scene:', e);
    }}
  }}, 300);
}})();
</script>
"""

    def _repr_html_(self) -> str:
        """IPython representation as HTML for Jupyter notebooks.

        Returns
        -------
        str
            HTML string for display in Jupyter.

        """
        return self._generate_html()

    def clear(self) -> None:
        """Remove all actors from the renderer.

        Examples
        --------
        >>> renderer.clear()  # Remove all visualizations

        """
        self.actors = []
        if not self.use_ipython and hasattr(self, "renderer"):
            self.renderer.removeAllActors()

    def set_background(self, color: tuple[float, float, float]) -> None:
        """Set the background color of the renderer.

        Parameters
        ----------
        color : tuple
            RGB color tuple with values between 0 and 1.

        Examples
        --------
        >>> renderer.set_background((1.0, 1.0, 1.0))  # White background

        """
        self.background = color

    @staticmethod
    def _color_name_to_rgb(color_name: str) -> tuple[float, float, float]:
        """Convert color name to RGB tuple.

        Parameters
        ----------
        color_name : str
            Color name (e.g., 'red', 'blue').

        Returns
        -------
        tuple of float
            RGB values (0-1). Returns gray (0.5, 0.5, 0.5) for unknown colors.

        """
        colors = {
            "red": (1.0, 0.0, 0.0),
            "green": (0.0, 1.0, 0.0),
            "blue": (0.0, 0.0, 1.0),
            "yellow": (1.0, 1.0, 0.0),
            "cyan": (0.0, 1.0, 1.0),
            "magenta": (1.0, 0.0, 1.0),
            "white": (1.0, 1.0, 1.0),
            "black": (0.0, 0.0, 0.0),
        }
        return colors.get(color_name.lower(), (0.5, 0.5, 0.5))


class ElectronRenderer:
    """Renderer using Electron for desktop window visualization.

    This class provides a desktop window for 3D visualization using
    Electron + vtk.js when running in standard Python environments
    (not in notebook or browser).

    The renderer creates an Electron window with vtk.js rendering,
    providing a desktop visualization experience similar to PyVista's
    native OpenGL rendering but using web technologies.

    Features
    --------
    - Desktop window output for standard Python scripts
    - Full vtk.js rendering capabilities
    - Interactive 3D visualization with mouse controls
    - No browser required (runs in Electron)

    Requirements
    ------------
    - Node.js and npm installed
    - Electron package (installed automatically on first use)

    Examples
    --------
    >>> # In standard Python (not notebook)
    >>> from pyvista_js.rendering import ElectronRenderer
    >>> from pyvista_js import Sphere
    >>>
    >>> renderer = ElectronRenderer()
    >>> mesh = Sphere()
    >>> renderer.add_mesh_actor(mesh, color='red', opacity=0.8)
    >>> renderer.render()  # Opens Electron window

    Notes
    -----
    This renderer is designed for desktop Python environments.
    It requires Node.js to be installed on the system.
    The first run will install Electron via npm if not already present.

    """

    def __init__(self) -> None:
        """Initialize the Electron renderer.

        Creates a temporary directory for HTML files and initializes
        the actor list.

        """
        self.actors = []
        self.background = (0.2, 0.3, 0.4)  # Default background color
        self.temp_dir = Path(tempfile.mkdtemp(prefix="pyvista_js_"))
        self._electron_available = self._check_electron()

    def _check_electron(self) -> bool:
        """Check if Node.js and Electron are available.

        Returns
        -------
        bool
            True if Electron is available or can be installed, False otherwise.

        """
        # Check if Node.js is installed
        try:
            subprocess.run(
                ["node", "--version"],  # noqa: S607
                capture_output=True,
                check=True,
                timeout=5,
            )
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            logger.warning("Node.js not found. Electron renderer requires Node.js to be installed.")
            return False

        return True

    def _ensure_electron_installed(self) -> bool:
        """Ensure Electron is installed in the temp directory.

        Returns
        -------
        bool
            True if Electron is installed successfully, False otherwise.

        """
        if not self._electron_available:
            return False

        # Create package.json if it doesn't exist
        package_json_path = self.temp_dir / "package.json"
        if not package_json_path.exists():
            package_json = {
                "name": "pyvista-js-electron",
                "version": "1.0.0",
                "description": "Electron viewer for pyvista-js",
                "main": "main.js",
                "dependencies": {"electron": "^28.0.0"},
            }
            package_json_path.write_text(json.dumps(package_json, indent=2))

        # Check if node_modules/electron exists
        electron_path = self.temp_dir / "node_modules" / "electron"
        if electron_path.exists():
            return True

        # Install Electron
        logger.info("Installing Electron... This may take a minute on first use.")
        try:
            subprocess.run(
                ["npm", "install"],  # noqa: S607
                cwd=self.temp_dir,
                capture_output=True,
                check=True,
                timeout=120,
            )
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired) as e:
            logger.warning("Failed to install Electron: %s", e)
            return False
        else:
            logger.info("Electron installed successfully.")
            return True

    def create_container(self, element_id: str = "pyvista-container") -> None:
        """Create container (no-op for Electron renderer).

        Parameters
        ----------
        element_id : str
            Container ID (stored for HTML generation).

        """
        self.container_id = element_id

    def add_mesh_actor(
        self,
        mesh: Mesh,
        color: str | tuple[float, float, float] | None = None,
        opacity: float = 1.0,
    ) -> dict[str, object]:
        """Add a mesh to the renderer.

        Parameters
        ----------
        mesh : Mesh
            The mesh to add.
        color : str or tuple, optional
            Color of the mesh.
        opacity : float
            Opacity of the mesh (0-1).

        Returns
        -------
        dict
            Actor dictionary with mesh data.

        """
        if isinstance(color, str):
            color = self._color_name_to_rgb(color)

        actor_info = {
            "mesh": mesh,
            "color": color,
            "opacity": opacity,
        }
        self.actors.append(actor_info)
        logger.info("Added mesh with %d points", mesh.n_points)
        return actor_info

    def render(self) -> None:
        """Render the scene in an Electron window.

        Generates HTML with vtk.js code, creates Electron main.js,
        and launches the Electron application to display the visualization.

        If Electron is not available, falls back to saving HTML file
        and attempting to open it in the default browser.

        """
        # Generate HTML content
        html_content = self._generate_html()

        # Save HTML file
        html_path = self.temp_dir / "viewer.html"
        html_path.write_text(html_content)

        logger.info("Visualization HTML saved to: %s", html_path)

        # Try to render with Electron
        if self._electron_available and self._ensure_electron_installed():
            self._render_with_electron(html_path)
        else:
            logger.warning(
                "Electron not available. HTML file saved to: %s\n"
                "You can open this file in a browser to view the visualization.",
                html_path,
            )
            # Try to open in default browser as fallback
            self._open_in_browser(html_path)

    def _render_with_electron(self, html_path: Path) -> None:
        """Launch Electron to display the visualization.

        Parameters
        ----------
        html_path : Path
            Path to the HTML file to display.

        """
        # Create Electron main.js
        main_js = f"""
const {{ app, BrowserWindow }} = require('electron');
const path = require('path');

function createWindow() {{
  const win = new BrowserWindow({{
    width: 1024,
    height: 768,
    title: 'PyVista-JS Viewer',
    webPreferences: {{
      nodeIntegration: false,
      contextIsolation: true
    }}
  }});

  win.loadFile('{html_path.name}');

  // Open DevTools for debugging (optional)
  // win.webContents.openDevTools();
}}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {{
  if (process.platform !== 'darwin') {{
    app.quit();
  }}
}});

app.on('activate', () => {{
  if (BrowserWindow.getAllWindows().length === 0) {{
    createWindow();
  }}
}});
"""
        main_js_path = self.temp_dir / "main.js"
        main_js_path.write_text(main_js)

        # Launch Electron
        try:
            logger.info("Opening Electron window...")
            # Use npx to run electron
            subprocess.Popen(
                ["npx", "electron", "."],  # noqa: S607
                cwd=self.temp_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            logger.info("Electron window opened successfully.")
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            logger.warning("Failed to launch Electron: %s", e)
            logger.info("HTML file available at: %s", html_path)

    def _open_in_browser(self, html_path: Path) -> None:
        """Fallback: Open HTML in default browser.

        Parameters
        ----------
        html_path : Path
            Path to the HTML file to open.

        """
        try:
            webbrowser.open(html_path.as_uri())
            logger.info("Opened visualization in default browser.")
        except OSError as e:
            logger.warning("Could not open browser: %s", e)

    def _generate_html(self) -> str:
        """Generate HTML content with vtk.js visualization.

        Returns
        -------
        str
            Complete HTML document with embedded vtk.js code.

        """
        container_id = getattr(self, "container_id", "pyvista-container")

        # Generate JavaScript code for each actor
        actor_js_code = []
        for idx, actor_info in enumerate(self.actors):
            mesh = actor_info["mesh"]
            color = actor_info.get("color", (0.5, 0.5, 0.5))
            opacity = actor_info.get("opacity", 1.0)

            # Detect mesh type and get parameters
            mesh_type = getattr(mesh, "_mesh_type", None)
            params = getattr(mesh, "_params", {})

            # Convert mesh points to JavaScript array
            points_flat = mesh.points.flatten().tolist()

            # Generate appropriate source based on mesh type
            if mesh_type == "Sphere":
                radius = params.get("radius", 1.0)
                center = params.get("center", (0, 0, 0))
                theta_res = params.get("theta_resolution", 30)
                phi_res = params.get("phi_resolution", 30)
                source_code = f"""
      const source{idx} = vtk.Filters.Sources.vtkSphereSource.newInstance({{
        center: [{center[0]}, {center[1]}, {center[2]}],
        radius: {radius},
        thetaResolution: {theta_res},
        phiResolution: {phi_res}
      }});"""
            elif mesh_type == "Cube":
                center = params.get("center", (0, 0, 0))
                x_len = params.get("x_length", 1.0)
                y_len = params.get("y_length", 1.0)
                z_len = params.get("z_length", 1.0)
                source_code = f"""
      const source{idx} = vtk.Filters.Sources.vtkCubeSource.newInstance({{
        center: [{center[0]}, {center[1]}, {center[2]}],
        xLength: {x_len},
        yLength: {y_len},
        zLength: {z_len}
      }});"""
            elif mesh_type == "Cylinder":
                center = params.get("center", (0, 0, 0))
                radius = params.get("radius", 0.5)
                height = params.get("height", 1.0)
                resolution = params.get("resolution", 100)
                source_code = f"""
      const source{idx} = vtk.Filters.Sources.vtkCylinderSource.newInstance({{
        center: [{center[0]}, {center[1]}, {center[2]}],
        radius: {radius},
        height: {height},
        resolution: {resolution}
      }});"""
            else:
                # Generic mesh using polydata
                points_str = ",".join(map(str, points_flat))
                source_code = f"""
      const points{idx} = new Float32Array([{points_str}]);
      const polydata{idx} = vtk.Common.DataModel.vtkPolyData.newInstance();
      polydata{idx}.getPoints().setData(points{idx}, 3);
      const source{idx} = polydata{idx};"""

            # Determine mapper setup based on mesh type
            if mesh_type in ["Sphere", "Cube", "Cylinder"]:
                mapper_setup = f"mapper{idx}.setInputConnection(source{idx}.getOutputPort());"
            else:
                mapper_setup = f"mapper{idx}.setInputData(source{idx});"

            actor_js_code.append(f"""{source_code}

      // Create mapper
      const mapper{idx} = vtk.Rendering.Core.vtkMapper.newInstance();
      {mapper_setup}

      // Create actor
      const actor{idx} = vtk.Rendering.Core.vtkActor.newInstance();
      actor{idx}.setMapper(mapper{idx});
      actor{idx}.getProperty().setColor({color[0]}, {color[1]}, {color[2]});
      actor{idx}.getProperty().setOpacity({opacity});

      // Add actor to renderer
      renderer.addActor(actor{idx});
            """)

        actors_code = "\n".join(actor_js_code)

        return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PyVista-JS Viewer</title>
    <style>
        body {{
            margin: 0;
            padding: 0;
            overflow: hidden;
            font-family: Arial, sans-serif;
        }}
        #info {{
            position: absolute;
            top: 10px;
            left: 10px;
            background: rgba(255, 255, 255, 0.9);
            padding: 10px;
            border-radius: 5px;
            font-size: 12px;
            z-index: 1000;
        }}
        #{container_id} {{
            width: 100vw;
            height: 100vh;
        }}
    </style>
    <script src="https://unpkg.com/vtk.js@29.5.0"></script>
</head>
<body>
    <div id="info">
        <strong>PyVista-JS Viewer</strong><br>
        Left Mouse: Rotate<br>
        Middle Mouse: Pan<br>
        Right Mouse: Zoom<br>
        Scroll: Zoom
    </div>
    <div id="{container_id}"></div>
    <script>
        (function() {{
            const container = document.getElementById('{container_id}');

            // Use the simpler FullScreenRenderWindow helper
            const fullScreenRenderer = vtk.Rendering.Misc.vtkFullScreenRenderWindow.newInstance({{
                container: container,
                background: [{self.background[0]}, {self.background[1]}, {self.background[2]}]
            }});

            const renderer = fullScreenRenderer.getRenderer();
            const renderWindow = fullScreenRenderer.getRenderWindow();

{actors_code}

            // Reset camera and render
            renderer.resetCamera();
            renderWindow.render();
        }})();
    </script>
</body>
</html>"""

    def clear(self) -> None:
        """Remove all actors from the renderer."""
        self.actors = []
        logger.info("Cleared all actors")

    def set_background(self, color: tuple[float, float, float]) -> None:
        """Set the background color.

        Parameters
        ----------
        color : tuple
            RGB color tuple with values between 0 and 1.

        """
        self.background = color

    @staticmethod
    def _color_name_to_rgb(color_name: str) -> tuple[float, float, float]:
        """Convert color name to RGB tuple.

        Parameters
        ----------
        color_name : str
            Color name (e.g., 'red', 'blue').

        Returns
        -------
        tuple of float
            RGB values (0-1). Returns gray (0.5, 0.5, 0.5) for unknown colors.

        """
        colors = {
            "red": (1.0, 0.0, 0.0),
            "green": (0.0, 1.0, 0.0),
            "blue": (0.0, 0.0, 1.0),
            "yellow": (1.0, 1.0, 0.0),
            "cyan": (0.0, 1.0, 1.0),
            "magenta": (1.0, 0.0, 1.0),
            "white": (1.0, 1.0, 1.0),
            "black": (0.0, 0.0, 0.0),
        }
        return colors.get(color_name.lower(), (0.5, 0.5, 0.5))

    def __del__(self) -> None:
        """Clean up temporary directory on deletion."""
        # Note: We intentionally don't delete the temp directory here
        # to allow the Electron window to remain open after the script exits.
        # The OS will clean up temp files eventually.


class MockRenderer:
    """Mock renderer for non-Pyodide environments.

    Provides a drop-in replacement for VTKJSRenderer that can be used
    in standard Python environments for development and testing.

    Why MockRenderer is Needed
    ---------------------------
    1. **Local Development**: Develop and test code on your PC without browser
    2. **CI/CD Testing**: Run pytest in GitHub Actions and other CI systems
    3. **Documentation**: Generate docs with sphinx-build without Pyodide
    4. **API Validation**: Verify API design before vtk.js integration
    5. **Cross-platform**: Same code works in Pyodide and standard Python

    The MockRenderer prints debug information instead of rendering,
    allowing you to verify that your visualization code is correct.

    Examples
    --------
    >>> # Works in standard Python
    >>> from pyvista_js.rendering import MockRenderer
    >>> from pyvista_js import Sphere
    >>>
    >>> renderer = MockRenderer()
    >>> mesh = Sphere()
    >>> renderer.add_mesh_actor(mesh, color='red')
    Mock: Added mesh with 900 points
    >>>
    >>> renderer.render()
    Mock: Rendering 1 actors

    Notes
    -----
    The mock renderer is automatically used when calling `get_renderer()`
    outside of a Pyodide environment. You typically don't need to instantiate
    it directly.

    """

    def __init__(self) -> None:
        """Initialize mock renderer."""
        self.actors = []
        self.background = (0.2, 0.3, 0.4)  # Default background color

    def create_container(self, element_id: str = "pyvista-container") -> None:
        """Mock container creation.

        Parameters
        ----------
        element_id : str
            Container ID (for API compatibility).

        Returns
        -------
        None
            Mock renderers don't create actual containers.

        """
        logger.info("Created container '%s'", element_id)

    def add_mesh_actor(
        self,
        mesh: Mesh,
        color: str | tuple[float, float, float] | None = None,
        opacity: float = 1.0,
    ) -> dict[str, object]:
        """Mock mesh addition.

        Parameters
        ----------
        mesh : Mesh
            The mesh to add.
        color : str or tuple, optional
            Color (stored but not rendered).
        opacity : float
            Opacity (stored but not rendered).

        Returns
        -------
        dict
            Mock actor dictionary with mesh data.

        """
        actor = {
            "mesh": mesh,
            "color": color,
            "opacity": opacity,
        }
        self.actors.append(actor)
        logger.info("Added mesh with %d points", mesh.n_points)
        return actor

    def render(self) -> None:
        """Mock rendering.

        Logs the number of actors that would be rendered.
        """
        logger.info("Rendering %d actors", len(self.actors))

    def clear(self) -> None:
        """Mock clear.

        Removes all actors from the mock renderer.
        """
        self.actors = []
        logger.info("Cleared all actors")

    def set_background(self, color: tuple[float, float, float]) -> None:
        """Set the background color.

        Parameters
        ----------
        color : tuple
            RGB color tuple with values between 0 and 1.

        """
        self.background = color


def get_renderer() -> VTKJSRenderer | MockRenderer | ElectronRenderer:
    """Get appropriate renderer for current environment.

    Automatically detects whether running in Pyodide/browser and
    returns the appropriate renderer implementation.

    Environment Variables
    ---------------------
    PYVISTA_JS_BACKEND : str, optional
        Override automatic backend selection. Options:
        - 'electron': Use Electron renderer (desktop window)
        - 'mock': Use mock renderer (testing)
        - 'auto': Automatic selection (default)

    Returns
    -------
    VTKJSRenderer, MockRenderer, or ElectronRenderer
        - VTKJSRenderer if in Pyodide or IPython environment
        - ElectronRenderer if PYVISTA_JS_BACKEND='electron' in standard Python
        - MockRenderer otherwise (standard Python, testing, CI/CD)

    Examples
    --------
    >>> # Automatically gets the right renderer
    >>> renderer = get_renderer()
    >>>
    >>> # In Pyodide or Jupyter: returns VTKJSRenderer
    >>> # In standard Python: returns MockRenderer
    >>>
    >>> # Same code works in both environments
    >>> from pyvista_js import Sphere
    >>> mesh = Sphere()
    >>> renderer.add_mesh_actor(mesh, color='blue')
    >>> renderer.create_container()
    >>> renderer.render()

    Force Electron backend in standard Python:

    >>> import os
    >>> os.environ['PYVISTA_JS_BACKEND'] = 'electron'
    >>> renderer = get_renderer()  # Returns ElectronRenderer

    Notes
    -----
    This function is used internally by the Plotter class. You typically
    don't need to call it directly unless implementing custom rendering logic.

    """
    # Check for explicit backend override
    backend = os.environ.get("PYVISTA_JS_BACKEND", "auto").lower()

    if backend == "electron":
        return ElectronRenderer()
    if backend == "mock":
        return MockRenderer()

    # Automatic selection (default behavior)
    # Use VTKJSRenderer if in Pyodide with vtk.js OR if IPython is available
    if (PYODIDE_ENV and VTK_AVAILABLE) or IPYTHON_AVAILABLE:
        return VTKJSRenderer()
    return MockRenderer()
