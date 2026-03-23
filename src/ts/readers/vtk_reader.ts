// @ts-ignore - PolyDataReader lacks type definitions
import vtkPolyDataReader from "@kitware/vtk.js/IO/Legacy/PolyDataReader";

export interface VtkReaderResult {
  reader: any;
  source: any;
}

export function createVtkReader(vtkText: string): VtkReaderResult {
  const reader = vtkPolyDataReader.newInstance();
  reader.parseAsText(vtkText);
  const source = reader.getOutputData(0);
  return { reader, source };
}
