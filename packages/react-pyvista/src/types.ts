export interface LightConfig {
  type: string
  position: [number, number, number]
  focalPoint: [number, number, number]
  color: [number, number, number]
  intensity: number
  positional: boolean
  coneAngle: number
  coneFalloff: number
  attenuationValues: [number, number, number]
}

export interface NormalsConfig {
  computePointNormals: boolean
  computeCellNormals: boolean
}

export interface PointDataArray {
  numberOfComponents: number
  values: number[]
  name: string
}

export interface FilterConfig {
  type: string
  shrinkFactor?: number
  radius?: number
  numberOfSides?: number
  normal?: [number, number, number]
  origin?: [number, number, number]
  invert?: boolean
  values?: number[]
  scalarName?: string
  scalarData?: number[]
  holeSize?: number
}

export interface SourceConfig {
  type: string
  center?: [number, number, number]
  radius?: number
  thetaResolution?: number
  phiResolution?: number
  height?: number
  resolution?: number
  xLength?: number
  yLength?: number
  zLength?: number
  innerRadius?: number
  outerRadius?: number
  tipLength?: number
  tipRadius?: number
  shaftRadius?: number
  point1?: [number, number, number]
  point2?: [number, number, number]
  origin?: [number, number, number]
  normal?: [number, number, number]
  points?: number[]
  polys?: number[]
  data?: string
  pointData?: PointDataArray[]
  tCoords?: number[]
  filters?: FilterConfig[]
}

export interface EdgesConfig {
  color: [number, number, number]
}

export interface PbrConfig {
  metallic: number
  roughness: number
}

export interface TextureConfig {
  url: string
}

export interface ActorConfig {
  source: SourceConfig
  color: [number, number, number]
  opacity: number
  style: string
  shading?: string
  edges?: EdgesConfig
  pbr?: PbrConfig
  normals?: NormalsConfig
  actorType?: string
  renderPointsAsSpheres?: boolean
  pointSize?: number
  texture?: TextureConfig
}

export interface CameraConfig {
  position?: [number, number, number]
  focalPoint?: [number, number, number]
  viewUp?: [number, number, number]
  viewAngle?: number
  clippingRange?: [number, number]
  parallelProjection?: boolean
  viewVector?: [number, number, number]
}

export interface TextActorConfig {
  text: string
  position: [number, number]
  color: [number, number, number]
  opacity: number
  fontSize: number
  bold: boolean
  italic: boolean
}

export interface SceneData {
  containerId: string
  background: [number, number, number]
  lightingMode: string | undefined
  lights: LightConfig[]
  actors: ActorConfig[]
  textActors?: TextActorConfig[]
  axes: boolean
  camera?: CameraConfig
}
