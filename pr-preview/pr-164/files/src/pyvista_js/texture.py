"""Texture class for pyvista-js.

Provides surface texture support compatible with PyVista API.
"""

from __future__ import annotations


class Texture:
    """Surface texture wrapping an image URL.

    Mirrors the PyVista :class:`pyvista.Texture` API for browser-based
    rendering via vtk.js. A texture is applied to a mesh by passing it
    to :meth:`~pyvista_js.Plotter.add_mesh` as the ``texture`` argument.

    Parameters
    ----------
    url : str
        URL of the image to use as a texture (PNG, JPEG, etc.).

    Examples
    --------
    >>> import pyvista_js as pv
    >>> from pyvista_js import examples
    >>> texture = examples.download_masonry_texture()
    >>> plotter = pv.Plotter()
    >>> sphere = pv.Sphere()
    >>> plotter.add_mesh(sphere, texture=texture)
    >>> plotter.show()

    """

    def __init__(self, url: str) -> None:
        """Initialize a Texture from an image URL."""
        self.url = url

    def __repr__(self) -> str:
        """Return a string representation of the Texture."""
        return f"Texture(url={self.url!r})"
