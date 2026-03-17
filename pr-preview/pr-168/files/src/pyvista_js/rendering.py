"""vtk.js rendering backend for pyvista-js.

This module provides the JavaScript bridge to vtk.js for rendering
in Pyodide/browser environments.

Architecture
------------
pyvista-js uses a backend abstraction to support multiple environments:

1. **VTKJSRenderer**: Used in Pyodide/browser with vtk.js for WebGL rendering
2. **BrowserRenderer**: Used in standard Python; opens the plot in the default browser
3. **MockRenderer**: Used in standard Python for development/testing

Environment Detection
---------------------
The library automatically detects the runtime:

>>> import sys
>>> PYODIDE_ENV = sys.platform == "emscripten"  # True in Pyodide

If running in Pyodide and vtk.js is available, VTKJSRenderer is used.
If running in standard Python, BrowserRenderer opens the plot in the default browser.
MockRenderer provides a fallback for testing.

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
it opens the visualization in the default web browser.

"""

from __future__ import annotations

import logging
import os
import pathlib
import sys
import tempfile
import time
import webbrowser
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing_extensions import Self

    from .camera import Camera
    from .light import Light
    from .mesh import PolyData
    from .texture import Texture

from .examples import CubeMap

# Load JavaScript templates
_JS_DIR = pathlib.Path(__file__).parent / "js"
_RENDERING_TEMPLATE = (_JS_DIR / "rendering.html").read_text()
_ACTOR_TEMPLATE = (_JS_DIR / "actor.js").read_text()

