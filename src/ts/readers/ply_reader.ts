import vtkPLYReader from "@kitware/vtk.js/IO/Geometry/PLYReader";

export interface PlyReaderResult {
  reader: any;
  source: any;
}

export function createPlyReader(base64Data: string): PlyReaderResult {
  const reader = vtkPLYReader.newInstance();
  const bytes = Uint8Array.from(atob(base64Data), (c) => c.charCodeAt(0));
  reader.parseAsArrayBuffer(bytes.buffer);
  const source = reader.getOutputData(0);
  return { reader, source };
}
