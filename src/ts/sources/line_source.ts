import vtkLineSource from "@kitware/vtk.js/Filters/Sources/LineSource";

export interface LineSourceParams {
  pointAX: number;
  pointAY: number;
  pointAZ: number;
  pointBX: number;
  pointBY: number;
  pointBZ: number;
  resolution: number;
}

export function createLineSource(params: LineSourceParams): any {
  return vtkLineSource.newInstance({
    point1: [params.pointAX, params.pointAY, params.pointAZ],
    point2: [params.pointBX, params.pointBY, params.pointBZ],
    resolution: params.resolution,
  });
}
