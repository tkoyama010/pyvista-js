const _source = vtk.Filters.Sources.vtkArrowSource.newInstance({
  tipLength,
  tipRadius,
  tipResolution,
  shaftRadius,
  shaftResolution,
  direction: [dirX, dirY, dirZ],
  startAt: "origin",
});
