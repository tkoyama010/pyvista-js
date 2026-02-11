const points{{INDEX}} = new Float32Array([{{POINTS_DATA}}]);
      const polydata{{INDEX}} = vtk.Common.DataModel.vtkPolyData.newInstance();
      polydata{{INDEX}}.getPoints().setData(points{{INDEX}}, 3);
      const source{{INDEX}} = polydata{{INDEX}};
