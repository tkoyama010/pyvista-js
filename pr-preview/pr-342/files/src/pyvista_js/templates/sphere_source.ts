const _source = vtk.Filters.Sources.vtkSphereSource.newInstance({
  center: [centerX, centerY, centerZ],
  radius,
  thetaResolution,
  phiResolution,
});
const _texMapSphere = vtk.Filters.Texture.vtkTextureMapToSphere.newInstance();
_texMapSphere.setInputConnection(_source.getOutputPort());
