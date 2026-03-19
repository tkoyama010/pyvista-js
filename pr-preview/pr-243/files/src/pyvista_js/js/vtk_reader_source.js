const reader{{ INDEX }} = vtk.IO.Legacy.vtkPolyDataReader.newInstance();
reader{{ INDEX }}.parseAsText({{ VTK_TEXT }}); const source{{ INDEX }} =
reader{{ INDEX }}.getOutputData(0);
