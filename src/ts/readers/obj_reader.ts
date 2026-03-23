import vtkOBJReader from "@kitware/vtk.js/IO/Misc/OBJReader";

export interface ObjReaderResult {
  reader: any;
  source: any;
}

export function createObjReader(base64Data: string): ObjReaderResult {
  const reader = vtkOBJReader.newInstance();
  const bytes = Uint8Array.from(atob(base64Data), (c) => c.charCodeAt(0));
  const text = new TextDecoder().decode(bytes);
  reader.parseAsText(text);
  const source = reader.getOutputData(0);
  return { reader, source };
}
