var tubedPD{{ INDEX }};
(function () {
  var tubeFilter{{ INDEX }} = vtk.Filters.General.vtkTubeFilter.newInstance({
    radius: {{ RADIUS }},
    numberOfSides: {{ N_SIDES }},
    capping: {{ CAPPING }}
  });
  var src = source{{ INDEX }};
  if (typeof src.update === 'function') { src.update(); }
  if (typeof src.getOutputPort === 'function') {
    tubeFilter{{ INDEX }}.setInputConnection(src.getOutputPort());
  } else {
    tubeFilter{{ INDEX }}.setInputData(src);
  }
  tubeFilter{{ INDEX }}.update();
  tubedPD{{ INDEX }} = tubeFilter{{ INDEX }}.getOutputData();
})();
