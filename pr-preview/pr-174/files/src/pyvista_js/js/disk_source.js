// Create disc (annular ring) geometry manually
const nRings{{INDEX}} = {{R_RES}} + 1;
const nCirc{{INDEX}} = {{C_RES}};
const inner{{INDEX}} = {{INNER}};
const outer{{INDEX}} = {{OUTER}};

const rawPts{{INDEX}} = [];
for (let r = 0; r < nRings{{INDEX}}; r++) {
  const radius = inner{{INDEX}} + (outer{{INDEX}} - inner{{INDEX}}) * r / (nRings{{INDEX}} - 1);
  for (let c = 0; c < nCirc{{INDEX}}; c++) {
    const angle = (2 * Math.PI * c) / nCirc{{INDEX}};
    rawPts{{INDEX}}.push(radius * Math.cos(angle), radius * Math.sin(angle), 0.0);
  }
}

const rawPolys{{INDEX}} = [];
for (let r = 0; r < nRings{{INDEX}} - 1; r++) {
  for (let c = 0; c < nCirc{{INDEX}}; c++) {
    const c1 = (c + 1) % nCirc{{INDEX}};
    const i00 = r * nCirc{{INDEX}} + c;
    const i01 = r * nCirc{{INDEX}} + c1;
    const i10 = (r + 1) * nCirc{{INDEX}} + c;
    const i11 = (r + 1) * nCirc{{INDEX}} + c1;
    rawPolys{{INDEX}}.push(3, i00, i01, i11);
    rawPolys{{INDEX}}.push(3, i00, i11, i10);
  }
}

const source{{INDEX}} = vtk.Common.DataModel.vtkPolyData.newInstance();
const vtkPts{{INDEX}} = vtk.Common.Core.vtkPoints.newInstance();
vtkPts{{INDEX}}.setData(Float32Array.from(rawPts{{INDEX}}), 3);
source{{INDEX}}.setPoints(vtkPts{{INDEX}});

const cellArray{{INDEX}} = vtk.Common.Core.vtkCellArray.newInstance();
cellArray{{INDEX}}.setData(Int32Array.from(rawPolys{{INDEX}}));
source{{INDEX}}.setPolys(cellArray{{INDEX}});
