var _result;
(function () {
  var src = _inputSource;
  if (typeof src.update === "function") {
    src.update();
  }
  var pd = typeof src.getOutputData === "function" ? src.getOutputData(0) : src;
  var inPts = pd.getPoints().getData();
  var inPolys = pd.getPolys().getData();
  var newPts = [];
  var newPolys = [];
  var offset = 0;
  var i = 0;
  while (i < inPolys.length) {
    var npts = inPolys[i];
    var ids = [];
    for (var j = 0; j < npts; j++) {
      ids.push(inPolys[i + 1 + j]);
    }
    var cx = 0,
      cy = 0,
      cz = 0;
    for (var k = 0; k < npts; k++) {
      cx += inPts[ids[k] * 3];
      cy += inPts[ids[k] * 3 + 1];
      cz += inPts[ids[k] * 3 + 2];
    }
    cx /= npts;
    cy /= npts;
    cz /= npts;
    newPolys.push(npts);
    for (var j = 0; j < npts; j++) {
      var id = ids[j];
      newPts.push(cx + _shrinkFactor * (inPts[id * 3] - cx));
      newPts.push(cy + _shrinkFactor * (inPts[id * 3 + 1] - cy));
      newPts.push(cz + _shrinkFactor * (inPts[id * 3 + 2] - cz));
      newPolys.push(offset + j);
    }
    offset += npts;
    i += npts + 1;
  }
  var pts = vtk.Common.Core.vtkPoints.newInstance();
  pts.setData(Float32Array.from(newPts), 3);
  _result = vtk.Common.DataModel.vtkPolyData.newInstance();
  _result.setPoints(pts);
  var polys = vtk.Common.Core.vtkCellArray.newInstance();
  polys.setData(Int32Array.from(newPolys));
  _result.setPolys(polys);
})();