# vtk.js CDN URL used across renderers
_VTKJS_CDN = "https://unpkg.com/vtk.js@29.5.0"

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
                    HTML(f"""
<script src="{_VTKJS_CDN}"></script>
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
            script.src = _VTKJS_CDN
            document.head.appendChild(script)
            # Wait for vtk.js to load from CDN
            time.sleep(2)
            self._loaded = True


logger = logging.getLogger(__name__)


class _BaseHTMLRenderer:
    """Base class providing shared state and HTML generation for vtk.js renderers.

    Subclasses implement :meth:`render` to display the generated HTML in their
    respective environments (Jupyter notebook, standalone browser, etc.).
    """

    def __init__(self) -> None:
        """Initialize shared renderer state."""
        self.actors: list[dict[str, object]] = []
        self.lights: list[Light] = []
        self.background: tuple[float, float, float] = (1.0, 1.0, 1.0)
        self.container_id: str = "pyvista-container"
        self._environment_texture_url: str | None = None
        self._environment_texture_cubemap: CubeMap | None = None
        self._view_vector: tuple[float, float, float] | None = None
        self._view_up: tuple[float, float, float] = (0.0, 1.0, 0.0)
        self._camera: Camera | None = None

    def create_container(self, element_id: str = "pyvista-container") -> object | None:
        """Store the container ID for later HTML generation.

        Parameters
        ----------
        element_id : str, default="pyvista-container"
            HTML element ID for the container.

        Returns
        -------
        object or None
            Subclasses may return a DOM element or None.

        """
        self.container_id = element_id
        return None

    def add_mesh_actor(  # noqa: PLR0913
        self,
        mesh: PolyData,
        color: str | tuple[float, float, float] | None = None,
        opacity: float = 1.0,
        pbr: bool = False,  # noqa: FBT001 FBT002
        metallic: float = 0.0,
        roughness: float = 0.5,
        texture: Texture | None = None,
        show_edges: bool = False,  # noqa: FBT001 FBT002
        edge_color: str | tuple[float, float, float] | None = None,
        style: str = "surface",
    ) -> dict[str, object]:
        """Add a mesh to the renderer.

        Parameters
        ----------
        mesh : PolyData
            The mesh object to render.
        color : tuple or str, optional
            RGB color tuple (0-1) or color name ('red', 'blue', etc.).
        opacity : float, default=1.0
            Opacity value between 0 and 1.
        pbr : bool, default=False
            Enable physically based rendering.
        metallic : float, default=0.0
            Metallic factor for PBR.
        roughness : float, default=0.5
            Roughness factor for PBR.
        texture : Texture, optional
            Surface texture to apply. The texture image is loaded from the
            URL stored in the :class:`~pyvista_js.Texture` object.
        show_edges : bool, default=False
            Show the edges of the mesh.
        edge_color : tuple or str, optional
            RGB color tuple (0-1) or color name for edges when ``show_edges=True``.
            If not specified, defaults to black.
        style : str, default='surface'
            Visualization style. One of 'surface', 'wireframe', or 'points'.

        Returns
        -------
        dict
            Actor information dictionary.

        """
        if isinstance(color, str):
            color = self._color_name_to_rgb(color)

        # Convert edge_color if it's a string
        if isinstance(edge_color, str):
            edge_color = self._color_name_to_rgb(edge_color)

        actor_info: dict[str, object] = {
            "mesh": mesh,
            "color": color,
            "opacity": opacity,
            "pbr": pbr,
            "metallic": metallic,
            "roughness": roughness,
            "texture": texture,
            "show_edges": show_edges,
            "edge_color": edge_color,
            "style": style,
        }
        self.actors.append(actor_info)
        return actor_info

    def add_light(self, light: Light) -> None:
        """Add a light source to the scene.

        Parameters
        ----------
        light : Light
            The :class:`~pyvista_js.light.Light` instance to add.

        Examples
        --------
        >>> import pyvista_js as pv
        >>> renderer = get_renderer()
        >>> renderer.add_light(pv.Light(position=(1, 1, 1), intensity=2.0))

        """
        self.lights.append(light)

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

    def set_background(self, color: tuple[float, float, float]) -> None:
        """Set the background color of the renderer.

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

    @property
    def camera(self) -> Camera | None:
        """Get or set the camera for the renderer.

        Parameters
        ----------
        camera : Camera
            The camera object to use for rendering.

        Returns
        -------
        Camera or None
            The current camera, or None if not set.

        """
        return self._camera

    @camera.setter
    def camera(self, camera: Camera) -> None:
        """Set the camera."""
        self._camera = camera

    def clear(self) -> None:
        """Remove all actors and lights from the renderer."""
        self.actors = []
        self.lights = []

    def _generate_texture_code(self, actor_info: dict[str, object], idx: int) -> str:
        """Generate vtk.js JavaScript to load and bind a surface texture.

        Parameters
        ----------
        actor_info : dict
            Actor dictionary, may contain a ``'texture'`` key.
        idx : int
            Actor index used to create unique JS variable names.

        Returns
        -------
        str
            JavaScript code to load the texture image and bind it to the actor,
            or an empty string when no texture is set.

        """
        texture = actor_info.get("texture")
        if texture is None:
            return ""
        tex_url = texture.url  # type: ignore[attr-defined]
        return (
            f"// Load and apply surface texture\n"
            f"const texture{idx} = vtk.Rendering.Core.vtkTexture.newInstance();\n"
            f"texture{idx}.setInterpolate(true);\n"
            f"actor{idx}.addTexture(texture{idx});\n"
            f"const texImg{idx} = new Image();\n"
            f"texImg{idx}.crossOrigin = 'anonymous';\n"
            f"texImg{idx}.onload = function() {{\n"
            f"  texture{idx}.setImage(texImg{idx});\n"
            f"  renderWindow.render();\n"
            f"}};\n"
            f"texImg{idx}.src = '{tex_url}';"
        )

    def _generate_lights_code(self) -> str:
        """Generate vtk.js JavaScript for all lights.

        Falls back to a default directional light when no lights have been added.
        """
        if not self.lights:
            # Default angled directional light for specular highlights
            return (
                "      // Default directional light\n"
                "      const light0 = vtk.Rendering.Core.vtkLight.newInstance();\n"
                "      light0.setLightTypeToSceneLight();\n"
                "      light0.setPositional(false);\n"
                "      light0.setIntensity(1.0);\n"
                "      light0.setPosition(1, 1, 1);\n"
                "      light0.setFocalPoint(0, 0, 0);\n"
                "      renderer.addLight(light0);"
            )
        lines = []
        for idx, light in enumerate(self.lights):
            code = light.generate_vtk_js_code(idx)
            # Indent each line
            indented = "\n".join("      " + line for line in code.splitlines())
            lines.append(indented)
        return "\n\n".join(lines)

    def _generate_actor_code(self, idx: int, actor_info: dict[str, object]) -> str:
        """Generate vtk.js JavaScript for a single actor.

        Parameters
        ----------
        idx : int
            Actor index used for unique JS variable names.
        actor_info : dict
            Actor dictionary with mesh, color, opacity, etc.

        Returns
        -------
        str
            JavaScript code for the actor.

        """
        mesh = actor_info["mesh"]
        color = actor_info.get("color") or (0.5, 0.5, 0.5)
        opacity = actor_info.get("opacity", 1.0)
        pbr = actor_info.get("pbr", False)
        metallic = float(actor_info.get("metallic", 0.0))  # type: ignore[arg-type]
        roughness = float(actor_info.get("roughness", 0.5))  # type: ignore[arg-type]
        show_edges = actor_info.get("show_edges", False)
        edge_color = actor_info.get("edge_color")
        style = actor_info.get("style", "surface")

        source_code = mesh.generate_vtk_js_source(idx)  # type: ignore[attr-defined]
        mapper_setup = mesh.get_mapper_setup(idx)  # type: ignore[attr-defined]

        pbr_code = self._generate_pbr_code(idx, pbr, metallic, roughness)
        edge_code = self._generate_edge_code(
            idx,
            show_edges,
            edge_color,  # type: ignore[arg-type]
        )
        style_code = self._generate_style_code(idx, str(style))
        texture_code = self._generate_texture_code(actor_info, idx)

        return (
            _ACTOR_TEMPLATE.replace("{{SOURCE_CODE}}", source_code)
            .replace("{{INDEX}}", str(idx))
            .replace("{{MAPPER_SETUP}}", mapper_setup)
            .replace("{{COLOR_R}}", str(color[0]))  # type: ignore[index]
            .replace("{{COLOR_G}}", str(color[1]))  # type: ignore[index]
            .replace("{{COLOR_B}}", str(color[2]))  # type: ignore[index]
            .replace("{{OPACITY}}", str(opacity))
            .replace("{{EDGE_CODE}}", edge_code)
            .replace("{{STYLE_CODE}}", style_code)
            .replace("{{PBR_CODE}}", pbr_code)
            .replace("{{TEXTURE_CODE}}", texture_code)
        )

    @staticmethod
    def _generate_pbr_code(
        idx: int,
        pbr: object,
        metallic: float,
        roughness: float,
    ) -> str:
        """Generate vtk.js PBR property code for an actor.

        Parameters
        ----------
        idx : int
            Actor index.
        pbr : object
            Whether PBR is enabled.
        metallic : float
            Metallic factor.
        roughness : float
            Roughness factor.

        Returns
        -------
        str
            JavaScript code or empty string.

        """
        if not pbr:
            return ""
        # vtk.js WebGL uses Phong shading; map metallic/roughness to
        # Phong parameters so both axes are visually distinct:
        #   metallic  → diffuse (1.0 → 0.3) and specular (0.5 → 1.0)
        #   roughness → specularPower (128 → 1)
        specular = round(metallic * 0.5 + 0.5, 4)
        specular_power = max(1, round((1.0 - roughness) ** 2 * 128))
        diffuse = round(1.0 - metallic * 0.7, 4)
        return (
            f"actor{idx}.getProperty().setInterpolationToPhong();\n"
            f"actor{idx}.getProperty().setMetallic({metallic});\n"
            f"actor{idx}.getProperty().setRoughness({roughness});\n"
            f"actor{idx}.getProperty().setAmbient(0.1);\n"
            f"actor{idx}.getProperty().setSpecular({specular});\n"
            f"actor{idx}.getProperty().setSpecularPower({specular_power});\n"
            f"actor{idx}.getProperty().setDiffuse({diffuse});"
        )

    @staticmethod
    def _generate_edge_code(
        idx: int,
        show_edges: object,
        edge_color: str | tuple[float, float, float] | None,
    ) -> str:
        """Generate vtk.js edge visibility code for an actor.

        Parameters
        ----------
        idx : int
            Actor index.
        show_edges : object
            Whether edges are visible.
        edge_color : str or tuple or None
            Edge color.

        Returns
        -------
        str
            JavaScript code or empty string.

        """
        if not show_edges:
            return ""
        if edge_color is None:
            edge_color = (0.0, 0.0, 0.0)
        edge_r, edge_g, edge_b = edge_color[0], edge_color[1], edge_color[2]  # type: ignore[index]
        return (
            f"actor{idx}.getProperty().setEdgeVisibility(true);\n"
            f"actor{idx}.getProperty().setEdgeColor({edge_r}, {edge_g}, {edge_b});"
        )

    @staticmethod
    def _generate_style_code(idx: int, style: str) -> str:
        """Generate vtk.js representation code for an actor.

        Parameters
        ----------
        idx : int
            Actor index.
        style : str
            Rendering style ('surface', 'wireframe', or 'points').

        Returns
        -------
        str
            JavaScript code or empty string.

        """
        # vtk.js Representation constants: POINTS=0, WIREFRAME=1, SURFACE=2
        style_map = {"wireframe": 1, "points": 0, "surface": 2}
        rep = style_map.get(style)
        if rep is not None:
            return f"actor{idx}.getProperty().setRepresentation({rep});"
        return ""

    def _generate_environment_code(self) -> str:
        """Generate vtk.js JavaScript for environment textures.

        Returns
        -------
        str
            JavaScript code for environment lighting, or empty string.

        """
        if self._environment_texture_url:
            return (
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
        if self._environment_texture_cubemap:
            urls = self._environment_texture_cubemap.face_urls
            urls_js = ", ".join(f"'{u}'" for u in urls)
            return (
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
        return ""

    def _generate_camera_code(self) -> str:
        """Generate vtk.js JavaScript for camera setup.

        Returns
        -------
        str
            JavaScript code for camera positioning, or empty string.

        """
        if self._camera is not None:
            px, py, pz = self._camera.position
            fx, fy, fz = self._camera.focal_point
            ux, uy, uz = self._camera.view_up
            angle = self._camera.view_angle
            near, far = self._camera.clipping_range
            return (
                "      const cam = renderer.getActiveCamera();\n"
                f"      cam.setPosition({px}, {py}, {pz});\n"
                f"      cam.setFocalPoint({fx}, {fy}, {fz});\n"
                f"      cam.setViewUp({ux}, {uy}, {uz});\n"
                f"      cam.setViewAngle({angle});\n"
                f"      cam.setClippingRange({near}, {far});"
            )
        if self._view_vector is not None:
            vx, vy, vz = self._view_vector
            ux, uy, uz = self._view_up
            return (
                "      const cam = renderer.getActiveCamera();\n"
                "      const fp = cam.getFocalPoint();\n"
                "      const dist = cam.getDistance();\n"
                f"      const vlen = Math.sqrt({vx}*{vx} + {vy}*{vy} + {vz}*{vz});\n"
                f"      cam.setPosition(fp[0]+dist*{vx}/vlen, fp[1]+dist*{vy}/vlen, fp[2]+dist*{vz}/vlen);\n"  # noqa: E501
                f"      cam.setViewUp({ux}, {uy}, {uz});\n"
                "      renderer.resetCameraClippingRange();"
            )
        return ""

    def _generate_html(self) -> str:
        """Generate HTML fragment with embedded vtk.js JavaScript."""
        actor_js_code = [
            self._generate_actor_code(idx, actor_info) for idx, actor_info in enumerate(self.actors)
        ]

        indented_actors = []
        for actor in actor_js_code:
            lines = actor.split("\n")
            indented_lines = "\n".join("      " + line if line.strip() else "" for line in lines)
            indented_actors.append(indented_lines)
        actors_code = "\n\n".join(indented_actors)

        return (
            _RENDERING_TEMPLATE.replace("{{CONTAINER_ID}}", self.container_id)
            .replace("{{BACKGROUND_R}}", str(self.background[0]))
            .replace("{{BACKGROUND_G}}", str(self.background[1]))
            .replace("{{BACKGROUND_B}}", str(self.background[2]))
            .replace("{{LIGHTS_CODE}}", self._generate_lights_code())
            .replace("{{ACTORS_CODE}}", actors_code)
            .replace("{{ENVIRONMENT_CODE}}", self._generate_environment_code())
            .replace("{{CAMERA_CODE}}", self._generate_camera_code())
        )

    def _repr_html_(self) -> str:
        """IPython representation as HTML for Jupyter notebooks."""
        return self._generate_html()

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


class VTKJSRenderer(_BaseHTMLRenderer):
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

        super().__init__()

        # Automatically load vtk.js in IPython/Jupyter (including Pyodide)
        if IPYTHON_AVAILABLE or PYODIDE_ENV:
            _VTKJSLoader().load()

        self.container = None
        self.use_ipython = IPYTHON_AVAILABLE

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
            super().create_container(element_id)
            return None
        # Create container div directly
        self.container = document.createElement("div")  # type: ignore[attr-defined]
        self.container.setAttribute("id", element_id)  # type: ignore[attr-defined]
        self.container.style.width = "100%"  # type: ignore[attr-defined]
        self.container.style.height = "600px"  # type: ignore[attr-defined]

        # Append to body
        document.body.appendChild(self.container)  # type: ignore[union-attr]

        return self.container

    def render(self) -> None:
        """Render the scene.

        Resets the camera to show all actors and triggers rendering.
        In IPython/Jupyter, generates and displays HTML with vtk.js code.

        Examples
        --------
        >>> renderer.render()  # Display the visualization

        """
        if self.use_ipython:
            html = self._generate_html()
            display(HTML(html))
        else:
            # Direct rendering
            self.renderer.resetCamera()  # type: ignore[attr-defined]
            self.render_window.render()  # type: ignore[attr-defined]

    def clear(self) -> None:
        """Remove all actors from the renderer.

        Examples
        --------
        >>> renderer.clear()  # Remove all visualizations

        """
        super().clear()
        if not self.use_ipython and hasattr(self, "renderer"):
            self.renderer.removeAllActors()


class BrowserRenderer(_BaseHTMLRenderer):
    """Renderer that opens the visualization in the default web browser.

    Used automatically in standard Python environments (outside of
    Jupyter/Pyodide). Generates a standalone HTML file and opens it
    with :func:`webbrowser.open`.

    Examples
    --------
    >>> import pyvista_js as pv
    >>> plotter = pv.Plotter()
    >>> plotter.add_mesh(pv.Sphere(), color='red')
    >>> plotter.show()  # Opens the default browser with the 3D scene

    """

    def render(self) -> None:
        """Write the visualization to a temp HTML file and open it in the browser."""
        html = self._generate_standalone_html()
        with tempfile.NamedTemporaryFile(
            suffix=".html",
            delete=False,
            mode="w",
            encoding="utf-8",
        ) as f:
            f.write(html)
            tmp_path = f.name

        url = pathlib.Path(tmp_path).as_uri()
        webbrowser.open(url)
        logger.info("Opened visualization in browser: %s", url)

    def _generate_standalone_html(self) -> str:
        """Wrap the HTML fragment in a complete standalone HTML page."""
        fragment = self._generate_html()
        container_id = self.container_id
        container_rule = (
            f"    #{container_id} "
            "{ width: 100vw !important; height: 100vh !important; border: none !important; }\n"
        )
        style = (
            "  <style>\n"
            "    html, body { margin: 0; padding: 0; width: 100%; height: 100%;"
            " overflow: hidden; }\n" + container_rule + "  </style>\n"
        )
        return (
            "<!DOCTYPE html>\n"
            "<html>\n"
            "<head>\n"
            "  <meta charset='utf-8'>\n"
            "  <title>pyvista-js</title>\n"
            f"  <script src='{_VTKJS_CDN}'></script>\n" + style + "</head>\n"
            "<body>\n" + fragment + "</body>\n"
            "</html>\n"
        )


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
        self.lights: list[Light] = []
        self.background = (1.0, 1.0, 1.0)  # Default background color
        self._view_vector: tuple[float, float, float] | None = None
        self._view_up: tuple[float, float, float] = (0.0, 1.0, 0.0)
        self._camera: Camera | None = None

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
        mesh: PolyData,
        color: str | tuple[float, float, float] | None = None,
        opacity: float = 1.0,
        pbr: bool = False,  # noqa: FBT001 FBT002
        metallic: float = 0.0,
        roughness: float = 0.5,
        texture: Texture | None = None,
        show_edges: bool = False,  # noqa: FBT001 FBT002
        edge_color: str | tuple[float, float, float] | None = None,
        style: str = "surface",
    ) -> dict[str, object]:
        """Mock mesh addition.

        Parameters
        ----------
        mesh : PolyData
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
        texture : Texture, optional
            Surface texture (stored but not rendered).
        show_edges : bool
            Edge visibility (stored but not rendered).
        edge_color : str or tuple, optional
            Edge color (stored but not rendered).
        style : str
            Rendering style (stored but not rendered).

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
            "texture": texture,
            "show_edges": show_edges,
            "edge_color": edge_color,
            "style": style,
        }
        self.actors.append(actor)
        logger.info("Added mesh with %d points", mesh.n_points)
        return actor

    def render(self) -> None:
        """Mock rendering.

        Logs the number of actors that would be rendered.
        """
        logger.info("Rendering %d actors", len(self.actors))

    def add_light(self, light: Light) -> None:
        """Mock add_light.

        Parameters
        ----------
        light : Light
            The light to add (stored but not rendered).

        """
        self.lights.append(light)
        logger.info("Added light type=%s intensity=%s", light.light_type, light.intensity)

    def clear(self) -> None:
        """Mock clear.

        Removes all actors and lights from the mock renderer.
        """
        self.actors = []
        self.lights = []
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

    @property
    def camera(self) -> Camera | None:
        """Get or set the camera (mock).

        Parameters
        ----------
        camera : Camera
            Camera object (stored but not rendered).

        Returns
        -------
        Camera or None
            The current camera, or None if not set.

        """
        return self._camera

    @camera.setter
    def camera(self, camera: Camera) -> None:
        """Set the camera."""
        self._camera = camera
        logger.info("Set camera: %s", camera)

    def set_environment_texture(self, texture: object) -> None:
        """Mock environment texture.

        Parameters
        ----------
        texture : str or CubeMap
            Environment texture (stored but not rendered).

        """
        logger.info("Set environment texture: %s", texture)


def get_renderer() -> VTKJSRenderer | BrowserRenderer | MockRenderer:
    """Get appropriate renderer for current environment.

    Automatically detects whether running in Pyodide/browser and
    returns the appropriate renderer implementation.

    Returns
    -------
    VTKJSRenderer or BrowserRenderer or MockRenderer
        - VTKJSRenderer if in Pyodide or IPython environment
        - BrowserRenderer in standard Python (opens the default browser)
        - MockRenderer if ``PYVISTA_JS_NO_BROWSER=1`` is set (for testing/CI)

    Examples
    --------
    >>> # Automatically gets the right renderer
    >>> renderer = get_renderer()
    >>>
    >>> # In Pyodide or Jupyter: returns VTKJSRenderer
    >>> # In standard Python: returns BrowserRenderer (opens browser)
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

    Set the environment variable ``PYVISTA_JS_NO_BROWSER=1`` to suppress
    browser opening (useful for CI/CD and automated testing).

    """
    # Use VTKJSRenderer if in Pyodide with vtk.js OR if IPython is available
    if (PYODIDE_ENV and VTK_AVAILABLE) or IPYTHON_AVAILABLE:
        return VTKJSRenderer()
    # Respect opt-out env var for CI/testing
    if os.environ.get("PYVISTA_JS_NO_BROWSER"):
        return MockRenderer()
    return BrowserRenderer()
