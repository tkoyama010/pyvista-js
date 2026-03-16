const points{{INDEX}} = [];
const resolution{{INDEX}} = {{RESOLUTION}};
const radius{{INDEX}} = {{RADIUS}};
const center{{INDEX}} = [{{CENTER_X}}, {{CENTER_Y}}, {{CENTER_Z}}];
for (let i = 0; i < resolution{{INDEX}}; i++) {
  const angle = (2 * Math.PI * i) / resolution{{INDEX}};
  points{{INDEX}}.push(
    center{{INDEX}}[0] + radius{{INDEX}} * Math.cos(angle),
    center{{INDEX}}[1] + radius{{INDEX}} * Math.sin(angle),
    center{{INDEX}}[2]
  );
}
// Close the loop by repeating the first point
points{{INDEX}}.push(points{{INDEX}}[0], points{{INDEX}}[1], points{{INDEX}}[2]);

const source{{INDEX}} = vtk.Common.DataModel.vtkPolyData.newInstance();
const pts{{INDEX}} = vtk.Common.Core.vtkPoints.newInstance();
pts{{INDEX}}.setData(Float32Array.from(points{{INDEX}}), 3);
source{{INDEX}}.setPoints(pts{{INDEX}});

const nPts{{INDEX}} = resolution{{INDEX}} + 1;
const cellArray{{INDEX}} = new Int32Array(nPts{{INDEX}} + 1);
cellArray{{INDEX}}[0] = nPts{{INDEX}};
for (let i = 0; i < nPts{{INDEX}}; i++) cellArray{{INDEX}}[i + 1] = i;
const lines{{INDEX}} = vtk.Common.Core.vtkCellArray.newInstance();
lines{{INDEX}}.setData(cellArray{{INDEX}});
source{{INDEX}}.setLines(lines{{INDEX}});
