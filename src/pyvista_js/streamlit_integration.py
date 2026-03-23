"""Streamlit integration for pyvista-js.

Provides components for displaying pyvista-js visualizations in Streamlit and stlite.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

from jinja2 import Environment, FileSystemLoader, StrictUndefined

if TYPE_CHECKING:
    from .plotter import Plotter

# Load JavaScript template
_TEMPLATES_DIR = Path(__file__).parent / "templates"
_STREAMLIT_TEMPLATE = (_TEMPLATES_DIR / "streamlit.html").read_text()
_jinja_env = Environment(loader=FileSystemLoader(_TEMPLATES_DIR), undefined=StrictUndefined, autoescape=False)  # noqa: S701

# Check if streamlit is available
try:
    import streamlit as st
    import streamlit.components.v1 as components

    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False


def pyvista_chart(plotter: Plotter, height: int = 600, key: str | None = None) -> None:
    """Display a pyvista-js Plotter in Streamlit.

    This function renders a pyvista-js visualization as a Streamlit component.
    It works in both standard Streamlit and stlite environments.

    Parameters
    ----------
    plotter : Plotter
        The pyvista-js Plotter instance to display.
    height : int, optional
        Height of the visualization in pixels. Default is 600.
    key : str, optional
        Unique key for the component.

    Examples
    --------
    >>> import pyvista_js as pv  # doctest: +SKIP
    >>> import streamlit as st  # doctest: +SKIP
    >>> plotter = pv.Plotter()  # doctest: +SKIP
    >>> sphere = pv.Sphere()  # doctest: +SKIP
    >>> plotter.add_mesh(sphere, color='red')  # doctest: +SKIP
    >>> pv.pyvista_chart(plotter, height=500)  # doctest: +SKIP

    """
    if not STREAMLIT_AVAILABLE:
        msg = "Streamlit is not available. Install with: pip install streamlit"
        raise ImportError(msg)

    # Generate HTML for vtk.js visualization
    html_code = _generate_vtkjs_html(plotter, height)

    # Display using Streamlit components
    components.html(html_code, height=height, scrolling=False, key=key)


def _generate_vtkjs_html(plotter: Plotter, height: int) -> str:
    """Generate HTML code for vtk.js visualization.

    Parameters
    ----------
    plotter : Plotter
        The Plotter instance.
    height : int
        Container height.

    Returns
    -------
    str
        HTML code with embedded vtk.js visualization.

    """
    # Extract mesh data from plotter
    meshes_data = []
    for actor_info in plotter.actors:
        mesh = actor_info["mesh"]
        meshes_data.append(
            {
                "points": mesh.points.tolist(),
                "n_points": mesh.n_points,
                "color": actor_info["color"],
                "opacity": actor_info["opacity"],
            },
        )

    return _jinja_env.from_string(_STREAMLIT_TEMPLATE).render(
        HEIGHT=str(height),
        MESHES_DATA=json.dumps(meshes_data),
    )


# Convenience function for Streamlit
if STREAMLIT_AVAILABLE:
    # Add to streamlit namespace
    st.pyvista_chart = pyvista_chart
