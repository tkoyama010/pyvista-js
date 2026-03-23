const _source = vtk.Filters.Sources.vtkPlaneSource.newInstance({
  origin: [originX, originY, originZ],
  point1: [point1X, point1Y, point1Z],
  point2: [point2X, point2Y, point2Z],
  xResolution: iResolution,
  yResolution: jResolution,
});
