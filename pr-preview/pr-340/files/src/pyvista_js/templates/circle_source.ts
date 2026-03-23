const _points = [];
const _centerVal = [centerX, centerY, centerZ];
for (let i = 0; i < resolutionVal; i++) {
  const angle = (2 * Math.PI * i) / resolutionVal;
  _points.push(
    _centerVal[0] + radiusVal * Math.cos(angle),
    _centerVal[1] + radiusVal * Math.sin(angle),
    _centerVal[2],
  );
}
_points.push(_points[0], _points[1], _points[2]);
const _source = vtk.Common.DataModel.vtkPolyData.newInstance();
const _pts = vtk.Common.Core.vtkPoints.newInstance();
_pts.setData(Float32Array.from(_points), 3);
_source.setPoints(_pts);
const _nPts = resolutionVal + 1;
const _cellArray = new Int32Array(_nPts + 1);
_cellArray[0] = _nPts;
for (let i = 0; i < _nPts; i++) _cellArray[i + 1] = i;
const _lines = vtk.Common.Core.vtkCellArray.newInstance();
_lines.setData(_cellArray);
_source.setLines(_lines);
