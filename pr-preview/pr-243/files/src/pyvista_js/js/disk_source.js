// Create disc geometry matching vtk.js vtkDiskSource ordering:
// outer loop circumferential (c), inner loop radial (r)
// point index = c * nRings + r
const nRings{{INDEX}} = {{R_RES}} + 1;
const nCirc{{INDEX}} = {{C_RES}};
const inner{{INDEX}} = {{INNER}};
const outer{{INDEX}} = {{OUTER}};
const deltaR{{INDEX}} = (outer{{INDEX}} - inner{{INDEX}}) / {{R_RES}};
const thetaStep{{INDEX}} = (2 * Math.PI) / nCirc{{INDEX}};

const rawPts{{INDEX}} = [];
for (let c = 0; c < nCirc{{INDEX}}; c++) {
  const theta = c * thetaStep{{INDEX}};
  const cosT = Math.cos(theta);
  const sinT = Math.sin(theta);
  for (let r = 0; r < nRings{{INDEX}}; r++) {
    const radius = inner{{INDEX}} + r * deltaR{{INDEX}};
    rawPts{{INDEX}}.push(radius * cosT, radius * sinT, 0.0);
  }
}

const rawPolys{{INDEX}} = [];
for (let c = 0; c < nCirc{{INDEX}}; c++) {
  const nextC = (c + 1) % nCirc{{INDEX}};
  for (let r = 0; r < nRings{{INDEX}} - 1; r++) {
    const p0 = c * nRings{{INDEX}} + r;
    const p1 = p0 + 1;
    const p2 = nextC * nRings{{INDEX}} + r + 1;
    const p3 = p2 - 1;
    rawPolys{{INDEX}}.push(3, p0, p1, p2);
    rawPolys{{INDEX}}.push(3, p0, p2, p3);
  }
}

const source{{INDEX}} = vtk.Common.DataModel.vtkPolyData.newInstance();
const vtkPts{{INDEX}} = vtk.Common.Core.vtkPoints.newInstance();
vtkPts{{INDEX}}.setData(Float32Array.from(rawPts{{INDEX}}), 3);
source{{INDEX}}.setPoints(vtkPts{{INDEX}});

const cellArray{{INDEX}} = vtk.Common.Core.vtkCellArray.newInstance();
cellArray{{INDEX}}.setData(Int32Array.from(rawPolys{{INDEX}}));
source{{INDEX}}.setPolys(cellArray{{INDEX}});
