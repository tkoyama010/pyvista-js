import vtkSphereSource from "@kitware/vtk.js/Filters/Sources/SphereSource";
import vtkTextureMapToSphere from "@kitware/vtk.js/Filters/Texture/TextureMapToSphere";

export interface SphereSourceParams {
  centerX: number;
  centerY: number;
  centerZ: number;
  radius: number;
  thetaResolution: number;
  phiResolution: number;
}

export interface SphereSourceResult {
  source: any;
  texMapSphere: any;
}

export function createSphereSource(params: SphereSourceParams): SphereSourceResult {
  const source = vtkSphereSource.newInstance({
    center: [params.centerX, params.centerY, params.centerZ],
    radius: params.radius,
    thetaResolution: params.thetaResolution,
    phiResolution: params.phiResolution,
  });
  const texMapSphere = vtkTextureMapToSphere.newInstance();
  texMapSphere.setInputConnection(source.getOutputPort());
  return { source, texMapSphere };
}
