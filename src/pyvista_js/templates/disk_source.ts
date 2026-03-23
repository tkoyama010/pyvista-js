const _nRings = rRes + 1;
const _nCirc = cRes;
const _deltaR = (outerR - innerR) / rRes;
const _thetaStep = (2 * Math.PI) / _nCirc;
const _rawPts = [];
for (let c = 0; c < _nCirc; c++) {
  const theta = c * _thetaStep;
  const cosT = Math.cos(theta);
  const sinT = Math.sin(theta);
  for (let r = 0; r < _nRings; r++) {
    const radius = innerR + r * _deltaR;
    _rawPts.push(radius * cosT, radius * sinT, 0.0);
  }
}
const _rawPolys = [];
for (let c = 0; c < _nCirc; c++) {
  const nextC = (c + 1) % _nCirc;
  for (let r = 0; r < _nRings - 1; r++) {
    const p0 = c * _nRings + r;
    const p1 = p0 + 1;
    const p2 = nextC * _nRings + r + 1;
    const p3 = p2 - 1;
    _rawPolys.push(3, p0, p1, p2);
    _rawPolys.push(3, p0, p2, p3);
  }
}
const _source = vtk.Common.DataModel.vtkPolyData.newInstance();
const _vtkPts = vtk.Common.Core.vtkPoints.newInstance();
_vtkPts.setData(Float32Array.from(_rawPts), 3);
_source.setPoints(_vtkPts);
const _cellArray = vtk.Common.Core.vtkCellArray.newInstance();
_cellArray.setData(Int32Array.from(_rawPolys));
_source.setPolys(_cellArray);
