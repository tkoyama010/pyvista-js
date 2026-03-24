/**
 * Type declarations for the vtk.js CDN global object.
 * Only the APIs actually used by pyvista-renderer.ts are declared here.
 */

// eslint-disable-next-line @typescript-eslint/no-empty-interface
interface VtkInstance {
  // Generic vtk.js instance — specific methods added per class below
}

interface VtkNewInstanceFactory<T = VtkInstance> {
  newInstance(options?: Record<string, unknown>): T;
}

// --- Common types ---

interface VtkDataArray extends VtkInstance {
  getData(): Float32Array;
}

interface VtkDataArrayFactory {
  newInstance(options: {
    numberOfComponents: number;
    values: Float32Array;
    name: string;
  }): VtkDataArray;
}

interface VtkPointData {
  addArray(arr: VtkDataArray): void;
  setTCoords(arr: VtkDataArray): void;
  setActiveScalars(name: string): void;
  getArrayByName(name: string): VtkDataArray | null;
}

interface VtkPoints extends VtkInstance {
  setData(data: Float32Array, numberOfComponents: number): void;
}

interface VtkCellArray extends VtkInstance {
  setData(data: Uint32Array): void;
  getData(): Uint32Array;
}

interface VtkPolyData extends VtkInstance {
  getPoints(): VtkPoints & { getData(): Float32Array; setData(data: Float32Array, n: number): void };
  setPoints(points: VtkPoints): void;
  getPolys(): VtkCellArray;
  getLines(): VtkCellArray;
  getPointData(): VtkPointData;
}

interface VtkPlane extends VtkInstance {
  setOrigin(x: number, y: number, z: number): void;
  setNormal(x: number, y: number, z: number): void;
}

// --- Filter/Source with output port ---

interface VtkAlgorithm extends VtkInstance {
  getOutputPort(): VtkOutputPort;
  getOutputData(): VtkPolyData;
  update(): void;
  setInputConnection(port: VtkOutputPort): void;
  setInputData(data: VtkPolyData): void;
}

interface VtkOutputPort {
  // Opaque handle
}

// --- Rendering ---

interface VtkProperty {
  setColor(r: number, g: number, b: number): void;
  setOpacity(opacity: number): void;
  setRepresentation(mode: number): void;
  setRepresentationToPoints(): void;
  setEdgeVisibility(visible: boolean): void;
  setEdgeColor(r: number, g: number, b: number): void;
  setInterpolationToGouraud(): void;
  setInterpolationToFlat(): void;
  setInterpolationToPhong(): void;
  setMetallic(value: number): void;
  setRoughness(value: number): void;
  setAmbient(value: number): void;
  setSpecular(value: number): void;
  setSpecularPower(value: number): void;
  setDiffuse(value: number): void;
  setPointSize(size: number): void;
}

interface VtkActor extends VtkInstance {
  setMapper(mapper: VtkMapper): void;
  getProperty(): VtkProperty;
  addTexture(texture: VtkTexture): void;
}

interface VtkMapper extends VtkInstance {
  setInputConnection(port: VtkOutputPort): void;
  setInputData(data: VtkPolyData): void;
  setRadius?(radius: number): void;
}

interface VtkTexture extends VtkInstance {
  setInterpolate(value: boolean): void;
  setImage(img: HTMLImageElement): void;
}

interface VtkCamera {
  setPosition(x: number, y: number, z: number): void;
  setFocalPoint(x: number, y: number, z: number): void;
  setViewUp(x: number, y: number, z: number): void;
  setViewAngle(angle: number): void;
  setClippingRange(near: number, far: number): void;
  setParallelProjection(value: boolean): void;
}

interface VtkLight extends VtkInstance {
  setPosition(x: number, y: number, z: number): void;
  setFocalPoint(x: number, y: number, z: number): void;
  setColor(r: number, g: number, b: number): void;
  setIntensity(intensity: number): void;
  setPositional(value: boolean): void;
  setConeAngle(angle: number): void;
  setExponent(value: number): void;
  setAttenuationValues(a: number, b: number, c: number): void;
  setLightTypeToSceneLight(): void;
  setLightTypeToCameraLight(): void;
  setLightTypeToHeadLight(): void;
  [key: string]: unknown;
}

