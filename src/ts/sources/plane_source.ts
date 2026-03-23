import vtkPlaneSource from "@kitware/vtk.js/Filters/Sources/PlaneSource";

export interface PlaneSourceParams {
  originX: number;
  originY: number;
  originZ: number;
  point1X: number;
  point1Y: number;
  point1Z: number;
  point2X: number;
  point2Y: number;
  point2Z: number;
  iResolution: number;
  jResolution: number;
}

export function createPlaneSource(params: PlaneSourceParams): any {
  return vtkPlaneSource.newInstance({
    origin: [params.originX, params.originY, params.originZ],
    point1: [params.point1X, params.point1Y, params.point1Z],
    point2: [params.point2X, params.point2Y, params.point2Z],
    xResolution: params.iResolution,
    yResolution: params.jResolution,
  });
}
