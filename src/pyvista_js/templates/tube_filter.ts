var _result;
(function () {
  var tubeFilter = vtk.Filters.General.vtkTubeFilter.newInstance({
    radius: _radius,
    numberOfSides: _nSides,
    capping: _capping,
  });
  var src = _inputSource;
  if (typeof src.update === "function") {
    src.update();
  }
  if (typeof src.getOutputPort === "function") {
    tubeFilter.setInputConnection(src.getOutputPort());
  } else {
    tubeFilter.setInputData(src);
  }
  tubeFilter.update();
  _result = tubeFilter.getOutputData();
})();
