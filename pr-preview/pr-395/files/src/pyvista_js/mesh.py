"""Mesh classes and utilities for pyvista-js.

This module provides classes for working with meshes, including
UnstructuredGrid and CellType.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from numpy.typing import ArrayLike


class PointData:
    """Dict-like container for point data arrays.

    This class provides a dictionary interface for storing named scalar arrays
    associated with mesh points, mimicking PyVista's point_data API.

    Examples
    --------
    >>> import pyvista_js as pv
    >>> import numpy as np
    >>> mesh = pv.Sphere()
    >>> mesh.point_data['elevation'] = mesh.points[:, 2]
    >>> 'elevation' in mesh.point_data
    True

    Render with scalar coloring:

    >>> plotter = pv.Plotter()
    >>> _ = plotter.add_mesh(mesh, scalars='elevation', cmap='viridis')
    >>> plotter.show()  # doctest: +SKIP

    """

    def __init__(self, data: dict[str, np.ndarray] | None = None) -> None:
        """Initialize an empty PointData container."""
        self._arrays: dict[str, np.ndarray] = data if data is not None else {}

    def __setitem__(self, name: str, array: ArrayLike) -> None:
        """Set a named array.

        Parameters
        ----------
        name : str
            Name of the array.
        array : array-like
            Data array to store.

        """
        self._arrays[name] = np.asarray(array)

    def __getitem__(self, name: str) -> np.ndarray:
        """Get a named array.

        Parameters
        ----------
        name : str
            Name of the array.

        Returns
        -------
        np.ndarray
            The requested array.

        """
        return self._arrays[name]

    def __contains__(self, name: str) -> bool:
        """Check if an array with the given name exists.

        Parameters
        ----------
        name : str
            Name to check.

        Returns
        -------
        bool
            True if the array exists.

        """
        return name in self._arrays

    def __len__(self) -> int:
        """Return the number of arrays."""
        return len(self._arrays)

    def keys(self) -> list[str]:
        """Return the names of all arrays.

        Returns
        -------
        list
            List of array names.

        """
        return list(self._arrays.keys())

    def items(self) -> list[tuple[str, np.ndarray]]:
        """Return (name, array) pairs.

        Returns
        -------
        list
            List of (name, array) tuples.

        """
        return list(self._arrays.items())

    def values(self) -> list[np.ndarray]:
        """Return all arrays.

        Returns
        -------
        list
            List of arrays.

        """
        return list(self._arrays.values())


_CIRCLE_MIN_RESOLUTION = 3
_VECTOR_COMPONENTS = 3  # Number of components in a 3D vector (x, y, z)
_TUBE_MIN_SIDES = 3


class UnstructuredGrid:
    """Represents an unstructured grid.

    Parameters
    ----------
    points : array-like
        Vertex coordinates as an (n, 3) array.
    cells : array-like, optional
        Cell connectivity information.
    cell_types : array-like, optional
        Array of cell types for each cell.

    """

    def __init__(
        self,
        points: ArrayLike,
        cells: ArrayLike | None = None,
        cell_types: ArrayLike | None = None,
    ) -> None:
        """Initialize an UnstructuredGrid mesh."""
        self.points = np.asarray(points)
        self.cells = np.asarray(cells) if cells is not None else None
        self.cell_types = np.asarray(cell_types) if cell_types is not None else None
        self._point_data = PointData()
        self._cell_data = PointData()

    @property
    def point_data(self) -> PointData:
        """Access point data arrays.

        Returns
        -------
        PointData
            Dict-like container for point data arrays.

        """
        return self._point_data

    @property
    def cell_data(self) -> PointData:
        """Access cell data arrays.

        Returns
        -------
        PointData
            Dict-like container for cell data arrays.

        """
        return self._cell_data

    def __setitem__(self, name: str, array: ArrayLike) -> None:
        """Set a point data array using dictionary-style access.

        Parameters
        ----------
        name : str
            Name of the array.
        array : array-like
            Data array to store.

        Examples
        --------
        >>> import pyvista_js as pv
        >>> import numpy as np
        >>> points = [[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]]
        >>> cells = [4, 0, 1, 2, 3]
        >>> cell_types = [pv.CellType.QUAD]
        >>> grid = pv.UnstructuredGrid(points, cells, cell_types)
        >>> grid['elevation'] = [1.0, 2.0, 3.0, 4.0]

        """
        self._point_data[name] = array

    def __getitem__(self, name: str) -> np.ndarray:
        """Get a point data array using dictionary-style access.

        Parameters
        ----------
        name : str
            Name of the array.

        Returns
        -------
        np.ndarray
            The requested array.

        """
        return self._point_data[name]

    @property
    def n_points(self) -> int:
        """Return the number of points."""
        return len(self.points)

    @property
    def n_cells(self) -> int:
        """Return the number of cells."""
        return len(self.cells) if self.cells is not None else 0

    def to_scene_data(self) -> dict[str, object]:
        """Return a JSON-serializable dict describing this mesh source.

        Returns
        -------
        dict
            Source configuration with ``"type"`` key and type-specific parameters.

        """
        data = {
            "type": "unstructured_grid",
            "points": self.points.flatten().tolist(),
        }

        if self.cells is not None:
            data["cells"] = self.cells.tolist()

        if self.cell_types is not None:
            data["cell_types"] = self.cell_types.tolist()

        # Inject point data arrays
        if len(self._point_data) > 0:
            point_data_arrays: list[dict[str, object]] = []
            for name, array in self._point_data.items():
                n_components = 1 if array.ndim == 1 else array.shape[1]
                point_data_arrays.append(
                    {
                        "name": name,
                        "numberOfComponents": n_components,
                        "values": array.flatten().tolist(),
                    },
                )
            data["point_data"] = point_data_arrays

        # Inject cell data arrays
        if len(self._cell_data) > 0:
            cell_data_arrays: list[dict[str, object]] = []
            for name, array in self._cell_data.items():
                n_components = 1 if array.ndim == 1 else array.shape[1]
                cell_data_arrays.append(
                    {
                        "name": name,
                        "numberOfComponents": n_components,
                        "values": array.flatten().tolist(),
                    },
                )
            data["cell_data"] = cell_data_arrays

        return data

    def __getstate__(self) -> dict[str, object]:
        """Return state for pickling.

        Returns
        -------
        dict
            State dictionary containing points, cells, point data, and cell data.

        """
        return {
            "points": self.points,
            "cells": self.cells,
            "cell_types": self.cell_types,
            "_point_data": self._point_data,
            "_cell_data": self._cell_data,
        }

    def __setstate__(self, state: dict[str, object]) -> None:
        """Restore state from pickle.

        Parameters
        ----------
        state : dict
            State dictionary from __getstate__.

        """
        self.points = state["points"]  # type: ignore[assignment]
        self.cells = state["cells"]  # type: ignore[assignment]
        self.cell_types = state.get("cell_types")  # type: ignore[assignment]
        self._point_data = state["_point_data"]  # type: ignore[assignment]
        self._cell_data = state.get("_cell_data")  # type: ignore[assignment]


# CellType constants
class CellType:
    """Cell types for UnstructuredGrid.

    This class defines constants for cell types used in UnstructuredGrid.
    These correspond to VTK cell types.

    Examples
    --------
    >>> import pyvista_js as pv
    >>> grid = pv.UnstructuredGrid(
    ...     points=[[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]],
    ...     cells=[4, 0, 1, 2, 3],
    ...     cell_types=[pv.CellType.QUAD],
    ... )

    """

    # 0D cells
    VERTEX = 1
    POLY_VERTEX = 2

    # 1D cells
    LINE = 3
    POLY_LINE = 4

    # 2D cells
    TRIANGLE = 5
    TRIANGLE_STRIP = 6
    POLYGON = 7
    PIXEL = 8
    QUAD = 9
    QUADRATIC_TRIANGLE = 10
    BIQUADRATIC_TRIANGLE = 11
    QUADRATIC_QUAD = 12
    CONVEX_POLYGON = 14

    # 3D cells
    TETRA = 10
    VOXEL = 11
    HEXAHEDRON = 12
    WEDGE = 13
    PYRAMID = 14
    PENTAGONAL_PRISM = 15
    HEXAGONAL_PRISM = 16
    QUADRATIC_TETRA = 17
    QUADRATIC_HEXAHEDRON = 18
    QUADRATIC_WEDGE = 19
    QUADRATIC_PYRAMID = 20
    TRIQUADRATIC_HEXAHEDRON = 22
    QUADRATIC_LINEAR_QUAD = 23
    QUADRATIC_LINEAR_WEDGE = 24
    BIQUADRATIC_QUADRATIC_WEDGE = 25
    BIQUADRATIC_QUADRATIC_HEXAHEDRON = 26
    CUBIC_LINE = 27
    HIGHER_ORDER_TRIANGLE = 28
    HIGHER_ORDER_QUAD = 29
    HIGHER_ORDER_POLYGON = 30
    HIGHER_ORDER_LINE = 31
    HIGHER_ORDER_TETRAHEDRON = 32
    HIGHER_ORDER_WEDGE = 33
    HIGHER_ORDER_PYRAMID = 34
    HIGHER_ORDER_QUADRATIC_QUAD = 35
    HIGHER_ORDER_QUADRATIC_LINEAR_QUAD = 36
    HIGHER_ORDER_QUADRATIC_TETRAHEDRON = 38
    HIGHER_ORDER_BIQUADRATIC_QUAD = 39
    HIGHER_ORDER_TRIQUADRATIC_HEXAHEDRON = 40
    HIGHER_ORDER_QUADRATIC_LINEAR_WEDGE = 41
    HIGHER_ORDER_BIQUADRATIC_QUADRATIC_WEDGE = 42
    PARAMETRIC_REGION = 44
