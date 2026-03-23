/**
 * Creates a sphere source with texture mapping
 * @param config - Configuration object injected by Jinja2
 * @returns Object containing sphere source and texture mapper
 */
function createSphere(config) {
  const source = vtk.Filters.Sources.vtkSphereSource.newInstance({
    center: [config.centerX, config.centerY, config.centerZ],
    radius: config.radius,
    thetaResolution: config.thetaResolution,
    phiResolution: config.phiResolution,
  });
  const texMapSphere = vtk.Filters.Texture.vtkTextureMapToSphere.newInstance();
  texMapSphere.setInputConnection(source.getOutputPort());
  return { source, texMapSphere };
}

// Call the function with the injected CONFIG
const { source: _source, texMapSphere: _texMapSphere } = createSphere(CONFIG);
