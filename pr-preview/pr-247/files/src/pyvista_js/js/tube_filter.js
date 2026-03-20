var {{ TUBED_PD }};
(function () {
  var {{ TUBE_FILTER }} = vtk.Filters.General.vtkTubeFilter.newInstance({
    radius: {{ RADIUS }},
    numberOfSides: {{ N_SIDES }},
    capping: {{ CAPPING }}
  });
  var src = {{ SOURCE }};
  if (typeof src.update === 'function') { src.update(); }
  if (typeof src.getOutputPort === 'function') {
    {{ TUBE_FILTER }}.setInputConnection(src.getOutputPort());
  } else {
    {{ TUBE_FILTER }}.setInputData(src);
  }
  {{ TUBE_FILTER }}.update();
  {{ TUBED_PD }} = {{ TUBE_FILTER }}.getOutputData();
})();
