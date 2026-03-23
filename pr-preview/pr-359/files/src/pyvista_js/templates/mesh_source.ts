const _points = new Float32Array(pointsData);
const _polydata = vtk.Common.DataModel.vtkPolyData.newInstance();
_polydata.getPoints().setData(_points, 3);
const _source = _polydata;
