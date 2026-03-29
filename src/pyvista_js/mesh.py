"""Mesh classes and utilities for pyvista-js.

This module provides classes for working with meshes, including
UnstructuredGrid and CellType.
"""

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
