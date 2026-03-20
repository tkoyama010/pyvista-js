const points = [];
const resolutionVal = {{ RESOLUTION }};
const radiusVal = {{ RADIUS }};
const centerVal = [{{ CENTER_X }}, {{ CENTER_Y }}, {{ CENTER_Z }}];
for (let i = 0; i < resolutionVal; i++) {
  const angle = (2 * Math.PI * i) / resolutionVal;
  points.push(
    centerVal[0] + radiusVal * Math.cos(angle),
    centerVal[1] + radiusVal * Math.sin(angle),
    centerVal[2]
  );
}
// Close the loop by repeating the first point
points.push(points[0], points[1], points[2]);

const {{ SOURCE }} = vtk.Common.DataModel.vtkPolyData.newInstance();
const pts = vtk.Common.Core.vtkPoints.newInstance();
pts.setData(Float32Array.from(points), 3);
{{ SOURCE }}.setPoints(pts);

const nPts = resolutionVal + 1;
const cellArray = new Int32Array(nPts + 1);
cellArray[0] = nPts;
for (let i = 0; i < nPts; i++) cellArray[i + 1] = i;
const lines = vtk.Common.Core.vtkCellArray.newInstance();
lines.setData(cellArray);
{{ SOURCE }}.setLines(lines);
