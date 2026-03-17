const points{{INDEX}} = new Float32Array([{{POINTS_DATA}}]);
const polydata{{INDEX}} = vtk.Common.DataModel.vtkPolyData.newInstance();
polydata{{INDEX}}.getPoints().setData(points{{INDEX}}, 3);

// Create verts array for point cloud rendering
const numPoints{{INDEX}} = points{{INDEX}}.length / 3;
const verts{{INDEX}} = new Uint32Array(numPoints{{INDEX}} + 1);
verts{{INDEX}}[0] = numPoints{{INDEX}};
for (let i = 0; i < numPoints{{INDEX}}; i++) {
  verts{{INDEX}}[i + 1] = i;
}
polydata{{INDEX}}.getVerts().setData(verts{{INDEX}});

const source{{INDEX}} = polydata{{INDEX}};
