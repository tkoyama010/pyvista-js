import vtkSTLReader from "@kitware/vtk.js/IO/Geometry/STLReader";

export interface StlReaderResult {
  reader: any;
  source: any;
}

export function createStlReader(base64Data: string): StlReaderResult {
  const reader = vtkSTLReader.newInstance();
  const bytes = Uint8Array.from(atob(base64Data), (c) => c.charCodeAt(0));
  reader.parseAsArrayBuffer(bytes.buffer);
  const source = reader.getOutputData(0);
  return { reader, source };
}
