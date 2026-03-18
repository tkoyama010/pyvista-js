var contourPD{{INDEX}};
(function () {
  var src = source{{INDEX}};
  if (typeof src.update === 'function') { src.update(); }
  var pd = (typeof src.getOutputData === 'function') ? src.getOutputData(0) : src;

  // Create contour filter
  var contourFilter = vtk.Filters.General.vtkContourFilter.newInstance();
  contourFilter.setInputData(pd);

  // Set contour values
  var values = [{{CONTOUR_VALUES}}];
  contourFilter.setComputeNormals(true);
  contourFilter.setComputeGradients(false);
  contourFilter.setComputeScalars(true);
  contourFilter.setNumberOfContours(values.length);
  for (var i = 0; i < values.length; i++) {
    contourFilter.setValue(i, values[i]);
  }

  // Execute filter
  contourFilter.update();
  contourPD{{INDEX}} = contourFilter.getOutputData();
})();
