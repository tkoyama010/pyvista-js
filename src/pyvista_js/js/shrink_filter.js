const shrinkFilter{{INDEX}} = vtk.Filters.General.vtkShrinkFilter.newInstance({
  shrinkFactor: {{SHRINK_FACTOR}}
});
shrinkFilter{{INDEX}}.setInputConnection(source{{INDEX}}.getOutputPort());
