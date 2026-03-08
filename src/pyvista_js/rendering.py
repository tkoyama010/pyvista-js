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

import logging
import sys
import time
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing_extensions import Self

    from .mesh import Mesh

from .examples import CubeMap

# Load JavaScript templates
_JS_DIR = Path(__file__).parent / "js"
_RENDERING_TEMPLATE = (_JS_DIR / "rendering.html").read_text()
_ACTOR_TEMPLATE = (_JS_DIR / "actor.js").read_text()

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
        return cls._instance  # type: ignore[return-value]

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
        self.actors: list[dict[str, object]] = []
        self.use_ipython = IPYTHON_AVAILABLE
        self.background = (0.2, 0.3, 0.4)  # Default background color
        self._environment_texture_url: str | None = None
        self._environment_texture_cubemap: CubeMap | None = None
        self._view_vector: tuple[float, float, float] | None = None
        self._view_up: tuple[float, float, float] = (0.0, 1.0, 0.0)

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
        self.container = document.createElement("div")  # type: ignore[attr-defined]
        self.container.setAttribute("id", element_id)  # type: ignore[attr-defined]
        self.container.style.width = "100%"  # type: ignore[attr-defined]
        self.container.style.height = "600px"  # type: ignore[attr-defined]

        # Append to body
        document.body.appendChild(self.container)  # type: ignore[union-attr]

        return self.container

    def add_mesh_actor(  # noqa: PLR0913
        self,
        mesh: Mesh,
        color: str | tuple[float, float, float] | None = None,
        opacity: float = 1.0,
        pbr: bool = False,  # noqa: FBT001 FBT002
        metallic: float = 0.0,
        roughness: float = 0.5,
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
        pbr : bool, default=False
            Enable physically based rendering (PBR).
        metallic : float, default=0.0
            Metallic factor for PBR, between 0 and 1.
        roughness : float, default=0.5
            Roughness factor for PBR, between 0 and 1.

        Returns
        -------
        actor
            The vtk.js vtkActor object representing the mesh (or dict if using IPython).

        Examples
        --------
        >>> from pyvista_js import Sphere
        >>> mesh = Sphere(radius=2.0)
        >>> actor = renderer.add_mesh_actor(mesh, color='red', opacity=0.8)

        PBR example:

        >>> actor = renderer.add_mesh_actor(mesh, color='white', pbr=True, metallic=0.8,
        ...                                 roughness=0.1)

        """
        # Store actor information for later rendering
        if isinstance(color, str):
            color = self._color_name_to_rgb(color)

        actor_info: dict[str, object] = {
            "mesh": mesh,
            "color": color,
            "opacity": opacity,
            "pbr": pbr,
            "metallic": metallic,
            "roughness": roughness,
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
            self.renderer.resetCamera()  # type: ignore[attr-defined]
            self.render_window.render()  # type: ignore[attr-defined]

    def view_vector(
        self,
        vector: tuple[float, float, float],
        viewup: tuple[float, float, float] | None = None,
    ) -> None:
        """Point the camera in the direction of the given vector.

        Parameters
        ----------
        vector : tuple of float
            Direction vector (vx, vy, vz) to point the camera.
        viewup : tuple of float, optional
            View-up vector. Defaults to (0, 1, 0).

        """
        self._view_vector = (float(vector[0]), float(vector[1]), float(vector[2]))
        if viewup is not None:
            self._view_up = (float(viewup[0]), float(viewup[1]), float(viewup[2]))

    def set_environment_texture(self, texture: str | CubeMap) -> None:
        """Set the environment texture for image-based lighting.

        Parameters
        ----------
        texture : str or CubeMap
            Either a URL string pointing to an equirectangular image, or a
            :class:`~pyvista_js.examples.CubeMap` with six face image URLs.

        """
        if isinstance(texture, CubeMap):
            self._environment_texture_cubemap = texture
            self._environment_texture_url = None
        else:
            self._environment_texture_url = texture
            self._environment_texture_cubemap = None

    def _generate_html(self) -> str:
        """Generate HTML and JavaScript for IPython display."""
        container_id = getattr(self, "container_id", "pyvista-container")

        # Generate JavaScript code for each actor
        actor_js_code = []
        for idx, actor_info in enumerate(self.actors):
            mesh = actor_info["mesh"]
            color = actor_info.get("color") or (0.5, 0.5, 0.5)
            opacity = actor_info.get("opacity", 1.0)
            pbr = actor_info.get("pbr", False)
            metallic = float(actor_info.get("metallic", 0.0))  # type: ignore[arg-type]
            roughness = float(actor_info.get("roughness", 0.5))  # type: ignore[arg-type]

            # Use polymorphic methods to generate source code
            source_code = mesh.generate_vtk_js_source(idx)  # type: ignore[attr-defined]
            mapper_setup = mesh.get_mapper_setup(idx)  # type: ignore[attr-defined]

            # Build PBR code snippet if enabled.
            # vtk.js WebGL uses Phong shading; map metallic/roughness to
            # Phong parameters so both axes are visually distinct:
            #   metallic  → diffuse (1.0 → 0.3) and specular (0.5 → 1.0)
            #   roughness → specularPower (128 → 1)
            if pbr:
                specular = round(metallic * 0.5 + 0.5, 4)
                specular_power = max(1, round((1.0 - roughness) ** 2 * 128))
                diffuse = round(1.0 - metallic * 0.7, 4)
                pbr_code = (
                    f"actor{idx}.getProperty().setInterpolationToPhong();\n"
                    f"actor{idx}.getProperty().setMetallic({metallic});\n"
                    f"actor{idx}.getProperty().setRoughness({roughness});\n"
                    f"actor{idx}.getProperty().setAmbient(0.1);\n"
                    f"actor{idx}.getProperty().setSpecular({specular});\n"
                    f"actor{idx}.getProperty().setSpecularPower({specular_power});\n"
                    f"actor{idx}.getProperty().setDiffuse({diffuse});"
                )
            else:
                pbr_code = ""

            # Use actor template
            actor_code = (
                _ACTOR_TEMPLATE.replace("{{SOURCE_CODE}}", source_code)
                .replace("{{INDEX}}", str(idx))
                .replace("{{MAPPER_SETUP}}", mapper_setup)
                .replace("{{COLOR_R}}", str(color[0]))  # type: ignore[index]
                .replace("{{COLOR_G}}", str(color[1]))  # type: ignore[index]
                .replace("{{COLOR_B}}", str(color[2]))  # type: ignore[index]
                .replace("{{OPACITY}}", str(opacity))
                .replace("{{PBR_CODE}}", pbr_code)
            )
            actor_js_code.append(actor_code)

        # Join actor code with proper indentation (6 spaces to match the context)
        indented_actors = []
        for actor in actor_js_code:
            lines = actor.split("\n")
            indented_lines = "\n".join("      " + line if line.strip() else "" for line in lines)
            indented_actors.append(indented_lines)
        actors_code = "\n\n".join(indented_actors)

        # Build environment texture code
        if self._environment_texture_url:
            env_code = (
                "      // Load environment texture for image-based lighting\n"
                "      const envTexture = vtk.Rendering.Core.vtkTexture.newInstance();\n"
                "      const envImg = new Image();\n"
                "      envImg.crossOrigin = 'anonymous';\n"
                "      envImg.onload = function() {\n"
                "        envTexture.setImage(envImg);\n"
                "        renderer.setEnvironmentTexture(envTexture);\n"
                "        renderWindow.render();\n"
                "      };\n"
                f"      envImg.src = '{self._environment_texture_url}';"
            )
        elif self._environment_texture_cubemap:
            urls = self._environment_texture_cubemap.face_urls
            urls_js = ", ".join(f"'{u}'" for u in urls)
            env_code = (
                "      // Load cubemap faces and stitch into a canvas for IBL\n"
                f"      const faceUrls = [{urls_js}];\n"
                "      Promise.all(faceUrls.map(function(url) {\n"
                "        return new Promise(function(resolve, reject) {\n"
                "          const img = new Image();\n"
                "          img.crossOrigin = 'anonymous';\n"
                "          img.onload = function() { resolve(img); };\n"
                "          img.onerror = reject;\n"
                "          img.src = url;\n"
                "        });\n"
                "      })).then(function(images) {\n"
                "        const size = images[0].width;\n"
                "        const canvas = document.createElement('canvas');\n"
                "        canvas.width = size * 6;\n"
                "        canvas.height = size;\n"
                "        const ctx = canvas.getContext('2d');\n"
                "        images.forEach(function(img, i) {\n"
                "          ctx.drawImage(img, i * size, 0);\n"
                "        });\n"
                "        const envTexture = vtk.Rendering.Core.vtkTexture.newInstance();\n"
                "        envTexture.setInterpolate(true);\n"
                "        envTexture.setCanvas(canvas);\n"
                "        renderer.setEnvironmentTexture(envTexture);\n"
                "        renderWindow.render();\n"
                "      });"
            )
        else:
            env_code = ""

        # Build camera code
        if self._view_vector is not None:
            vx, vy, vz = self._view_vector
            ux, uy, uz = self._view_up
            camera_code = (
                "      const cam = renderer.getActiveCamera();\n"
                "      const fp = cam.getFocalPoint();\n"
                f"      cam.setPosition(fp[0] + {vx}, fp[1] + {vy}, fp[2] + {vz});\n"
                f"      cam.setViewUp({ux}, {uy}, {uz});\n"
                "      renderer.resetCameraClippingRange();"
            )
        else:
            camera_code = ""

        # Use rendering template
        return (
            _RENDERING_TEMPLATE.replace("{{CONTAINER_ID}}", container_id)
            .replace("{{BACKGROUND_R}}", str(self.background[0]))
            .replace("{{BACKGROUND_G}}", str(self.background[1]))
            .replace("{{BACKGROUND_B}}", str(self.background[2]))
            .replace("{{ACTORS_CODE}}", actors_code)
            .replace("{{ENVIRONMENT_CODE}}", env_code)
            .replace("{{CAMERA_CODE}}", camera_code)
        )

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
        self.actors: list[dict[str, object]] = []
        self.background = (0.2, 0.3, 0.4)  # Default background color
        self._view_vector: tuple[float, float, float] | None = None
        self._view_up: tuple[float, float, float] = (0.0, 1.0, 0.0)

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

    def add_mesh_actor(  # noqa: PLR0913
        self,
        mesh: Mesh,
        color: str | tuple[float, float, float] | None = None,
        opacity: float = 1.0,
        pbr: bool = False,  # noqa: FBT001 FBT002
        metallic: float = 0.0,
        roughness: float = 0.5,
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
        pbr : bool
            PBR flag (stored but not rendered).
        metallic : float
            Metallic factor (stored but not rendered).
        roughness : float
            Roughness factor (stored but not rendered).

        Returns
        -------
        dict
            Mock actor dictionary with mesh data.

        """
        actor: dict[str, object] = {
            "mesh": mesh,
            "color": color,
            "opacity": opacity,
            "pbr": pbr,
            "metallic": metallic,
            "roughness": roughness,
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

    def view_vector(
        self,
        vector: tuple[float, float, float],
        viewup: tuple[float, float, float] | None = None,
    ) -> None:
        """Mock view_vector.

        Parameters
        ----------
        vector : tuple of float
            Direction vector (stored but not rendered).
        viewup : tuple of float, optional
            View-up vector (stored but not rendered).

        """
        self._view_vector = (float(vector[0]), float(vector[1]), float(vector[2]))
        if viewup is not None:
            self._view_up = (float(viewup[0]), float(viewup[1]), float(viewup[2]))
        logger.info("Set view vector: %s (viewup=%s)", vector, viewup)

    def set_environment_texture(self, texture: object) -> None:
        """Mock environment texture.

        Parameters
        ----------
        texture : str or CubeMap
            Environment texture (stored but not rendered).

        """
        logger.info("Set environment texture: %s", texture)


def get_renderer() -> VTKJSRenderer | MockRenderer:
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
    return MockRenderer()
