// Create disc geometry matching vtk.js vtkDiskSource ordering:
// outer loop circumferential (c), inner loop radial (r)
// point index = c * nRings + r
const nRings = {{ R_RES }} + 1;
const nCirc = {{ C_RES }};
const innerR = {{ INNER }};
const outerR = {{ OUTER }};
const deltaR = (outerR - innerR) / {{ R_RES }};
const thetaStep = (2 * Math.PI) / nCirc;

const rawPts = [];
for (let c = 0; c < nCirc; c++) {
  const theta = c * thetaStep;
  const cosT = Math.cos(theta);
  const sinT = Math.sin(theta);
  for (let r = 0; r < nRings; r++) {
    const radius = innerR + r * deltaR;
    rawPts.push(radius * cosT, radius * sinT, 0.0);
  }
}

const rawPolys = [];
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

const {{ SOURCE }} = vtk.Common.DataModel.vtkPolyData.newInstance();
const vtkPts = vtk.Common.Core.vtkPoints.newInstance();
vtkPts.setData(Float32Array.from(rawPts), 3);
{{ SOURCE }}.setPoints(vtkPts);

const cellArray = vtk.Common.Core.vtkCellArray.newInstance();
cellArray.setData(Int32Array.from(rawPolys));
{{ SOURCE }}.setPolys(cellArray);
