"""Tests for pyvista-js running in Pyodide environment.

These tests use pytest-pyodide to verify that pyvista-js works correctly
in a browser-based Pyodide (WebAssembly) environment.

Note:
----
These tests require Pyodide to be available. The tests will be run
in a browser environment using Selenium or Playwright.

"""

from __future__ import annotations

import pytest
from pytest_pyodide import run_in_pyodide


@run_in_pyodide
def test_basic_import(selenium):
    """Test that pyvista_js can be imported in Pyodide.

    This is a basic smoke test to verify that the package loads
    without errors in the Pyodide environment.

    Parameters
    ----------
    selenium : fixture
        The selenium fixture provided by pytest-pyodide.

    """
    import pyvista_js as pv

    # Verify the module is loaded
    assert pv.__version__ is not None
    assert hasattr(pv, "Plotter")


@run_in_pyodide
def test_sphere_creation(selenium):
    """Test that Sphere mesh can be created in Pyodide.

    Parameters
    ----------
    selenium : fixture
        The selenium fixture provided by pytest-pyodide.

    """
    from pyvista_js import Sphere

    sphere = Sphere()
    assert sphere is not None
    assert hasattr(sphere, "points")
    assert len(sphere.points) > 0


@run_in_pyodide
def test_plotter_creation(selenium):
    """Test that Plotter can be created in Pyodide.

    Parameters
    ----------
    selenium : fixture
        The selenium fixture provided by pytest-pyodide.

    """
    from pyvista_js import Plotter, Sphere

    plotter = Plotter()
    assert plotter is not None
    assert hasattr(plotter, "actors")

    # Add a mesh
    plotter.add_mesh(Sphere(), color="red")
    assert len(plotter.actors) == 1


@run_in_pyodide
def test_html_generation(selenium):
    """Test that HTML can be generated in Pyodide.

    Parameters
    ----------
    selenium : fixture
        The selenium fixture provided by pytest-pyodide.

    """
    from pyvista_js import Plotter, Sphere

    plotter = Plotter()
    plotter.add_mesh(Sphere(), color="blue")

    # Generate HTML
    html = plotter.generate_standalone_html()
    assert html is not None
    assert len(html) > 0
    assert "<html" in html
    assert "</html>" in html


@run_in_pyodide
def test_line_creation(selenium):
    """Test that Line mesh can be created in Pyodide.

    Parameters
    ----------
    selenium : fixture
        The selenium fixture provided by pytest-pyodide.

    """
    from pyvista_js import Line

    line = Line()
    assert line is not None
    assert hasattr(line, "points")


@run_in_pyodide
def test_multiple_meshes(selenium):
    """Test that multiple meshes can be added to a plotter in Pyodide.

    Parameters
    ----------
    selenium : fixture
        The selenium fixture provided by pytest-pyodide.

    """
    from pyvista_js import Plotter, Sphere

    plotter = Plotter()
    plotter.add_mesh(Sphere(radius=1.0), color="red")
    plotter.add_mesh(Sphere(radius=0.5, center=(2, 0, 0)), color="blue")

    assert len(plotter.actors) == 2


@run_in_pyodide
def test_mesh_filters_shrink(selenium):
    """Test that shrink filter works in Pyodide.

    Parameters
    ----------
    selenium : fixture
        The selenium fixture provided by pytest-pyodide.

    """
    from pyvista_js import Plotter, Sphere

    sphere = Sphere()
    shrunk = sphere.shrink(shrink_factor=0.5)

    plotter = Plotter()
    plotter.add_mesh(shrunk, color="red")

    assert len(plotter.actors) == 1


@run_in_pyodide
def test_mesh_filters_tube(selenium):
    """Test that tube filter works in Pyodide.

    Parameters
    ----------
    selenium : fixture
        The selenium fixture provided by pytest-pyodide.

    """
    from pyvista_js import Line, Plotter

    line = Line()
    tube = line.tube(radius=0.1)

    plotter = Plotter()
    plotter.add_mesh(tube, color="blue")

    assert len(plotter.actors) == 1


@run_in_pyodide
@pytest.mark.skip(reason="clip filter requires vtk.js execution in browser")
def test_mesh_filters_clip(selenium):
    """Test that clip filter works in Pyodide.

    Parameters
    ----------
    selenium : fixture
        The selenium fixture provided by pytest-pyodide.

    """
    from pyvista_js import Plotter, Sphere

    sphere = Sphere()
    clipped = sphere.clip(normal="x")

    plotter = Plotter()
    plotter.add_mesh(clipped, color="red")

    assert len(plotter.actors) == 1


@run_in_pyodide
@pytest.mark.skip(reason="contour filter requires scalar arrays")
def test_mesh_filters_contour(selenium):
    """Test that contour filter works in Pyodide.

    Parameters
    ----------
    selenium : fixture
        The selenium fixture provided by pytest-pyodide.

    """
    from pyvista_js import Plotter, Sphere

    sphere = Sphere()
    elevation = sphere.points[:, 2]
    contours = sphere.contour(scalars=elevation, isosurfaces=5)

    plotter = Plotter()
    plotter.add_mesh(contours, color="green")

    assert len(plotter.actors) == 1


@run_in_pyodide
def test_camera_settings(selenium):
    """Test that camera settings work in Pyodide.

    Parameters
    ----------
    selenium : fixture
        The selenium fixture provided by pytest-pyodide.

    """
    from pyvista_js import Plotter, Sphere

    plotter = Plotter()
    plotter.add_mesh(Sphere(), color="red")

    # Test camera position
    plotter.camera_position = [5, 5, 5]
    assert plotter.camera_position is not None


@run_in_pyodide
def test_background_color(selenium):
    """Test that background color can be set in Pyodide.

    Parameters
    ----------
    selenium : fixture
        The selenium fixture provided by pytest-pyodide.

    """
    from pyvista_js import Plotter, Sphere

    plotter = Plotter()
    plotter.add_mesh(Sphere(), color="white")

    # Set background color
    plotter.background_color = (0.2, 0.3, 0.4)
    assert plotter.background_color == (0.2, 0.3, 0.4)