interface VtkRenderer extends VtkInstance {
  setBackground(r: number, g: number, b: number): void;
  addActor(actor: VtkActor): void;
  addLight(light: VtkLight): void;
  removeAllLights(): void;
  setAutomaticLightCreation(value: boolean): void;
  resetCamera(): void;
  resetCameraClippingRange(): void;
  getActiveCamera(): VtkCamera;
}

interface VtkRenderWindow extends VtkInstance {
  addRenderer(renderer: VtkRenderer): void;
  addView(view: VtkOpenGLRenderWindow): void;
  render(): void;
}

interface VtkOpenGLRenderWindow extends VtkInstance {
  setContainer(container: HTMLElement): void;
  setSize(width: number, height: number): void;
}

interface VtkInteractor extends VtkInstance {
  setInteractorStyle(style: VtkInstance): void;
  setView(view: VtkOpenGLRenderWindow): void;
  initialize(): void;
  bindEvents(container: HTMLElement): void;
}

interface VtkOrientationMarkerWidget extends VtkInstance {
  setEnabled(value: boolean): void;
  setViewportCorner(corner: number): void;
  setViewportSize(size: number): void;
  setMinPixelSize(size: number): void;
  setMaxPixelSize(size: number): void;
}

interface VtkOrientationMarkerWidgetFactory {
  newInstance(options: { actor: VtkInstance; interactor: VtkInteractor }): VtkOrientationMarkerWidget;
  Corners: { BOTTOM_LEFT: number };
}

// --- Reader interfaces ---

interface VtkReader extends VtkInstance {
  getOutputPort(): VtkOutputPort;
  getOutputData(): VtkPolyData;
  update(): void;
  parseAsArrayBuffer(buffer: ArrayBuffer): void;
  parseAsText(text: string): void;
}

// --- Global vtk namespace ---

interface VtkGlobal {
  Rendering: {
    Core: {
      vtkRenderer: VtkNewInstanceFactory<VtkRenderer>;
      vtkRenderWindow: VtkNewInstanceFactory<VtkRenderWindow>;
      vtkRenderWindowInteractor: VtkNewInstanceFactory<VtkInteractor>;
      vtkLight: VtkNewInstanceFactory<VtkLight>;
      vtkActor: VtkNewInstanceFactory<VtkActor>;
      vtkMapper: VtkNewInstanceFactory<VtkMapper>;
      vtkSphereMapper: VtkNewInstanceFactory<VtkMapper>;
      vtkTexture: VtkNewInstanceFactory<VtkTexture>;
      vtkAxesActor: VtkNewInstanceFactory<VtkInstance>;
    };
    OpenGL: {
      vtkRenderWindow: VtkNewInstanceFactory<VtkOpenGLRenderWindow>;
    };
  };
  Filters: {
    Sources: {
      vtkSphereSource: VtkNewInstanceFactory<VtkAlgorithm>;
      vtkConeSource: VtkNewInstanceFactory<VtkAlgorithm>;
      vtkCubeSource: VtkNewInstanceFactory<VtkAlgorithm>;
      vtkCylinderSource: VtkNewInstanceFactory<VtkAlgorithm>;
      vtkDiskSource?: VtkNewInstanceFactory<VtkAlgorithm>;
      vtkArrowSource: VtkNewInstanceFactory<VtkAlgorithm>;
      vtkLineSource: VtkNewInstanceFactory<VtkAlgorithm>;
      vtkPlaneSource: VtkNewInstanceFactory<VtkAlgorithm>;
    };
    Core: {
      vtkPolyDataNormals: VtkNewInstanceFactory<VtkAlgorithm>;
    };
    General: {
      vtkTubeFilter: VtkNewInstanceFactory<VtkAlgorithm>;
      vtkClipClosedSurface?: VtkNewInstanceFactory<VtkAlgorithm>;
      vtkContourTriangulator?: VtkNewInstanceFactory<VtkAlgorithm>;
    };
    Texture: {
      vtkTextureMapToSphere: VtkNewInstanceFactory<VtkAlgorithm>;
    };
  };
  Common: {
    Core: {
      vtkPoints: VtkNewInstanceFactory<VtkPoints>;
      vtkDataArray: VtkDataArrayFactory;
    };
    DataModel: {
      vtkPolyData: VtkNewInstanceFactory<VtkPolyData>;
      vtkPlane: VtkNewInstanceFactory<VtkPlane>;
    };
  };
  Interaction: {
    Style: {
      vtkInteractorStyleTrackballCamera: VtkNewInstanceFactory<VtkInstance>;
    };
    Widgets: {
      vtkOrientationMarkerWidget: VtkOrientationMarkerWidgetFactory;
    };
  };
  IO: {
    Geometry: {
      vtkPLYReader: VtkNewInstanceFactory<VtkReader>;
      vtkSTLReader: VtkNewInstanceFactory<VtkReader>;
    };
    Misc: {
      vtkOBJReader: VtkNewInstanceFactory<VtkReader>;
    };
    Legacy: {
      vtkPolyDataReader: VtkNewInstanceFactory<VtkReader>;
    };
  };
}

