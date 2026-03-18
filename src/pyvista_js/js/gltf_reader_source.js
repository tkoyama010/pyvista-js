const gltfBytes{{INDEX}} = Uint8Array.from(atob({{GLTF_BASE64}}), c => c.charCodeAt(0));
const gltfBlob{{INDEX}} = new Blob([gltfBytes{{INDEX}}], {type: 'model/gltf+json'});
const gltfUrl{{INDEX}} = URL.createObjectURL(gltfBlob{{INDEX}});
const gltfImporter{{INDEX}} = vtk.IO.Geometry.vtkGLTFImporter.newInstance();
gltfImporter{{INDEX}}.setUrl(gltfUrl{{INDEX}});
gltfImporter{{INDEX}}.loadData().then(function() {
  gltfImporter{{INDEX}}.importActors(renderer);
  URL.revokeObjectURL(gltfUrl{{INDEX}});
  renderer.resetCamera();
  renderWindow.render();
});
