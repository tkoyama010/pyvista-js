const _source = vtk.Filters.Sources.vtkConeSource.newInstance({
  center: [centerX, centerY, centerZ],
  direction: [directionX, directionY, directionZ],
  height,
  radius,
  resolution,
  capping,
  generateTCoords: true,
});
