import vtkPolyData from "@kitware/vtk.js/Common/DataModel/PolyData";
import vtkPoints from "@kitware/vtk.js/Common/Core/Points";
import vtkCellArray from "@kitware/vtk.js/Common/Core/CellArray";

export interface CircleSourceParams {
  resolution: number;
  radius: number;
  centerX: number;
  centerY: number;
  centerZ: number;
}

export function createCircleSource(params: CircleSourceParams): any {
  const points: number[] = [];
  for (let i = 0; i < params.resolution; i++) {
    const angle = (2 * Math.PI * i) / params.resolution;
    points.push(
      params.centerX + params.radius * Math.cos(angle),
      params.centerY + params.radius * Math.sin(angle),
      params.centerZ,
    );
  }
  points.push(points[0], points[1], points[2]);

  const source = vtkPolyData.newInstance();
  const pts = vtkPoints.newInstance();
  pts.setData(Float32Array.from(points), 3);
  source.setPoints(pts);

  const nPts = params.resolution + 1;
  const cellArray = new Int32Array(nPts + 1);
  cellArray[0] = nPts;
  for (let i = 0; i < nPts; i++) cellArray[i + 1] = i;
  const lines = vtkCellArray.newInstance();
  lines.setData(cellArray);
  source.setLines(lines);
  return source;
}
