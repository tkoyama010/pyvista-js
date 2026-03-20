const {{ SOURCE }} = vtk.Filters.Sources.vtkConeSource.newInstance({
  center: [{{ CENTER_X }}, {{ CENTER_Y }}, {{ CENTER_Z }}],
  direction: [{{ DIRECTION_X }}, {{ DIRECTION_Y }}, {{ DIRECTION_Z }}],
  height: {{ HEIGHT }},
  radius: {{ RADIUS }},
  resolution: {{ RESOLUTION }},
  capping: {{ CAPPING }},
  generateTCoords: true
});
