"""Camera class for pyvista-js.

Provides a PyVista-like camera interface for controlling the viewpoint
in vtk.js scenes.
"""

from __future__ import annotations


class Camera:
    """Represents a virtual camera in a 3D scene.

    Provides a PyVista-like API for controlling camera position, orientation,
    and projection settings in vtk.js scenes.

    Parameters
    ----------
    position : tuple of float, optional
        Camera position as (x, y, z). Default is (0, 0, 1).
    focal_point : tuple of float, optional
        Point the camera looks at as (x, y, z). Default is (0, 0, 0).
    view_up : tuple of float, optional
        View-up vector as (x, y, z). Default is (0, 1, 0).
    view_angle : float, optional
        Camera view angle (field of view) in degrees. Default is 30.0.
    clipping_range : tuple of float, optional
        Near and far clipping plane distances as (near, far).
        Default is (0.01, 1000.01).

    Examples
    --------
    >>> import pyvista_js as pv
    >>> camera = pv.Camera()
    >>> camera.position = (5, 5, 5)
    >>> camera.focal_point = (0, 0, 0)
    >>> plotter = pv.Plotter()
    >>> _ = plotter.add_mesh(pv.Sphere())
    >>> plotter.camera = camera
    >>> plotter.show()  # doctest: +SKIP

    """

    def __init__(
        self,
        position: tuple[float, float, float] = (0.0, 0.0, 1.0),
        focal_point: tuple[float, float, float] = (0.0, 0.0, 0.0),
        view_up: tuple[float, float, float] = (0.0, 1.0, 0.0),
        view_angle: float = 30.0,
        clipping_range: tuple[float, float] = (0.01, 1000.01),
    ) -> None:
        """Initialize a Camera instance."""
        self.position = position
        self.focal_point = focal_point
        self.view_up = view_up
        self.view_angle = view_angle
        self.clipping_range = clipping_range

    @property
    def position(self) -> tuple[float, float, float]:
        """Get or set the camera position.

        Parameters
        ----------
        value : tuple of float
            Camera position as (x, y, z).

        Returns
        -------
        tuple of float
            Camera position as (x, y, z).

        Examples
        --------
        >>> import pyvista_js as pv
        >>> camera = pv.Camera()
        >>> camera.position = (5, 0, 0)
        >>> camera.position
        (5.0, 0.0, 0.0)

        """
        return self._position

    @position.setter
    def position(self, value: tuple[float, float, float]) -> None:
        """Set the camera position."""
        self._position = (float(value[0]), float(value[1]), float(value[2]))

    @property
    def focal_point(self) -> tuple[float, float, float]:
        """Get or set the camera focal point.

        Parameters
        ----------
        value : tuple of float
            Focal point as (x, y, z).

        Returns
        -------
        tuple of float
            Focal point as (x, y, z).

        Examples
        --------
        >>> import pyvista_js as pv
        >>> camera = pv.Camera()
        >>> camera.focal_point = (1, 2, 3)
        >>> camera.focal_point
        (1.0, 2.0, 3.0)

        """
        return self._focal_point

    @focal_point.setter
    def focal_point(self, value: tuple[float, float, float]) -> None:
        """Set the camera focal point."""
        self._focal_point = (float(value[0]), float(value[1]), float(value[2]))

    @property
    def view_up(self) -> tuple[float, float, float]:
        """Get or set the view-up vector.

        Parameters
        ----------
        value : tuple of float
            View-up vector as (x, y, z).

        Returns
        -------
        tuple of float
            View-up vector as (x, y, z).

        Examples
        --------
        >>> import pyvista_js as pv
        >>> camera = pv.Camera()
        >>> camera.view_up = (0, 0, 1)
        >>> camera.view_up
        (0.0, 0.0, 1.0)

        """
        return self._view_up

    @view_up.setter
    def view_up(self, value: tuple[float, float, float]) -> None:
        """Set the view-up vector."""
        self._view_up = (float(value[0]), float(value[1]), float(value[2]))

    @property
    def view_angle(self) -> float:
        """Get or set the camera view angle in degrees.

        Parameters
        ----------
        value : float
            View angle in degrees (field of view).

        Returns
        -------
        float
            View angle in degrees.

        Examples
        --------
        >>> import pyvista_js as pv
        >>> camera = pv.Camera()
        >>> camera.view_angle = 45.0
        >>> camera.view_angle
        45.0

        """
        return self._view_angle

    @view_angle.setter
    def view_angle(self, value: float) -> None:
        """Set the camera view angle."""
        self._view_angle = float(value)

    @property
    def clipping_range(self) -> tuple[float, float]:
        """Get or set the clipping range (near, far).

        Parameters
        ----------
        value : tuple of float
            Near and far clipping plane distances as (near, far).

        Returns
        -------
        tuple of float
            Clipping range as (near, far).

        Examples
        --------
        >>> import pyvista_js as pv
        >>> camera = pv.Camera()
        >>> camera.clipping_range = (0.1, 100.0)
        >>> camera.clipping_range
        (0.1, 100.0)

        """
        return self._clipping_range

    @clipping_range.setter
    def clipping_range(self, value: tuple[float, float]) -> None:
        """Set the clipping range."""
        self._clipping_range = (float(value[0]), float(value[1]))

    def __repr__(self) -> str:
        """Return string representation of the camera."""
        return (
            f"Camera("
            f"position={self._position}, "
            f"focal_point={self._focal_point}, "
            f"view_up={self._view_up}, "
            f"view_angle={self._view_angle}, "
            f"clipping_range={self._clipping_range})"
        )
