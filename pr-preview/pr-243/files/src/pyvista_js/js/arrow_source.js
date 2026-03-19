const source{{ INDEX }} = vtk.Filters.Sources.vtkArrowSource.newInstance({
tipLength: {{ TIP_LENGTH }}, tipRadius: {{ TIP_RADIUS }}, tipResolution:
{{ TIP_RESOLUTION }}, shaftRadius: {{ SHAFT_RADIUS }}, shaftResolution:
{{ SHAFT_RESOLUTION }}, direction: [{{ DIR_X }}, {{ DIR_Y }}, {{ DIR_Z }}],
startAt: 'origin' });
