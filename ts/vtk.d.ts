/**
 * Type declarations for the vtk.js CDN global object.
 *
 * Only the APIs actually used by `renderer.ts` are declared here.
 * These correspond to the global `vtk` object loaded from the CDN
 * (`https://unpkg.com/vtk.js`), not the ES-module `@kitware/vtk.js` package.
 */

/** Generic factory that creates vtk.js instances via `newInstance()`. */
interface VtkNewInstanceFactory<T> {
  newInstance(options?: Record<string, unknown>): T;
}

/** A vtk.js data array holding typed numeric values. */
interface VtkDataArray {
  getData(): Float32Array;
}

/** Factory for creating {@link VtkDataArray} instances. */
interface VtkDataArrayFactory {
  newInstance(options: {
    numberOfComponents: number;
    values: Float32Array;
    name: string;
  }): VtkDataArray;
}

/** Manages per-point data arrays (scalars, vectors, texture coordinates). */
interface VtkPointData {
  addArray(arr: VtkDataArray): void;
  setTCoords(arr: VtkDataArray): void;
  setActiveScalars(name: string): void;
  getArrayByName(name: string): VtkDataArray | null;
}

/** A set of 3D points. */
interface VtkPoints {
  setData(data: Float32Array, numberOfComponents: number): void;
}

/** A vtk.js cell array (polygons, lines, etc.). */
interface VtkCellArray {
  setData(data: Uint32Array): void;
  getData(): Uint32Array;
}

/** Polygonal mesh data structure — the core vtk.js data object. */
interface VtkPolyData {
  getPoints(): VtkPoints & {
    getData(): Float32Array;
    setData(data: Float32Array, n: number): void;
  };
  setPoints(points: VtkPoints): void;
  getPolys(): VtkCellArray;
  getLines(): VtkCellArray;
  getPointData(): VtkPointData;
}

/** An implicit plane defined by origin and normal. */
interface VtkPlane {
  setOrigin(x: number, y: number, z: number): void;
  setNormal(x: number, y: number, z: number): void;
}

/** Opaque handle representing a vtk.js output port. */
interface VtkOutputPort {
  readonly __brand: "VtkOutputPort";
}

/** A vtk.js algorithm (filter or source) with input/output pipeline. */
interface VtkAlgorithm {
  getOutputPort(): VtkOutputPort;
  getOutputData(): VtkPolyData;
  update(): void;
  setInputConnection(port: VtkOutputPort): void;
  setInputData(data: VtkPolyData): void;
  setComputePointNormals?(v: boolean): void;
  setComputeCellNormals?(v: boolean): void;
  setNormal?(x: number, y: number, z: number): void;
  setClippingPlanes?(planes: VtkPlane[]): void;
}

/** Controls surface appearance (color, opacity, shading, edges, PBR). */
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

/** A renderable entity in the scene that maps data through a mapper. */
interface VtkActor {
  setMapper(mapper: VtkMapper): void;
  getProperty(): VtkProperty;
  addTexture(texture: VtkTexture): void;
}

/** Maps data to graphics primitives for rendering. */
interface VtkMapper {
  setInputConnection(port: VtkOutputPort): void;
  setInputData(data: VtkPolyData): void;
  setRadius?(radius: number): void;
}

/** An image-based texture applied to actor surfaces. */
interface VtkTexture {
  setInterpolate(value: boolean): void;
  setImage(img: HTMLImageElement): void;
}

/** A virtual camera controlling the viewpoint. */
interface VtkCamera {
  setPosition(x: number, y: number, z: number): void;
  setFocalPoint(x: number, y: number, z: number): void;
  setViewUp(x: number, y: number, z: number): void;
  setViewAngle(angle: number): void;
  setClippingRange(near: number, far: number): void;
  setParallelProjection(value: boolean): void;
}

/** A scene light with position, color, and cone parameters. */
interface VtkLight {
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
  [key: string]: ((...args: number[]) => void) | undefined;
}

/** The vtk.js renderer that holds actors, lights, and a camera. */
interface VtkRenderer {
  setBackground(r: number, g: number, b: number): void;
  addActor(actor: VtkActor): void;
  addLight(light: VtkLight): void;
  removeAllLights(): void;
  setAutomaticLightCreation(value: boolean): void;
  resetCamera(): void;
  resetCameraClippingRange(): void;
  getActiveCamera(): VtkCamera;
}

/** The abstract render window managing renderers and views. */
interface VtkRenderWindow {
  addRenderer(renderer: VtkRenderer): void;
  addView(view: VtkOpenGLRenderWindow): void;
  render(): void;
}

/** The WebGL-backed render window that owns the canvas. */
interface VtkOpenGLRenderWindow {
  setContainer(container: HTMLElement): void;
  setSize(width: number, height: number): void;
}

/** Handles user interaction events (mouse, keyboard, touch). */
interface VtkInteractor {
  setInteractorStyle(style: VtkInteractorStyle): void;
  setView(view: VtkOpenGLRenderWindow): void;
  initialize(): void;
  bindEvents(container: HTMLElement): void;
}

