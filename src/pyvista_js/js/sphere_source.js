const source{{INDEX}} = vtk.Filters.Sources.vtkSphereSource.newInstance({
  center: [{{CENTER_X}}, {{CENTER_Y}}, {{CENTER_Z}}],
  radius: {{RADIUS}},
  thetaResolution: {{THETA_RESOLUTION}},
  phiResolution: {{PHI_RESOLUTION}}
});
const texMapSphere{{INDEX}} = vtk.Filters.Texture.vtkTextureMapToSphere.newInstance();
texMapSphere{{INDEX}}.setInputConnection(source{{INDEX}}.getOutputPort());
