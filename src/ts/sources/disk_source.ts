import vtkPolyData from "@kitware/vtk.js/Common/DataModel/PolyData";
import vtkPoints from "@kitware/vtk.js/Common/Core/Points";
import vtkCellArray from "@kitware/vtk.js/Common/Core/CellArray";

export interface DiskSourceParams {
  rRes: number;
  cRes: number;
  innerR: number;
  outerR: number;
}

export function createDiskSource(params: DiskSourceParams): any {
  const nRings = params.rRes + 1;
  const nCirc = params.cRes;
  const deltaR = (params.outerR - params.innerR) / params.rRes;
  const thetaStep = (2 * Math.PI) / nCirc;
  const rawPts: number[] = [];
  for (let c = 0; c < nCirc; c++) {
    const theta = c * thetaStep;
    const cosT = Math.cos(theta);
    const sinT = Math.sin(theta);
    for (let r = 0; r < nRings; r++) {
      const radius = params.innerR + r * deltaR;
      rawPts.push(radius * cosT, radius * sinT, 0.0);
    }
  }
  const rawPolys: number[] = [];
  for (let c = 0; c < nCirc; c++) {
    const nextC = (c + 1) % nCirc;
    for (let r = 0; r < nRings - 1; r++) {
      const p0 = c * nRings + r;
      const p1 = p0 + 1;
      const p2 = nextC * nRings + r + 1;
      const p3 = p2 - 1;
      rawPolys.push(3, p0, p1, p2);
      rawPolys.push(3, p0, p2, p3);
    }
  }
  const source = vtkPolyData.newInstance();
  const vtkPts = vtkPoints.newInstance();
  vtkPts.setData(Float32Array.from(rawPts), 3);
  source.setPoints(vtkPts);
  const cellArray = vtkCellArray.newInstance();
  cellArray.setData(Int32Array.from(rawPolys));
  source.setPolys(cellArray);
  return source;
}
