import vtkConeSource from "@kitware/vtk.js/Filters/Sources/ConeSource";

export interface ConeSourceParams {
  centerX: number;
  centerY: number;
  centerZ: number;
  directionX: number;
  directionY: number;
  directionZ: number;
  height: number;
  radius: number;
  resolution: number;
  capping: boolean;
}

export function createConeSource(params: ConeSourceParams): any {
  return vtkConeSource.newInstance({
    center: [params.centerX, params.centerY, params.centerZ],
    direction: [params.directionX, params.directionY, params.directionZ],
    height: params.height,
    radius: params.radius,
    resolution: params.resolution,
    capping: params.capping,
  });
}
