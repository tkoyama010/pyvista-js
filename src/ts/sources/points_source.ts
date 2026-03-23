import vtkPolyData from "@kitware/vtk.js/Common/DataModel/PolyData";

export function createPointsSource(pointsData: number[]): any {
  const points = new Float32Array(pointsData);
  const polydata = vtkPolyData.newInstance();
  polydata.getPoints().setData(points, 3);
  const numPoints = points.length / 3;
  const verts = new Uint32Array(numPoints + 1);
  verts[0] = numPoints;
  for (let i = 0; i < numPoints; i++) {
    verts[i + 1] = i;
  }
  polydata.getVerts().setData(verts);
  return polydata;
}
