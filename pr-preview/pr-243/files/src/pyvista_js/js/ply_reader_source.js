const plyReader{{ INDEX }} = vtk.IO.PLY.vtkPLYReader.newInstance();
const plyBytes{{ INDEX }} = Uint8Array.from(atob({{ PLY_BASE64 }}), c => c.charCodeAt(0));
plyReader{{ INDEX }}.parseAsArrayBuffer(plyBytes{{ INDEX }}.buffer);
const source{{ INDEX }} = plyReader{{ INDEX }}.getOutputData(0);
