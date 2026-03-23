var _result;
(function () {
  var src = _inputSource;
  if (typeof src.update === "function") {
    src.update();
  }
  var pd = typeof src.getOutputData === "function" ? src.getOutputData(0) : src;
  var inPts = pd.getPoints().getData();
  var inPolys = pd.getPolys().getData();
  var nPts = inPts.length / 3;
  var distances = new Float32Array(nPts);
  for (var i = 0; i < nPts; i++) {
    var px = inPts[i * 3];
    var py = inPts[i * 3 + 1];
    var pz = inPts[i * 3 + 2];
    distances[i] =
      _normalX * (px - _originX) +
      _normalY * (py - _originY) +
      _normalZ * (pz - _originZ);
  }
  var newPts = [];
  var newPolys = [];
  var ptMap = {};
  var newPtIdx = 0;
  var i = 0;
  while (i < inPolys.length) {
    var npts = inPolys[i];
    var ids = [];
    for (var j = 0; j < npts; j++) {
      ids.push(inPolys[i + 1 + j]);
    }
    var allKept = true;
    for (var k = 0; k < npts; k++) {
      var dist = distances[ids[k]];
      var keep = _invert ? dist >= 0 : dist <= 0;
      if (!keep) {
        allKept = false;
        break;
      }
    }
    if (allKept) {
      newPolys.push(npts);
      for (var j = 0; j < npts; j++) {
        var oldId = ids[j];
        if (!(oldId in ptMap)) {
          newPts.push(inPts[oldId * 3]);
          newPts.push(inPts[oldId * 3 + 1]);
          newPts.push(inPts[oldId * 3 + 2]);
          ptMap[oldId] = newPtIdx++;
        }
        newPolys.push(ptMap[oldId]);
      }
    }
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
