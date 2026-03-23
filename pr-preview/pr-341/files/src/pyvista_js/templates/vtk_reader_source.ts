const _reader = vtk.IO.Legacy.vtkPolyDataReader.newInstance();
_reader.parseAsText(vtkText);
const _source = _reader.getOutputData(0);
