import vtkCubeSource from "@kitware/vtk.js/Filters/Sources/CubeSource";

export interface CubeSourceParams {
  centerX: number;
  centerY: number;
  centerZ: number;
  xLength: number;
  yLength: number;
  zLength: number;
}

export function createCubeSource(params: CubeSourceParams): any {
  return vtkCubeSource.newInstance({
    center: [params.centerX, params.centerY, params.centerZ],
    xLength: params.xLength,
    yLength: params.yLength,
    zLength: params.zLength,
  });
}
