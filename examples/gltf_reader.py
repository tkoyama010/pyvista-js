"""glTF rendering example: GLTFReader and download_damaged_helmet."""

import pyvista_js as pv
from pyvista_js import examples
from pyvista_js.examples import _GLTF_SAMPLE_BASE, _CACHE_DIR, _download_url

# Download the damaged helmet glTF file
_URL = f"{_GLTF_SAMPLE_BASE}/DamagedHelmet/glTF-Embedded/DamagedHelmet.gltf"
gltf_path = _download_url(_URL, "DamagedHelmet.gltf")

# --- Using GLTFReader directly ---
reader = pv.GLTFReader(gltf_path)
mesh = reader.read()
print(f"GLTFReader: mesh has {mesh.n_points} points")

plotter = pv.Plotter()
plotter.add_mesh(mesh, pbr=True, metallic=0.5, roughness=0.3)
plotter.view_isometric()
plotter.show()

# --- Using examples.download_damaged_helmet() ---
mesh2 = examples.download_damaged_helmet()
print(f"download_damaged_helmet: mesh has {mesh2.n_points} points")

cubemap = examples.download_sky_box_cube_map()

plotter2 = pv.Plotter()
plotter2.set_environment_texture(cubemap)
plotter2.add_mesh(mesh2, pbr=True, metallic=0.5, roughness=0.3)
plotter2.view_isometric()
plotter2.show()
