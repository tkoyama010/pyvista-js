"""Example datasets for pyvista-js.

Provides download helpers for standard datasets, mirroring the
``pyvista.examples`` submodule API.
"""

from __future__ import annotations

import sys
import urllib.request
from pathlib import Path
from typing import TYPE_CHECKING

from pyvista_js.texture import Texture

if TYPE_CHECKING:
    from pyvista_js.mesh import PolyData

_PYVISTA_DATA_BASE = "https://raw.githubusercontent.com/pyvista/vtk-data/master/Data"
_GLTF_SAMPLE_BASE = "https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Models/master/2.0"
_CACHE_DIR = Path.home() / ".pyvista_js" / "examples"


def _download_url(url: str, filename: str) -> Path:
    """Download a file from an arbitrary URL to the local cache.

    Parameters
    ----------
    url : str
        Full URL of the file to download.
    filename : str
        Local filename to save the file as inside the cache directory.

    Returns
    -------
    Path
        Local path to the downloaded file.

    """
    _CACHE_DIR.mkdir(parents=True, exist_ok=True)
    local = _CACHE_DIR / filename
    if not local.exists():
        if "pyodide" in sys.modules:
            _fetch_with_js(url, local)
        else:
            urllib.request.urlretrieve(url, local)  # noqa: S310
    return local


def _download_file(filename: str) -> Path:
    """Download a file from the PyVista vtk-data repository to a local cache.

    Parameters
    ----------
    filename : str
        Filename within the vtk-data ``Data/`` directory.

    Returns
    -------
    Path
        Local path to the downloaded file.

    """
    _CACHE_DIR.mkdir(parents=True, exist_ok=True)
    local = _CACHE_DIR / filename
    if not local.exists():
        url = f"{_PYVISTA_DATA_BASE}/{filename}"
        if "pyodide" in sys.modules:
            _fetch_with_js(url, local)
        else:
            urllib.request.urlretrieve(url, local)  # noqa: S310
    return local


def _fetch_with_js(url: str, local: Path) -> None:
    """Download a file using JavaScript XMLHttpRequest (Pyodide fallback).

    Parameters
    ----------
    url : str
        URL to download.
    local : Path
        Local path to save the file.

    """
    from js import Uint8Array, XMLHttpRequest  # noqa: PLC0415

    req = XMLHttpRequest.new()
    req.open("GET", url, False)  # noqa: FBT003
    req.responseType = "arraybuffer"
    req.send(None)
    if req.status != 200:  # noqa: PLR2004
        msg = f"Failed to download {url}: HTTP {req.status}"
        raise OSError(msg)
    js_array = Uint8Array.new(req.response)
    local.write_bytes(js_array.to_py().tobytes())


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

        """
        return self


def download_trumpet() -> PolyData:
    """Download the trumpet dataset.

    Downloads ``trumpet.obj`` from the PyVista vtk-data repository and
    returns it as a :class:`~pyvista_js.PolyData` mesh, mirroring the
    ``pyvista.examples.download_trumpet`` API.

    Returns
    -------
    pyvista_js.PolyData
        The trumpet mesh.

    Examples
    --------
    >>> from pyvista_js import examples
    >>> mesh = examples.download_trumpet()  # doctest: +SKIP
    >>> type(mesh).__name__  # doctest: +SKIP
    '_OBJMesh'

    """
    from .readers import OBJReader  # noqa: PLC0415

    path = _download_file("trumpet.obj")
    return OBJReader(path).read()


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
    >>> _ = plotter.add_mesh(mesh, color='white', pbr=True, metallic=0.8, roughness=0.1)
    >>> plotter.show()  # doctest: +SKIP

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


def download_masonry_texture() -> Texture:
    """Download the masonry texture dataset.

    Downloads a brick masonry image from the PyVista data repository
    and returns it as a :class:`~pyvista_js.texture.Texture` object.

    Returns
    -------
    Texture
        Texture wrapping the masonry image URL.

    Examples
    --------
    >>> import pyvista_js as pv
    >>> from pyvista_js import examples
    >>> texture = examples.download_masonry_texture()
    >>> surf = pv.Cylinder()
    >>> plotter = pv.Plotter()
    >>> _ = plotter.add_mesh(surf, texture=texture)
    >>> plotter.show()  # doctest: +SKIP

    """
    return Texture(f"{_PYVISTA_DATA_BASE}/masonry.bmp")


def download_damaged_helmet() -> PolyData:
    """Download the damaged helmet glTF example.

    Downloads ``DamagedHelmet.gltf`` from the KhronosGroup glTF-Sample-Models
    repository and returns it as a :class:`~pyvista_js.PolyData` mesh,
    mirroring the ``pyvista.examples.gltf.download_damaged_helmet`` API.

    Returns
    -------
    pyvista_js.PolyData
        The damaged helmet mesh.

    Examples
    --------
    >>> from pyvista_js import examples
    >>> mesh = examples.download_damaged_helmet()  # doctest: +SKIP
    >>> type(mesh).__name__  # doctest: +SKIP
    '_GLTFMesh'

    """
    from .readers import GLTFReader  # noqa: PLC0415

    url = f"{_GLTF_SAMPLE_BASE}/DamagedHelmet/glTF-Embedded/DamagedHelmet.gltf"
    path = _download_url(url, "DamagedHelmet.gltf")
    return GLTFReader(path).read()


def download_cad_model() -> PolyData:
    """Download the CAD model dataset.

    Downloads ``42400-IDGH.stl`` from the PyVista vtk-data repository and
    returns it as a :class:`~pyvista_js.PolyData` mesh, mirroring the
    ``pyvista.examples.download_cad_model`` API.

    Returns
    -------
    pyvista_js.PolyData
        The CAD model mesh.

    Examples
    --------
    >>> from pyvista_js import examples
    >>> mesh = examples.download_cad_model()  # doctest: +SKIP
    >>> type(mesh).__name__  # doctest: +SKIP
    '_STLMesh'

    """
    from .readers import STLReader  # noqa: PLC0415

    path = _download_file("42400-IDGH.stl")
    return STLReader(path).read()