/** A trackball camera interaction style. */
interface VtkInteractorStyle {
  readonly __brand: "VtkInteractorStyle";
}

/** A 3D orientation marker widget (axes glyph in corner). */
interface VtkOrientationMarkerWidget {
  setEnabled(value: boolean): void;
  setViewportCorner(corner: number): void;
  setViewportSize(size: number): void;
  setMinPixelSize(size: number): void;
  setMaxPixelSize(size: number): void;
}

/** A 3D axes actor used by the orientation marker widget. */
interface VtkAxesActor {
  readonly __brand: "VtkAxesActor";
}

/** Factory for {@link VtkOrientationMarkerWidget} with corner constants. */
interface VtkOrientationMarkerWidgetFactory {
  newInstance(options: {
    actor: VtkAxesActor;
    interactor: VtkInteractor;
  }): VtkOrientationMarkerWidget;
  Corners: { BOTTOM_LEFT: number };
}

/** A vtk.js file reader that parses binary or text data into PolyData. */
interface VtkReader {
  getOutputPort(): VtkOutputPort;
  getOutputData(): VtkPolyData;
  update(): void;
  parseAsArrayBuffer(buffer: ArrayBuffer): void;
  parseAsText(text: string): void;
}

/** Factory for creating {@link VtkReader} instances. */
interface VtkReaderFactory {
  newInstance(): VtkReader;
}

/** The top-level `vtk` global namespace loaded from the CDN. */
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
      vtkAxesActor: VtkNewInstanceFactory<VtkAxesActor>;
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
      vtkInteractorStyleTrackballCamera: VtkNewInstanceFactory<VtkInteractorStyle>;
    };
    Widgets: {
      vtkOrientationMarkerWidget: VtkOrientationMarkerWidgetFactory;
    };
  };
  IO: {
    Geometry: {
      vtkPLYReader: VtkReaderFactory;
      vtkSTLReader: VtkReaderFactory;
    };
    Misc: {
      vtkOBJReader: VtkReaderFactory;
    };
    Legacy: {
      vtkPolyDataReader: VtkReaderFactory;
    };
  };
}

declare const vtk: VtkGlobal;
declare const __pvjsSceneData: SceneData | undefined;
declare const __pvjsContainer: HTMLElement | undefined;

/** Configuration for a single light in the scene. */
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

/** Configuration for surface normal computation. */
interface NormalsConfig {
  computePointNormals: boolean;
  computeCellNormals: boolean;
}

/** A named array of per-point data values. */
interface PointDataArray {
  numberOfComponents: number;
  values: number[];
  name: string;
}

/** Configuration for a geometry filter (shrink, tube, clip, or contour). */
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

/** Configuration for a geometry source (primitive, mesh, or file reader). */
interface SourceConfig {
  type: string;
  center?: [number, number, number];
  radius?: number;
  thetaResolution?: number;
  phiResolution?: number;
  height?: number;
  resolution?: number;
  xLength?: number;
  yLength?: number;
  zLength?: number;
  innerRadius?: number;
  outerRadius?: number;
  tipLength?: number;
  tipRadius?: number;
  shaftRadius?: number;
  point1?: [number, number, number];
  point2?: [number, number, number];
  origin?: [number, number, number];
  normal?: [number, number, number];
  points?: number[];
  polys?: number[];
  data?: string;
  pointData?: PointDataArray[];
  tCoords?: number[];
  filters?: FilterConfig[];
}

/** Edge rendering configuration. */
interface EdgesConfig {
  color: [number, number, number];
}

/** Physically-based rendering parameters. */
interface PBRConfig {
  metallic: number;
  roughness: number;
}

/** Configuration for an image texture loaded from a URL. */
interface TextureConfig {
  url: string;
}

/** Full configuration for a single actor in the scene. */
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

/** Camera position and projection settings. */
interface CameraConfig {
  position?: [number, number, number];
  focalPoint?: [number, number, number];
  viewUp?: [number, number, number];
  viewAngle?: number;
  clippingRange?: [number, number];
  parallelProjection?: boolean;
  viewVector?: [number, number, number];
}

/** Configuration for a 2D text overlay. */
interface TextActorConfig {
  text: string;
  position: [number, number];
  color: [number, number, number];
  opacity: number;
  fontSize: number;
  bold: boolean;
  italic: boolean;
}

/** Top-level scene description passed from Python as JSON. */
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

/** Extends the global Window with vtk.js renderer references. */
interface Window {
  renderer: VtkRenderer;
  renderWindow: VtkRenderWindow;
  openGLRenderWindow: VtkOpenGLRenderWindow;
  interactor: VtkInteractor;
}

/** Maps reader type names to their vtk.js factory and parse method. */
type ReaderFactoryMap = Record<
  string,
  { factory: VtkReaderFactory; parseMethod: "parseAsArrayBuffer" | "parseAsText" }
>;
