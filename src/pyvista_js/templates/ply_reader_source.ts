const _reader = vtk.IO.Geometry.vtkPLYReader.newInstance();
const _bytes = Uint8Array.from(atob(base64Data), (c) => c.charCodeAt(0));
_reader.parseAsArrayBuffer(_bytes.buffer);
const _source = _reader.getOutputData(0);
