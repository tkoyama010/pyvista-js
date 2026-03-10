"""Example datasets for pyvista-js.

Provides download helpers for standard datasets, mirroring the
``pyvista.examples`` submodule API.
"""

from __future__ import annotations

_PYVISTA_DATA_BASE = "https://raw.githubusercontent.com/pyvista/vtk-data/master/Data"


class CubeMap:
    """Cubemap texture holding six face image URLs.

    Parameters
    ----------
    posx : str
        URL of the positive-X face image.
    negx : str
        URL of the negative-X face image.
    posy : str
        URL of the positive-Y face image.
    negy : str
        URL of the negative-Y face image.
    posz : str
        URL of the positive-Z face image.
    negz : str
        URL of the negative-Z face image.

    Examples
    --------
    >>> from pyvista_js import examples
    >>> cubemap = examples.download_sky_box_cube_map()
    >>> type(cubemap)
    <class 'pyvista_js.examples.CubeMap'>

    .. replite::
       :kernel: pyolite
       :height: 400px
       :prompt: Try it live

       import sys
       sys.path.insert(0, '/drive/src')
       from pyvista_js import examples
       cubemap = examples.download_sky_box_cube_map()
       type(cubemap)

    """

    def __init__(  # noqa: PLR0913
        self,
        posx: str,
        negx: str,
        posy: str,
        negy: str,
        posz: str,
        negz: str,
    ) -> None:
        """Initialize a cubemap with six face URLs."""
        self.posx = posx
        self.negx = negx
        self.posy = posy
        self.negy = negy
        self.posz = posz
        self.negz = negz

    @property
    def face_urls(self) -> list[str]:
        """Return face URLs in the order [+X, -X, +Y, -Y, +Z, -Z]."""
        return [self.posx, self.negx, self.posy, self.negy, self.posz, self.negz]

    def to_skybox(self) -> CubeMap:
        """Return self for API compatibility with PyVista.

        Returns
        -------
        CubeMap
            This cubemap instance.

        Examples
        --------
        >>> from pyvista_js import examples
        >>> cubemap = examples.download_sky_box_cube_map()
        >>> skybox = cubemap.to_skybox()

        .. replite::
           :kernel: pyolite
           :height: 400px
           :prompt: Try it live

           import sys
           sys.path.insert(0, '/drive/src')
           from pyvista_js import examples
           cubemap = examples.download_sky_box_cube_map()
           skybox = cubemap.to_skybox()

        """
        return self


def download_sky_box_cube_map() -> CubeMap:
    """Download the skybox cube map dataset.

    Downloads six face images of the sky box cubemap from the PyVista
    data repository and returns them as a :class:`CubeMap` object.

    Returns
    -------
    CubeMap
        Cubemap containing the six skybox face image URLs.

    Examples
    --------
    >>> import pyvista_js as pv
    >>> from pyvista_js import examples
    >>> cubemap = examples.download_sky_box_cube_map()
    >>> plotter = pv.Plotter()
    >>> plotter.set_environment_texture(cubemap)
    >>> mesh = pv.Sphere()
    >>> plotter.add_mesh(mesh, color='white', pbr=True, metallic=0.8, roughness=0.1)
    >>> plotter.show()

    .. replite::
       :kernel: pyolite
       :height: 400px
       :prompt: Try it live

       import sys
       sys.path.insert(0, '/drive/src')
       import pyvista_js as pv
       from pyvista_js import examples
       cubemap = examples.download_sky_box_cube_map()
       plotter = pv.Plotter()
       plotter.set_environment_texture(cubemap)
       mesh = pv.Sphere()
       plotter.add_mesh(mesh, color='white', pbr=True, metallic=0.8, roughness=0.1)
       plotter.show()

    """
    base = _PYVISTA_DATA_BASE
    return CubeMap(
        posx=f"{base}/skybox2-posx.jpg",
        negx=f"{base}/skybox2-negx.jpg",
        posy=f"{base}/skybox2-posy.jpg",
        negy=f"{base}/skybox2-negy.jpg",
        posz=f"{base}/skybox2-posz.jpg",
        negz=f"{base}/skybox2-negz.jpg",
    )
