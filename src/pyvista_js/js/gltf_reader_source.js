const gltfImporter{{INDEX}} = vtk.IO.Geometry.GLTFImporter.newInstance();
const gltfBytes{{INDEX}} = Uint8Array.from(atob({{GLTF_BASE64}}), c => c.charCodeAt(0));
gltfImporter{{INDEX}}.parseAsArrayBuffer(gltfBytes{{INDEX}}.buffer);
const source{{INDEX}} = gltfImporter{{INDEX}}.getOutputData(0);
