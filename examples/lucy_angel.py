"""Lucy Angel example with custom lighting.

This example demonstrates custom lighting setup using the Lucy Angel mesh
from The Stanford 3D Scanning Repository.
"""

import pyvista_js as pv
from pyvista_js import examples

# Download the Lucy Angel dataset
dataset = examples.download_lucy()

# Create a light at the "flame" position
flame_light = pv.Light(
    color=[0.886, 0.345, 0.133],
    position=[550, 140, 950],
    intensity=1.5,
    positional=True,
    cone_angle=90,
    attenuation_values=(0.001, 0.005, 0),
)

# Create a scene light with lower intensity
scene_light = pv.Light(intensity=0.2)

# Create a plotter with no default lights
pl = pv.Plotter(lighting=None)
_ = pl.add_mesh(dataset, smooth_shading=True)
pl.add_light(flame_light)
pl.add_light(scene_light)
pl.background_color = "k"
pl.show()
