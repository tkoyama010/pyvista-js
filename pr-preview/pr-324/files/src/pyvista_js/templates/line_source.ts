const _source = vtk.Filters.Sources.vtkLineSource.newInstance({
  point1: [pointAX, pointAY, pointAZ],
  point2: [pointBX, pointBY, pointBZ],
  resolution,
});
