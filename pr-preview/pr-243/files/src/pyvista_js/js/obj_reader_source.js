const objReader{{ INDEX }} = vtk.IO.Misc.vtkOBJReader.newInstance(); const
objBytes{{ INDEX }} = Uint8Array.from(atob({{ OBJ_BASE64 }}), c =>
c.charCodeAt(0));
objReader{{ INDEX }}.parseAsArrayBuffer(objBytes{{ INDEX }}.buffer); const
source{{ INDEX }} = objReader{{ INDEX }}.getOutputData(0);
