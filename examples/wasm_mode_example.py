"""Example: Using pyvista-js with WASM configuration in JupyterLite/Pyodide.

This example demonstrates how to use the new dual-mode support to render
visualizations in WASM environments like JupyterLite.
"""

# %% [markdown]
# # WASM Mode Example
#
# This notebook demonstrates how to use pyvista-js in WASM mode with
# programmatic configuration.

# %%
import json

from pyvista_js import Sphere
from pyvista_js.rendering import get_renderer

# %%
# Create a renderer and add a sphere
renderer = get_renderer()
sphere = Sphere(radius=1.0, theta_resolution=32, phi_resolution=32)
renderer.add_mesh_actor(sphere, color="red", opacity=0.8)

# %%
# Generate configuration object for WASM mode
config = renderer.generate_config_object()

# View the configuration
print("Configuration object keys:", list(config.keys()))
print("\nActors:", len(config.get("actors", [])))
print("Background color:", config["backgroundColor"])

# %%
# Serialize to JSON
json_config = json.dumps(config, indent=2)
print("JSON config (first 500 chars):")
print(json_config[:500] + "...")

# %%
# In a real JupyterLite environment, you would pass this to JavaScript:
#
# from js import initViewer
# import js
# config_js = js.JSON.parse(json_config)
# viewer = initViewer(config_js)
#
# This creates the vtk.js viewer with the configuration.

# %% [markdown]
# ## Multiple Actors Example

# %%
from pyvista_js import Cube, Cylinder

renderer = get_renderer()

# Add multiple meshes
sphere = Sphere(center=(-2, 0, 0), radius=0.5)
renderer.add_mesh_actor(sphere, color="red")

cube = Cube(x_length=1.0, y_length=1.0, z_length=1.0)
renderer.add_mesh_actor(cube, color="blue")

cylinder = Cylinder(center=(2, 0, 0), radius=0.5, height=1.5)
renderer.add_mesh_actor(cylinder, color="green")

# Generate config
config = renderer.generate_config_object()
print(f"Configuration has {len(config['actors'])} actors")

# %% [markdown]
# ## Camera and Lighting Example

# %%
from pyvista_js.camera import Camera
from pyvista_js.light import Light

renderer = get_renderer(lighting=None)  # No default lighting
sphere = Sphere()
renderer.add_mesh_actor(sphere, color="white")

# Add custom camera
camera = Camera()
camera.position = (3.0, 3.0, 3.0)
camera.focal_point = (0.0, 0.0, 0.0)
camera.view_up = (0.0, 1.0, 0.0)
renderer.camera = camera

# Add custom lights
light1 = Light(position=(2, 2, 2), intensity=0.8)
renderer.add_light(light1)

light2 = Light(position=(-2, -2, 2), intensity=0.5, color=(0.5, 0.5, 1.0))
renderer.add_light(light2)

# Generate config
config = renderer.generate_config_object()
print("Camera position:", config["camera"]["position"])
print("Number of lights:", len(config["lights"]))

# %% [markdown]
# ## PBR (Physically Based Rendering) Example

# %%
renderer = get_renderer()
sphere = Sphere()
renderer.add_mesh_actor(
    sphere, color=(0.8, 0.6, 0.2), pbr=True, metallic=0.9, roughness=0.1
)

config = renderer.generate_config_object()
actor_config = config["actors"][0]
print("PBR enabled:", actor_config.get("pbr"))
print("Metallic:", actor_config.get("metallic"))
print("Roughness:", actor_config.get("roughness"))

# %% [markdown]
# ## Wireframe and Edge Display

# %%
renderer = get_renderer()
sphere = Sphere()
renderer.add_mesh_actor(sphere, color="cyan", style="wireframe", show_edges=True)

config = renderer.generate_config_object()
actor_config = config["actors"][0]
print("Style:", actor_config.get("style"))
print("Show edges:", actor_config.get("showEdges"))
