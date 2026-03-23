const _source = vtk.Filters.Sources.vtkCylinderSource.newInstance({
  center: [centerX, centerY, centerZ],
  radius,
  height,
  resolution,
  generateTCoords: true,
});
