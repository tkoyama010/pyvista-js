const source{{INDEX}} = vtk.Filters.Sources.vtkDiskSource.newInstance({
  innerRadius: {{INNER}},
  outerRadius: {{OUTER}},
  radialResolution: {{R_RES}},
  circumferentialResolution: {{C_RES}}
});
