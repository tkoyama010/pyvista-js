const source{{ INDEX }} = vtk.Filters.Sources.vtkLineSource.newInstance({
point1: [{{ POINT_A_X }}, {{ POINT_A_Y }}, {{ POINT_A_Z }}], point2:
[{{ POINT_B_X }}, {{ POINT_B_Y }}, {{ POINT_B_Z }}], resolution:
{{ RESOLUTION }} });
