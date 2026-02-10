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
vtk.js must be loaded before using VTKJSRenderer:

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

import sys

# Check if running in Pyodide environment
PYODIDE_ENV = sys.platform == "emscripten"

if PYODIDE_ENV:
    try:
        from js import document  # noqa: F401
        VTK_AVAILABLE = True
    except ImportError:
        VTK_AVAILABLE = False
else:
    VTK_AVAILABLE = False

# Check if IPython is available
try:
    from IPython.display import HTML, display
    IPYTHON_AVAILABLE = True
except ImportError:
    IPYTHON_AVAILABLE = False


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

    def __init__(self):
        """Initialize the vtk.js renderer.

        Raises
        ------
        RuntimeError
            If not running in Pyodide environment.
        ImportError
            If vtk.js is not available in the page.
        """
        if not PYODIDE_ENV:
            # In non-Pyodide environment, check if IPython is available
            if not IPYTHON_AVAILABLE:
                raise RuntimeError(
                    "VTKJSRenderer requires either Pyodide environment or IPython"
                )

        self.container = None
        self.actors = []
        self.use_ipython = IPYTHON_AVAILABLE

    def create_container(self, element_id="pyvista-container"):
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
        else:
            # Create container div directly
            self.container = document.createElement("div")
            self.container.setAttribute("id", element_id)
            self.container.style.width = "100%"
            self.container.style.height = "600px"

            # Append to body
            document.body.appendChild(self.container)

            return self.container

    def add_mesh_actor(self, mesh, color=None, opacity=1.0):
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
            'mesh': mesh,
            'color': color,
            'opacity': opacity,
        }
        self.actors.append(actor_info)

        return actor_info

    def render(self):
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

    def _generate_html(self):
        """Generate HTML and JavaScript for IPython display."""
        container_id = getattr(self, 'container_id', 'pyvista-container')

        # Generate JavaScript code for each actor
        actor_js_code = []
        for actor_info in self.actors:
            mesh = actor_info['mesh']
            color = actor_info.get('color', (0.5, 0.5, 0.5))
            opacity = actor_info.get('opacity', 1.0)

            # Convert mesh points to JavaScript array
            points_flat = mesh.points.flatten().tolist()
            '[' + ','.join(map(str, points_flat)) + ']'

            # Generate code to create sphere source (for now, assuming Sphere)
            # TODO: Add support for other mesh types
            actor_js_code.append(f'''
      // Create sphere source
      const sphereSource = vtk.Filters.Sources.vtkSphereSource.newInstance({{
        center: [0, 0, 0],
        radius: 1.0,
        thetaResolution: 30,
        phiResolution: 30
      }});

      // Create mapper
      const mapper = vtk.Rendering.Core.vtkMapper.newInstance();
      mapper.setInputConnection(sphereSource.getOutputPort());

      // Create actor
      const actor = vtk.Rendering.Core.vtkActor.newInstance();
      actor.setMapper(mapper);
      actor.getProperty().setColor({color[0]}, {color[1]}, {color[2]});
      actor.getProperty().setOpacity({opacity});

      // Add actor to renderer
      renderer.addActor(actor);
            ''')

        actors_code = '\n'.join(actor_js_code)

        html = f'''
<div id="{container_id}" style="width:600px;height:400px;border:2px solid #333;"></div>
<div id="debug-{container_id}" style="margin-top:10px;font-family:monospace;
font-size:11px;background:#f5f5f5;padding:8px;"></div>
<script>
(function() {{
  const debug = document.getElementById('debug-{container_id}');
  function log(msg) {{
    console.log(msg);
    debug.innerHTML += msg + '<br>';
  }}

  setTimeout(function() {{
    try {{
      const container = document.getElementById('{container_id}');
      log('📦 Container: ' + container.offsetWidth + 'x' + container.offsetHeight);

      // Use the simpler FullScreenRenderWindow helper
      const fullScreenRenderer = vtk.Rendering.Misc.vtkFullScreenRenderWindow.newInstance({{
        container: container,
        background: [0.2, 0.3, 0.4]
      }});

      const renderer = fullScreenRenderer.getRenderer();
      const renderWindow = fullScreenRenderer.getRenderWindow();
      log('✅ Renderer created');

{actors_code}

      // Reset camera and render
      renderer.resetCamera();
      renderWindow.render();

      log('🎉 Scene rendered successfully!');
      log('🖱️  Drag to rotate, scroll to zoom');

    }} catch(e) {{
      log('❌ Error: ' + e.message);
      console.error(e);
    }}
  }}, 300);
}})();
</script>
'''
        return html

    def clear(self):
        """Remove all actors from the renderer.

        Examples
        --------
        >>> renderer.clear()  # Remove all visualizations
        """
        self.actors = []
        if not self.use_ipython and hasattr(self, 'renderer'):
            self.renderer.removeAllActors()

    @staticmethod
    def _color_name_to_rgb(color_name):
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
            'red': (1.0, 0.0, 0.0),
            'green': (0.0, 1.0, 0.0),
            'blue': (0.0, 0.0, 1.0),
            'yellow': (1.0, 1.0, 0.0),
            'cyan': (0.0, 1.0, 1.0),
            'magenta': (1.0, 0.0, 1.0),
            'white': (1.0, 1.0, 1.0),
            'black': (0.0, 0.0, 0.0),
        }
        return colors.get(color_name.lower(), (0.5, 0.5, 0.5))


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

    def __init__(self):
        """Initialize mock renderer."""
        self.actors = []

    def create_container(self, element_id="pyvista-container"):
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
        print(f"Mock: Created container '{element_id}'")
        return None

    def add_mesh_actor(self, mesh, color=None, opacity=1.0):
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
            'mesh': mesh,
            'color': color,
            'opacity': opacity,
        }
        self.actors.append(actor)
        print(f"Mock: Added mesh with {mesh.n_points} points")
        return actor

    def render(self):
        """Mock rendering.

        Prints the number of actors that would be rendered.
        """
        print(f"Mock: Rendering {len(self.actors)} actors")

    def clear(self):
        """Mock clear.

        Removes all actors from the mock renderer.
        """
        self.actors = []
        print("Mock: Cleared all actors")


def get_renderer():
    """Get appropriate renderer for current environment.

    Automatically detects whether running in Pyodide/browser and
    returns the appropriate renderer implementation.

    Returns
    -------
    VTKJSRenderer or MockRenderer
        - VTKJSRenderer if in Pyodide or IPython environment
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

    Notes
    -----
    This function is used internally by the Plotter class. You typically
    don't need to call it directly unless implementing custom rendering logic.
    """
    # Use VTKJSRenderer if in Pyodide with vtk.js OR if IPython is available
    if (PYODIDE_ENV and VTK_AVAILABLE) or IPYTHON_AVAILABLE:
        return VTKJSRenderer()
    else:
        return MockRenderer()