declare const vtk: VtkGlobal;
declare let __pvjsSceneData: SceneData | undefined;
declare let __pvjsContainer: HTMLElement | undefined;

// --- Scene data interfaces (JSON schema) ---

interface LightConfig {
  type: string;
  position: [number, number, number];
  focalPoint: [number, number, number];
  color: [number, number, number];
  intensity: number;
  positional: boolean;
  coneAngle: number;
  coneFalloff: number;
  attenuationValues: [number, number, number];
}

interface NormalsConfig {
  computePointNormals: boolean;
  computeCellNormals: boolean;
}

interface PointDataArray {
  numberOfComponents: number;
  values: number[];
  name: string;
}

interface FilterConfig {
  type: string;
  shrinkFactor?: number;
  radius?: number;
  numberOfSides?: number;
  normal?: [number, number, number];
  origin?: [number, number, number];
  invert?: boolean;
  values?: number[];
  scalarName?: string;
  scalarData?: number[];
}

interface SourceConfig {
  type: string;
  // Sphere
  center?: [number, number, number];
  radius?: number;
  thetaResolution?: number;
  phiResolution?: number;
  // Cone / Cylinder
  height?: number;
  resolution?: number;
  // Cube
  xLength?: number;
  yLength?: number;
  zLength?: number;
  // Disk
  innerRadius?: number;
  outerRadius?: number;
  // Arrow
  tipLength?: number;
  tipRadius?: number;
  shaftRadius?: number;
  // Line
  point1?: [number, number, number];
  point2?: [number, number, number];
  // Plane
  origin?: [number, number, number];
  normal?: [number, number, number];
  // Mesh
  points?: number[];
  polys?: number[];
  // Reader
  data?: string;
  // Point data
  pointData?: PointDataArray[];
  tCoords?: number[];
  // Filters
  filters?: FilterConfig[];
}

interface EdgesConfig {
  color: [number, number, number];
}

interface PBRConfig {
  metallic: number;
  roughness: number;
}

interface TextureConfig {
  url: string;
}

interface ActorConfig {
  source: SourceConfig;
  color: [number, number, number];
  opacity: number;
  style: string;
  shading?: string;
  edges?: EdgesConfig;
  pbr?: PBRConfig;
  normals?: NormalsConfig;
  actorType?: string;
  renderPointsAsSpheres?: boolean;
  pointSize?: number;
  texture?: TextureConfig;
}

interface CameraConfig {
  position?: [number, number, number];
  focalPoint?: [number, number, number];
  viewUp?: [number, number, number];
  viewAngle?: number;
  clippingRange?: [number, number];
  parallelProjection?: boolean;
  viewVector?: [number, number, number];
}

interface TextActorConfig {
  text: string;
  position: [number, number];
  color: [number, number, number];
  opacity: number;
  fontSize: number;
  bold: boolean;
  italic: boolean;
}

interface SceneData {
  containerId: string;
  background: [number, number, number];
  lightingMode: string | null;
  lights: LightConfig[];
  actors: ActorConfig[];
  textActors?: TextActorConfig[];
  axes: boolean;
  camera?: CameraConfig;
}

// Extend Window for global references
interface Window {
  renderer: VtkRenderer;
  renderWindow: VtkRenderWindow;
  openGLRenderWindow: VtkOpenGLRenderWindow;
  interactor: VtkInteractor;
}
