const _source = vtk.Filters.Sources.vtkCubeSource.newInstance({
  center: [centerX, centerY, centerZ],
  xLength,
  yLength,
  zLength,
});
