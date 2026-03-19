const stlReader{{ INDEX }} = vtk.IO.Geometry.vtkSTLReader.newInstance(); const
stlBytes{{ INDEX }} = Uint8Array.from(atob({{ STL_BASE64 }}), c =>
c.charCodeAt(0));
stlReader{{ INDEX }}.parseAsArrayBuffer(stlBytes{{ INDEX }}.buffer); const
source{{ INDEX }} = stlReader{{ INDEX }}.getOutputData(0);
