import vtkPolyData from "@kitware/vtk.js/Common/DataModel/PolyData";

export function createMeshSource(pointsData: number[]): any {
  const points = new Float32Array(pointsData);
  const polydata = vtkPolyData.newInstance();
  polydata.getPoints().setData(points, 3);
  return polydata;
}
