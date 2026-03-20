const {{ SOURCE }} = vtk.Filters.Sources.vtkCubeSource.newInstance({ center:
[{{ CENTER_X }}, {{ CENTER_Y }}, {{ CENTER_Z }}], xLength: {{ X_LENGTH }},
yLength: {{ Y_LENGTH }}, zLength: {{ Z_LENGTH }} });
