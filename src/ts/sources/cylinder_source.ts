import vtkCylinderSource from "@kitware/vtk.js/Filters/Sources/CylinderSource";

export interface CylinderSourceParams {
  centerX: number;
  centerY: number;
  centerZ: number;
  radius: number;
  height: number;
  resolution: number;
}

export function createCylinderSource(params: CylinderSourceParams): any {
  return vtkCylinderSource.newInstance({
    center: [params.centerX, params.centerY, params.centerZ],
    radius: params.radius,
    height: params.height,
    resolution: params.resolution,
  });
}
