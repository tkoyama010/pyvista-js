const {{ VTK_READER }} = vtk.IO.Legacy.vtkPolyDataReader.newInstance();
{{ VTK_READER }}.parseAsText({{ VTK_TEXT }});
const {{ SOURCE }} = {{ VTK_READER }}.getOutputData(0);
