import vtkArrowSource from "@kitware/vtk.js/Filters/Sources/ArrowSource";

export interface ArrowSourceParams {
  tipLength: number;
  tipRadius: number;
  tipResolution: number;
  shaftRadius: number;
  shaftResolution: number;
  dirX: number;
  dirY: number;
  dirZ: number;
}

export function createArrowSource(params: ArrowSourceParams): any {
  const source = vtkArrowSource.newInstance({
    tipLength: params.tipLength,
    tipRadius: params.tipRadius,
    tipResolution: params.tipResolution,
    shaftRadius: params.shaftRadius,
    shaftResolution: params.shaftResolution,
    direction: [params.dirX, params.dirY, params.dirZ],
  });
  return source;
}
