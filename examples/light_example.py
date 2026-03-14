"""Light example: Demonstrating custom lights on a sphere scene.

This example shows how to use the Light class to add colored lights
to a 3D scene, replacing the default directional light.
"""

import pyvista_js as pv

plotter = pv.Plotter()
plotter.background_color = "black"

# Central white sphere
plotter.add_mesh(pv.Sphere(radius=1.0, center=(0, 0, 0)), color="white")

# Red light from the left
red_light = pv.Light(
    position=(-5, 0, 3),
    focal_point=(0, 0, 0),
    color="red",
    intensity=1.5,
)
plotter.add_light(red_light)

# Blue light from the right
blue_light = pv.Light(
    position=(5, 0, 3),
    focal_point=(0, 0, 0),
    color="blue",
    intensity=1.5,
)
plotter.add_light(blue_light)

# White spotlight from above
spot = pv.Light(
    position=(0, 6, 0),
    focal_point=(0, 0, 0),
    color="white",
    intensity=1.0,
    positional=True,
    cone_angle=25.0,
    cone_falloff=3.0,
)
plotter.add_light(spot)

plotter.view_vector((1, 1, 1))
plotter.show()
