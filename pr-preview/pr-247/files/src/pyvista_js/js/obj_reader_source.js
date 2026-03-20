const {{ OBJ_READER }} = vtk.IO.Misc.vtkOBJReader.newInstance();
const objBytes = Uint8Array.from(atob({{ OBJ_BASE64 }}), c => c.charCodeAt(0));
{{ OBJ_READER }}.parseAsArrayBuffer(objBytes.buffer);
const {{ SOURCE }} = {{ OBJ_READER }}.getOutputData(0);
