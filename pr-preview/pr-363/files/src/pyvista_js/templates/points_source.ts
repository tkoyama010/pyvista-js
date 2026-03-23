const _points = new Float32Array(pointsData);
const _polydata = vtk.Common.DataModel.vtkPolyData.newInstance();
_polydata.getPoints().setData(_points, 3);
const _numPoints = _points.length / 3;
const _verts = new Uint32Array(_numPoints + 1);
_verts[0] = _numPoints;
for (let i = 0; i < _numPoints; i++) {
  _verts[i + 1] = i;
}
_polydata.getVerts().setData(_verts);
const _source = _polydata;
