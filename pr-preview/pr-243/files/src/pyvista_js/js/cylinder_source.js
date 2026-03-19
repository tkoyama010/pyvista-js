const source{{INDEX}} = vtk.Filters.Sources.vtkCylinderSource.newInstance({
  center: [{{CENTER_X}}, {{CENTER_Y}}, {{CENTER_Z}}],
  radius: {{RADIUS}},
  height: {{HEIGHT}},
  resolution: {{RESOLUTION}},
  generateTCoords: true
});
