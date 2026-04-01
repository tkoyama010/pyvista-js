/**
 * Pyvista-js renderer — reads scene configuration from JSON and creates
 * vtk.js objects.
 *
 * In JupyterLite, `_generate_render_js()` sets `__pvjsSceneData` and
 * `__pvjsContainer` before evaluating this code. In standalone HTML,
 * the scene data is read from the DOM.
 */

/** Number of components in a 3-D coordinate (x, y, z). */
// biome-ignore lint/nursery/noExcessiveLinesPerFile: renderer is a cohesive single-file module
const XYZ_COMPONENTS = 3;

/** Number of components in a 2-D texture coordinate (u, v). */
const UV_COMPONENTS = 2;

/** Default fallback width (px) when the container has no intrinsic size. */
const DEFAULT_WIDTH = 600;

/** Default fallback height (px) when the container has no intrinsic size. */
const DEFAULT_HEIGHT = 400;

/** Scale factor to convert a [0-1] float colour channel to [0-255] integer. */
const COLOR_BYTE_SCALE = 255;

/** Multiplier to convert a normalised fraction to a CSS percentage. */
const PERCENT = 100;

/** Default outer radius for a circle/disk source. */
const DEFAULT_RADIUS = 1;

/** Default circumferential resolution for a circle/disk source. */
const DEFAULT_RESOLUTION = 50;

/** Multiplier applied to pointSize when rendering points as spheres. */
const POINT_SPHERE_RADIUS_SCALE = 0.01;

/** Default point size (px) when none is specified. */
const DEFAULT_POINT_SIZE = 5;

// PBR material constants — hand-tuned for a plausible metallic/roughness look.
const PBR_AMBIENT = 0.1;
const PBR_SPECULAR_METALLIC_WEIGHT = 0.75;
const PBR_SPECULAR_BASE = 0.25;
const PBR_SPECULAR_POWER_SCALE = 100;
const PBR_DIFFUSE_BASE = 0.65;
const PBR_DIFFUSE_METALLIC_WEIGHT = 0.35;

// Orientation-marker widget layout.
const AXES_VIEWPORT_SIZE = 0.15;
const AXES_MIN_PIXEL_SIZE = 100;
const AXES_MAX_PIXEL_SIZE = 300;

// vtk.js representation enum values.
const VTK_REPRESENTATION_SURFACE = 2;
const VTK_REPRESENTATION_WIREFRAME = 1;
const VTK_REPRESENTATION_POINTS = 0;

// Disk source uses a single radial ring.
const DISK_RADIAL_RESOLUTION = 1;

/** Number of vertices in a triangle. */
const TRIANGLE_VERTS = 3;

/** Number of coordinates produced by two edge intersections (2 points × 3 components). */
const TWO_POINTS_XYZ = 6;

/**
 * Access a typed array element, returning 0 for out-of-bounds.
 * @param array
 * @param index
 * @returns The element at `index`, or 0 if out of bounds.
 */
function at(array: Float32Array | Uint32Array, index: number): number {
  return array[index] ?? 0;
}

/** Wraps either a vtk.js algorithm (filter/source) or raw PolyData. */
interface SourceResult {
  output: VtkAlgorithm | VtkPolyData;
  isFilter: boolean;
}

/**
 * Resolve a {@link SourceResult} to its underlying PolyData.
 * @param sourceResult
 * @returns The underlying {@link VtkPolyData} from the source or filter output.
 */
function getPolyData(sourceResult: SourceResult): VtkPolyData {
  if (sourceResult.isFilter) {
    (sourceResult.output as VtkAlgorithm).update();
    return (sourceResult.output as VtkAlgorithm).getOutputData();
  }

  return sourceResult.output as VtkPolyData;
}

/**
 * Wire `filter`'s input to the output of `sourceResult`.
 * @param filter
 * @param sourceResult
 */
function connectInput(filter: VtkAlgorithm, sourceResult: SourceResult): void {
  if (sourceResult.isFilter) {
    filter.setInputConnection((sourceResult.output as VtkAlgorithm).getOutputPort());
  } else {
    filter.setInputData(sourceResult.output as VtkPolyData);
  }
}

const sceneData: SceneData =
  // biome-ignore lint/nursery/noTernary lint/correctness/noUndeclaredVariables: ternary is idiomatic for concise conditional returns
  typeof __pvjsSceneData === "undefined"
    ? (JSON.parse(document.querySelector("#scene-data")?.textContent ?? "{}") as SceneData)
    : // biome-ignore lint/correctness/noUndeclaredVariables: vtk globals are declared in vtk.d.ts
      __pvjsSceneData;
const container: HTMLElement =
  // biome-ignore lint/nursery/noTernary lint/correctness/noUndeclaredVariables: ternary is idiomatic for concise conditional returns
  typeof __pvjsContainer === "undefined"
    ? (document.querySelector<HTMLElement>(`#${CSS.escape(sceneData.containerId)}`) ??
      document.createElement("div"))
    : // biome-ignore lint/correctness/noUndeclaredVariables: vtk globals are declared in vtk.d.ts
      __pvjsContainer;
// biome-ignore lint/nursery/useExplicitType: vtk.js factory return types are untyped
const bg = sceneData.background;

// biome-ignore lint/nursery/useExplicitType lint/correctness/noUndeclaredVariables: vtk.js factory return types are untyped
const renderer = vtk.Rendering.Core.vtkRenderer.newInstance();
renderer.setBackground(bg[0], bg[1], bg[2]);

// biome-ignore lint/nursery/useExplicitType lint/correctness/noUndeclaredVariables: vtk.js factory return types are untyped
const renderWindow = vtk.Rendering.Core.vtkRenderWindow.newInstance();
renderWindow.addRenderer(renderer);

// biome-ignore lint/nursery/useExplicitType lint/correctness/noUndeclaredVariables: vtk.js factory return types are untyped
const openGlRenderWindow = vtk.Rendering.OpenGL.vtkRenderWindow.newInstance();
renderWindow.addView(openGlRenderWindow);
openGlRenderWindow.setContainer(container);

// biome-ignore lint/nursery/useExplicitType: vtk.js factory return types are untyped
const bbox = container.getBoundingClientRect();
openGlRenderWindow.setSize(bbox.width || DEFAULT_WIDTH, bbox.height || DEFAULT_HEIGHT);

// biome-ignore lint/nursery/useExplicitType lint/correctness/noUndeclaredVariables: vtk.js factory return types are untyped
const interactor = vtk.Rendering.Core.vtkRenderWindowInteractor.newInstance();
// biome-ignore lint/nursery/useExplicitType lint/correctness/noUndeclaredVariables: vtk.js factory return types are untyped
const interactorStyle = vtk.Interaction.Style.vtkInteractorStyleTrackballCamera.newInstance();
interactor.setInteractorStyle(interactorStyle);
interactor.setView(openGlRenderWindow);
interactor.initialize();
interactor.bindEvents(container);

// biome-ignore lint/nursery/useGlobalThis: window augmentation requires window, not globalThis
window.renderer = renderer;
// biome-ignore lint/nursery/useGlobalThis: window augmentation requires window, not globalThis
window.renderWindow = renderWindow;
// biome-ignore lint/nursery/useGlobalThis: window augmentation requires window, not globalThis
window.openGlRenderWindow = openGlRenderWindow;
// biome-ignore lint/nursery/useGlobalThis: window augmentation requires window, not globalThis
window.interactor = interactor;

if (sceneData.lightingMode === null && sceneData.lights.length === 0) {
  renderer.removeAllLights();
  renderer.setAutomaticLightCreation(false);
} else {
  setupLights(sceneData.lights, renderer);
}

for (const [index, actorConfig] of sceneData.actors.entries()) {
  setupActor(actorConfig, index, renderer, renderWindow);
}

if (sceneData.textActors) {
  for (const textConfig of sceneData.textActors) {
    setupTextActor(textConfig, container);
  }
}

if (sceneData.axes) {
  setupAxes(interactor);
}

renderer.resetCamera();
if (sceneData.camera) {
  setupCamera(renderer, sceneData.camera);
}

renderWindow.render();

/**
 * Add custom lights to the renderer, replacing the defaults.
 * @param lightsConfig
 * @param ren
 * @returns Nothing; mutates the renderer in place.
 */
function setupLights(lightsConfig: LightConfig[], ren: VtkRenderer): void {
  if (lightsConfig.length === 0) {
    return;
  }

  ren.removeAllLights();
  ren.setAutomaticLightCreation(false);
  for (const cfg of lightsConfig) {
    // biome-ignore lint/correctness/noUndeclaredVariables: vtk globals are declared in vtk.d.ts
    const light = vtk.Rendering.Core.vtkLight.newInstance();
    const typeMap: Record<string, string> = {
      // biome-ignore lint/security/noSecrets: vtk.js method name, not a secret
      scene: "setLightTypeToSceneLight",
      // biome-ignore lint/security/noSecrets: vtk.js method name, not a secret
      camera: "setLightTypeToCameraLight",
      // biome-ignore lint/security/noSecrets: vtk.js method name, not a secret
      head: "setLightTypeToHeadLight",
    };
    // biome-ignore lint/security/noSecrets: vtk.js method name, not a secret
    const setter = typeMap[cfg.type] ?? "setLightTypeToSceneLight";
    const setterFunction = light[setter];
    if (typeof setterFunction === "function") {
      (setterFunction as () => void).call(light);
    }

    light.setPosition(cfg.position[0], cfg.position[1], cfg.position[2]);
    light.setFocalPoint(cfg.focalPoint[0], cfg.focalPoint[1], cfg.focalPoint[2]);
    light.setColor(cfg.color[0], cfg.color[1], cfg.color[2]);
    light.setIntensity(cfg.intensity);
    light.setPositional(cfg.positional);
    light.setConeAngle(cfg.coneAngle);
    light.setExponent(cfg.coneFalloff);
    light.setAttenuationValues(
      cfg.attenuationValues[0],
      cfg.attenuationValues[1],
      cfg.attenuationValues[2],
    );
    ren.addLight(light);
  }
}

/**
 * Lazily build the reader factory map to avoid accessing vtk.IO at module load time.
 * @returns A map from reader type names to their factory and parse method.
 */
function getReaderMap(): ReaderFactoryMap {
  return {
    plyReader: {
      // biome-ignore lint/correctness/noUndeclaredVariables: vtk globals are declared in vtk.d.ts
      factory: vtk.IO.Geometry.vtkPLYReader,
      parseMethod: "parseAsArrayBuffer",
    },
    stlReader: {
      // biome-ignore lint/correctness/noUndeclaredVariables: vtk globals are declared in vtk.d.ts
      factory: vtk.IO.Geometry.vtkSTLReader,
      parseMethod: "parseAsArrayBuffer",
    },
    objReader: {
      // biome-ignore lint/correctness/noUndeclaredVariables: vtk globals are declared in vtk.d.ts
      factory: vtk.IO.Misc.vtkOBJReader,
      parseMethod: "parseAsText",
    },
    vtkReader: {
      // biome-ignore lint/correctness/noUndeclaredVariables: vtk globals are declared in vtk.d.ts
      factory: vtk.IO.Legacy.vtkPolyDataReader,
      parseMethod: "parseAsText",
    },
  };
}

/**
 * Dispatch to the appropriate source factory based on `cfg.type`.
 * @param cfg
 * @returns A {@link SourceResult} for the configured source type, or `undefined` if the type is unknown.
 */
function createSource(cfg: SourceConfig): SourceResult | undefined {
  const sourceFactoryMap: Record<string, (sourceCfg: SourceConfig) => SourceResult> = {
    sphere: createSphereSource,
    cone: createConeSource,
    cube: createCubeSource,
    cylinder: createCylinderSource,
    disk: createDiskSource,
    circle: createCircleSource,
    arrow: createArrowSource,
    line: createLineSource,
    plane: createPlaneSource,
    mesh: createMeshSource,
    points: createPointsSource,
    plyReader: createReaderSource,
    stlReader: createReaderSource,
    objReader: createReaderSource,
    vtkReader: createReaderSource,
  };

  const factory = sourceFactoryMap[cfg.type];
  if (!factory) {
    return;
  }

  return factory(cfg);
}

/**
 * Create a sphere source with texture-map-to-sphere applied.
 * @param cfg
 * @returns A {@link SourceResult} wrapping the texture-mapped sphere filter.
 */
function createSphereSource(cfg: SourceConfig): SourceResult {
  // biome-ignore lint/correctness/noUndeclaredVariables: vtk globals are declared in vtk.d.ts
  const source = vtk.Filters.Sources.vtkSphereSource.newInstance({
    center: cfg.center,
    radius: cfg.radius,
    thetaResolution: cfg.thetaResolution,
    phiResolution: cfg.phiResolution,
  });
  // biome-ignore lint/correctness/noUndeclaredVariables: vtk globals are declared in vtk.d.ts
  const texMap = vtk.Filters.Texture.vtkTextureMapToSphere.newInstance();
  texMap.setInputConnection(source.getOutputPort());
  return { output: texMap, isFilter: true };
}

/**
 * Create a cone source.
 * @param cfg
 * @returns A {@link SourceResult} wrapping the cone source filter.
 */
function createConeSource(cfg: SourceConfig): SourceResult {
  // biome-ignore lint/correctness/noUndeclaredVariables: vtk globals are declared in vtk.d.ts
  const source = vtk.Filters.Sources.vtkConeSource.newInstance({
    height: cfg.height,
    radius: cfg.radius,
    resolution: cfg.resolution,
  });
  return { output: source, isFilter: true };
}

/**
 * Create a cube source.
 * @param cfg
 * @returns A {@link SourceResult} wrapping the cube source.
 */
function createCubeSource(cfg: SourceConfig): SourceResult {
  // biome-ignore lint/correctness/noUndeclaredVariables: vtk globals are declared in vtk.d.ts
  const source = vtk.Filters.Sources.vtkCubeSource.newInstance({
    xLength: cfg.xLength,
    yLength: cfg.yLength,
    zLength: cfg.zLength,
  });
  return { output: source, isFilter: false };
}

/**
 * Create a cylinder source.
 * @param cfg
 * @returns A {@link SourceResult} wrapping the cylinder source filter.
 */
function createCylinderSource(cfg: SourceConfig): SourceResult {
  // biome-ignore lint/correctness/noUndeclaredVariables: vtk globals are declared in vtk.d.ts
  const source = vtk.Filters.Sources.vtkCylinderSource.newInstance({
    height: cfg.height,
    radius: cfg.radius,
    resolution: cfg.resolution,
  });
  return { output: source, isFilter: true };
}

/**
 * Create a disk source, falling back to empty PolyData if unavailable.
 * @param cfg
 * @returns A {@link SourceResult} wrapping the disk source or empty PolyData fallback.
 */
function createDiskSource(cfg: SourceConfig): SourceResult {
  // biome-ignore lint/correctness/noUndeclaredVariables: vtk globals are declared in vtk.d.ts
  const diskFactory = vtk.Filters.Sources.vtkDiskSource;
  // biome-ignore lint/nursery/noTernary: ternary is idiomatic for concise conditional returns
  const source = diskFactory
    ? diskFactory.newInstance({
        innerRadius: cfg.innerRadius,
        outerRadius: cfg.outerRadius,
        radialResolution: DISK_RADIAL_RESOLUTION,
        circumferentialResolution: cfg.resolution,
      })
    : undefined;
  return {
    // biome-ignore lint/correctness/noUndeclaredVariables: vtk globals are declared in vtk.d.ts
    output: source ?? vtk.Common.DataModel.vtkPolyData.newInstance(),
    isFilter: true,
  };
}

/**
 * Create a circle source (disk with `innerRadius=0`).
 * @param cfg
 * @returns A {@link SourceResult} wrapping the disk source configured as a circle.
 */
function createCircleSource(cfg: SourceConfig): SourceResult {
  return createDiskSource({
    type: "disk",
    innerRadius: 0,
    outerRadius: cfg.radius ?? DEFAULT_RADIUS,
    resolution: cfg.resolution ?? DEFAULT_RESOLUTION,
  });
}

/**
 * Create an arrow source.
 * @param cfg
 * @returns A {@link SourceResult} wrapping the arrow source filter.
 */
function createArrowSource(cfg: SourceConfig): SourceResult {
  // biome-ignore lint/correctness/noUndeclaredVariables: vtk globals are declared in vtk.d.ts
  const source = vtk.Filters.Sources.vtkArrowSource.newInstance({
    tipLength: cfg.tipLength,
    tipRadius: cfg.tipRadius,
    shaftRadius: cfg.shaftRadius,
  });
  return { output: source, isFilter: true };
}

/**
 * Create a line source between two points.
 * @param cfg
 * @returns A {@link SourceResult} wrapping the line source filter.
 */
function createLineSource(cfg: SourceConfig): SourceResult {
  // biome-ignore lint/correctness/noUndeclaredVariables: vtk globals are declared in vtk.d.ts
  const source = vtk.Filters.Sources.vtkLineSource.newInstance({
    point1: cfg.point1,
    point2: cfg.point2,
  });
  return { output: source, isFilter: true };
}

/**
 * Create a plane source with optional normal.
 * @param cfg
 * @returns A {@link SourceResult} wrapping the plane source filter.
 */
function createPlaneSource(cfg: SourceConfig): SourceResult {
  // biome-ignore lint/correctness/noUndeclaredVariables: vtk globals are declared in vtk.d.ts
  const source = vtk.Filters.Sources.vtkPlaneSource.newInstance({
    origin: cfg.origin,
  });
  if (cfg.normal) {
    source.setNormal?.(cfg.normal[0], cfg.normal[1], cfg.normal[2]);
  }

  return { output: source, isFilter: true };
}

/**
 * Create PolyData from raw point and polygon arrays.
 * @param cfg
 * @returns A {@link SourceResult} wrapping the constructed mesh PolyData.
 */
function createMeshSource(cfg: SourceConfig): SourceResult {
  // biome-ignore lint/correctness/noUndeclaredVariables: vtk globals are declared in vtk.d.ts
  const polydata = vtk.Common.DataModel.vtkPolyData.newInstance();
  const pointsArray = Float32Array.from(cfg.points ?? []);
  // biome-ignore lint/correctness/noUndeclaredVariables: vtk globals are declared in vtk.d.ts
  const vtkPts = vtk.Common.Core.vtkPoints.newInstance();
  vtkPts.setData(pointsArray, XYZ_COMPONENTS);
  polydata.setPoints(vtkPts);
  if (cfg.polys) {
    const polysArray = Uint32Array.from(cfg.polys);
    polydata.getPolys().setData(polysArray);
  }

  return { output: polydata, isFilter: false };
}

/**
 * Create a point cloud PolyData from raw point arrays.
 * @param cfg
 * @returns A {@link SourceResult} wrapping the point cloud PolyData.
 */
function createPointsSource(cfg: SourceConfig): SourceResult {
  // biome-ignore lint/correctness/noUndeclaredVariables: vtk globals are declared in vtk.d.ts
  const polydata = vtk.Common.DataModel.vtkPolyData.newInstance();
  const pointsArray = Float32Array.from(cfg.points ?? []);
  // biome-ignore lint/correctness/noUndeclaredVariables: vtk globals are declared in vtk.d.ts
  const vtkPts = vtk.Common.Core.vtkPoints.newInstance();
  vtkPts.setData(pointsArray, XYZ_COMPONENTS);
  polydata.setPoints(vtkPts);
  return { output: polydata, isFilter: false };
}

/**
 * Decode base64-encoded file data and parse it with the appropriate vtk.js reader.
 * @param cfg
 * @returns A {@link SourceResult} wrapping the parsed reader as a filter.
 */
function createReaderSource(cfg: SourceConfig): SourceResult {
  const entry = getReaderMap()[cfg.type] as
    | { factory: VtkReaderFactory; parseMethod: "parseAsArrayBuffer" | "parseAsText" }
    | undefined;
  if (!entry) {
    throw new Error(`Unknown reader type: ${cfg.type}`);
  }

  // eslint-disable-next-line no-restricted-globals -- browser-only base64 decoding
  const bytes = Uint8Array.from(atob(cfg.data ?? ""), (char) => char.codePointAt(0) ?? 0);

  const reader = entry.factory.newInstance();
  if (entry.parseMethod === "parseAsText") {
    reader.parseAsText(new TextDecoder().decode(bytes));
  } else {
    reader.parseAsArrayBuffer(new Uint8Array(bytes).buffer);
  }

  return {
    output: reader as unknown as VtkAlgorithm,
    isFilter: true,
  };
}

/**
 * Inject per-point scalar/vector data arrays into PolyData.
 * @param polydata
 * @param pointDataArrays
 */
function injectPointData(
  polydata: VtkPolyData,
  pointDataArrays: PointDataArray[] | undefined,
): void {
  if (!pointDataArrays) {
    return;
  }

  for (const array of pointDataArrays) {
    // biome-ignore lint/correctness/noUndeclaredVariables: vtk globals are declared in vtk.d.ts
    const dataArray = vtk.Common.Core.vtkDataArray.newInstance({
      numberOfComponents: array.numberOfComponents,
      values: Float32Array.from(array.values),
      name: array.name,
    });
    polydata.getPointData().addArray(dataArray);
  }
}

/**
 * Inject 2-component texture coordinates into PolyData.
 * @param polydata
 * @param tCoords
 */
function injectTcoords(polydata: VtkPolyData, tCoords: number[] | undefined): void {
  if (!tCoords) {
    return;
  }

  // biome-ignore lint/correctness/noUndeclaredVariables: vtk globals are declared in vtk.d.ts
  const tcArray = vtk.Common.Core.vtkDataArray.newInstance({
    numberOfComponents: UV_COMPONENTS,
    values: Float32Array.from(tCoords),
    name: "TextureCoordinates",
  });
  polydata.getPointData().setTcoords(tcArray);
}

/**
 * Optionally insert a normals-computation filter between source and mapper.
 * @param sourceResult
 * @param normalsConfig
 * @returns The original {@link SourceResult} if no normals config, otherwise a new one with the normals filter applied.
 */
function setupNormals(
  sourceResult: SourceResult,
  normalsConfig: NormalsConfig | undefined,
): SourceResult {
  if (!normalsConfig) {
    return sourceResult;
  }

  // biome-ignore lint/correctness/noUndeclaredVariables: vtk globals are declared in vtk.d.ts
  const normals = vtk.Filters.Core.vtkPolyDataNormals.newInstance();
  normals.setComputePointNormals?.(normalsConfig.computePointNormals);
  normals.setComputeCellNormals?.(normalsConfig.computeCellNormals);
  connectInput(normals, sourceResult);
  return { output: normals, isFilter: true };
}

/**
 * Apply physically-based rendering properties to an actor.
 * @param actor
 * @param pbr
 */
function applyPbr(actor: VtkActor, pbr: PbrConfig | undefined): void {
  if (!pbr) {
    return;
  }
  actor.getProperty().setInterpolationToPhong();
  const m = pbr.metallic;
  const r = pbr.roughness;
  actor.getProperty().setMetallic(m);
  actor.getProperty().setRoughness(r);
  actor.getProperty().setAmbient(PBR_AMBIENT);
  actor.getProperty().setSpecular(PBR_SPECULAR_METALLIC_WEIGHT * m + PBR_SPECULAR_BASE);
  actor.getProperty().setSpecularPower(Math.max(1, PBR_SPECULAR_POWER_SCALE * (1 - r)));
  actor.getProperty().setDiffuse(PBR_DIFFUSE_BASE + PBR_DIFFUSE_METALLIC_WEIGHT * (1 - m));
}

/**
 * Load and attach a URL-based texture to an actor.
 * @param actor
 * @param renWin
 * @param textureCfg
 */
function applyTexture(
  actor: VtkActor,
  renWin: VtkRenderWindow,
  textureCfg: TextureConfig | undefined,
): void {
  if (!textureCfg) {
    return;
  }
  // biome-ignore lint/correctness/noUndeclaredVariables: vtk globals are declared in vtk.d.ts
  const texture = vtk.Rendering.Core.vtkTexture.newInstance();
  texture.setInterpolate(true);
  actor.addTexture(texture);
  const img = new Image();
  img.crossOrigin = "anonymous";
  img.addEventListener("load", () => {
    texture.setImage(img);
    renWin.render();
  });
  img.src = textureCfg.url;
}

/**
 * Apply representation style and shading to an actor.
 * @param actor
 * @param cfg
 */
function applyActorStyle(actor: VtkActor, cfg: ActorConfig): void {
  const styleMap: Record<string, number> = {
    surface: VTK_REPRESENTATION_SURFACE,
    wireframe: VTK_REPRESENTATION_WIREFRAME,
    points: VTK_REPRESENTATION_POINTS,
  };
  const rep = styleMap[cfg.style];
  if (rep !== undefined) {
    actor.getProperty().setRepresentation(rep);
  }

  if (cfg.shading === "gouraud") {
    actor.getProperty().setInterpolationToGouraud();
  } else if (cfg.shading === "flat") {
    actor.getProperty().setInterpolationToFlat();
  }

  if (cfg.edges) {
    actor.getProperty().setEdgeVisibility(true);
    actor.getProperty().setEdgeColor(cfg.edges.color[0], cfg.edges.color[1], cfg.edges.color[2]);
  }
}

/**
 * Configure point-specific rendering on the actor and mapper.
 * @param actor
 * @param mapper
 * @param cfg
 */
function applyPointStyle(actor: VtkActor, mapper: VtkMapper, cfg: ActorConfig): void {
  if (cfg.actorType !== "points") {
    return;
  }

  if (cfg.renderPointsAsSpheres && mapper.setRadius) {
    mapper.setRadius((cfg.pointSize ?? DEFAULT_POINT_SIZE) * POINT_SPHERE_RADIUS_SCALE);
  } else {
    actor.getProperty().setPointSize(cfg.pointSize ?? DEFAULT_POINT_SIZE);
    actor.getProperty().setRepresentationToPoints();
  }
}

/**
 * Create a mapper and connect it to the source pipeline.
 * @param mapperInput
 * @param cfg
 * @returns The configured mapper.
 */
function createMapper(mapperInput: SourceResult, cfg: ActorConfig): VtkMapper {
  const mapperClass =
    // biome-ignore lint/nursery/noTernary: ternary is idiomatic for concise conditional returns
    cfg.actorType === "points" && cfg.renderPointsAsSpheres
      ? // biome-ignore lint/correctness/noUndeclaredVariables: vtk globals are declared in vtk.d.ts
        vtk.Rendering.Core.vtkSphereMapper
      : // biome-ignore lint/correctness/noUndeclaredVariables: vtk globals are declared in vtk.d.ts
        vtk.Rendering.Core.vtkMapper;
  const mapper = mapperClass.newInstance();
  if (mapperInput.isFilter) {
    mapper.setInputConnection((mapperInput.output as VtkAlgorithm).getOutputPort());
  } else {
    mapper.setInputData(mapperInput.output as VtkPolyData);
  }

  return mapper;
}

/**
 * Build a complete vtk.js actor from an {@link ActorConfig} and add it to the renderer.
 * @param cfg
 * @param _index
 * @param ren
 * @param renWin
 */
function setupActor(
  cfg: ActorConfig,
  _index: number,
  ren: VtkRenderer,
  renWin: VtkRenderWindow,
): void {
  const sourceResult = createSource(cfg.source);
  if (!sourceResult?.output) {
    return;
  }

  if (cfg.source.pointData ?? cfg.source.tCoords) {
    const pd = getPolyData(sourceResult);
    injectPointData(pd, cfg.source.pointData);
    injectTcoords(pd, cfg.source.tCoords);
  }

  let currentResult = sourceResult;
  if (cfg.source.filters && cfg.source.filters.length > 0) {
    currentResult = applyFilters(sourceResult, cfg.source.filters);
  }

  const mapperInput = setupNormals(currentResult, cfg.normals);
  const mapper = createMapper(mapperInput, cfg);

  // biome-ignore lint/correctness/noUndeclaredVariables: vtk globals are declared in vtk.d.ts
  const actor = vtk.Rendering.Core.vtkActor.newInstance();
  actor.setMapper(mapper);
  actor.getProperty().setColor(cfg.color[0], cfg.color[1], cfg.color[2]);
  actor.getProperty().setOpacity(cfg.opacity);

  applyActorStyle(actor, cfg);
  applyPbr(actor, cfg.pbr);
  applyPointStyle(actor, mapper, cfg);
  applyTexture(actor, renWin, cfg.texture);

  ren.addActor(actor);
}

/**
 * Apply camera settings from the scene configuration.
 * @param ren
 * @param camConfig
 */
function setupCamera(ren: VtkRenderer, camConfig: CameraConfig): void {
  const cam = ren.getActiveCamera();
  if (camConfig.position) {
    cam.setPosition(camConfig.position[0], camConfig.position[1], camConfig.position[2]);
  }

  if (camConfig.focalPoint) {
    cam.setFocalPoint(camConfig.focalPoint[0], camConfig.focalPoint[1], camConfig.focalPoint[2]);
  }

  if (camConfig.viewUp) {
    cam.setViewUp(camConfig.viewUp[0], camConfig.viewUp[1], camConfig.viewUp[2]);
  }

  if (camConfig.viewAngle !== undefined) {
    cam.setViewAngle(camConfig.viewAngle);
  }

  if (camConfig.clippingRange) {
    cam.setClippingRange(camConfig.clippingRange[0], camConfig.clippingRange[1]);
  }

  if (camConfig.parallelProjection) {
    cam.setParallelProjection(true);
  }

  if (camConfig.viewVector && camConfig.viewUp) {
    cam.setPosition(camConfig.viewVector[0], camConfig.viewVector[1], camConfig.viewVector[2]);
    cam.setViewUp(camConfig.viewUp[0], camConfig.viewUp[1], camConfig.viewUp[2]);
    cam.setFocalPoint(0, 0, 0);
    ren.resetCamera();
    ren.resetCameraClippingRange();
  }
}

/**
 * Add an orientation-marker axes widget to the bottom-left corner.
 * @param interactorObject
 */
function setupAxes(interactorObject: VtkInteractor): void {
  // biome-ignore lint/correctness/noUndeclaredVariables: vtk globals are declared in vtk.d.ts
  const axes = vtk.Rendering.Core.vtkAxesActor.newInstance();
  // biome-ignore lint/correctness/noUndeclaredVariables: vtk globals are declared in vtk.d.ts
  const orientationWidget = vtk.Interaction.Widgets.vtkOrientationMarkerWidget.newInstance({
    actor: axes,
    interactor: interactorObject,
  });
  orientationWidget.setEnabled(true);
  orientationWidget.setViewportCorner(
    // biome-ignore lint/correctness/noUndeclaredVariables: vtk globals are declared in vtk.d.ts
    vtk.Interaction.Widgets.vtkOrientationMarkerWidget.Corners.BOTTOM_LEFT,
  );
  orientationWidget.setViewportSize(AXES_VIEWPORT_SIZE);
  orientationWidget.setMinPixelSize(AXES_MIN_PIXEL_SIZE);
  orientationWidget.setMaxPixelSize(AXES_MAX_PIXEL_SIZE);
}

/**
 * Create an absolutely-positioned HTML overlay for 2D text.
 * @param cfg
 * @param containerElement
 */
function setupTextActor(cfg: TextActorConfig, containerElement: HTMLElement): void {
  const div = document.createElement("div");
  div.textContent = cfg.text;
  div.style.position = "absolute";
  div.style.left = `${String(cfg.position[0] * PERCENT)}%`;
  div.style.bottom = `${String(cfg.position[1] * PERCENT)}%`;
  const r = Math.round(cfg.color[0] * COLOR_BYTE_SCALE);
  const g = Math.round(cfg.color[1] * COLOR_BYTE_SCALE);
  const b = Math.round(cfg.color[2] * COLOR_BYTE_SCALE);
  div.style.color = `rgba(${String(r)},${String(g)},${String(b)},${String(cfg.opacity)})`;
  div.style.fontSize = `${String(cfg.fontSize)}px`;
  // biome-ignore lint/nursery/noTernary: ternary is idiomatic for concise conditional returns
  div.style.fontWeight = cfg.bold ? "bold" : "normal";
  // biome-ignore lint/nursery/noTernary: ternary is idiomatic for concise conditional returns
  div.style.fontStyle = cfg.italic ? "italic" : "normal";
  div.style.pointerEvents = "none";
  div.style.zIndex = "10";
  div.style.whiteSpace = "pre";
  div.style.textShadow = "1px 1px 2px rgba(0,0,0,0.8), -1px -1px 2px rgba(0,0,0,0.8)";
  containerElement.append(div);
}

/**
 * Try to apply a shrink filter.
 * @param current
 * @param f
 * @returns The filtered result, or the original if config is incomplete.
 */
function tryShrinkFilter(current: SourceResult, f: FilterConfig): SourceResult {
  // biome-ignore lint/nursery/noTernary: ternary is idiomatic for concise conditional returns
  return f.shrinkFactor === undefined ? current : applyShrinkFilter(current, f.shrinkFactor);
}

/**
 * Try to apply a tube filter.
 * @param current
 * @param f
 * @returns The filtered result, or the original if config is incomplete.
 */
function tryTubeFilter(current: SourceResult, f: FilterConfig): SourceResult {
  // biome-ignore lint/nursery/noTernary: ternary is idiomatic for concise conditional returns
  return f.radius === undefined || f.numberOfSides === undefined
    ? current
    : applyTubeFilter(current, f.radius, f.numberOfSides);
}

/**
 * Try to apply a clip filter.
 * @param current
 * @param f
 * @returns The filtered result, or the original if config is incomplete.
 */
function tryClipFilter(current: SourceResult, f: FilterConfig): SourceResult {
  // biome-ignore lint/nursery/noTernary: ternary is idiomatic for concise conditional returns
  return !(f.normal && f.origin) || f.invert === undefined
    ? current
    : applyClipFilter(current, f.normal, f.origin, f.invert);
}

/**
 * Try to apply a contour filter.
 * @param current
 * @param f
 * @returns The filtered result, or the original if config is incomplete.
 */
function tryContourFilter(current: SourceResult, f: FilterConfig): SourceResult {
  // biome-ignore lint/nursery/noTernary: ternary is idiomatic for concise conditional returns
  return f.values && f.scalarName && f.scalarData
    ? applyContourFilter(current, f.values, f.scalarName, f.scalarData)
    : current;
}

/**
 * Try to apply a fill-holes filter.
 * @param current
 * @param f
 * @returns The filtered result, or the original if config is incomplete.
 */
function tryFillHolesFilter(current: SourceResult, f: FilterConfig): SourceResult {
  // biome-ignore lint/nursery/noTernary: ternary is idiomatic for concise conditional returns
  return f.holeSize === undefined ? current : applyFillHolesFilter(current, f.holeSize);
}

/**
 * Map from filter type to its dispatcher function.
 */
const filterDispatchMap: Record<string, (current: SourceResult, f: FilterConfig) => SourceResult> =
  {
    shrink: tryShrinkFilter,
    tube: tryTubeFilter,
    clip: tryClipFilter,
    contour: tryContourFilter,
    fillHoles: tryFillHolesFilter,
  };

/**
 * Apply a chain of filters to a source.
 * @param sourceResult
 * @param filters
 * @returns The final {@link SourceResult} after all filters have been applied in sequence.
 */
function applyFilters(sourceResult: SourceResult, filters: FilterConfig[]): SourceResult {
  let current = sourceResult;
  for (const f of filters) {
    const dispatch = filterDispatchMap[f.type];
    if (dispatch) {
      current = dispatch(current, f);
    }
  }

  return current;
}

/**
 * Manual shrink filter — vtk.js does not provide vtkShrinkFilter.
 *
 * For each cell, duplicate its vertices and move them toward the cell centroid
 * by `shrinkFactor` (0 = collapse to centroid, 1 = no change).
 * @param sourceResult
 * @param shrinkFactor
 * @returns A {@link SourceResult} with each cell shrunk toward its centroid.
 */
// biome-ignore lint/complexity/noExcessiveLinesPerFunction: inline biome-ignore comments push it just over the limit
function applyShrinkFilter(sourceResult: SourceResult, shrinkFactor: number): SourceResult {
  const inputPd = getPolyData(sourceResult);
  const inPoints = inputPd.getPoints().getData();
  const polys = inputPd.getPolys().getData();
  if (polys.length === 0) {
    return sourceResult;
  }

  const resultPoints: number[] = [];
  const resultPolys: number[] = [];
  let offset = 0;
  let index = 0;
  while (index < polys.length) {
    const nVerts = at(polys, index);
    // biome-ignore lint/nursery/noIncrementDecrement: standard loop counter pattern
    index++;
    let cx = 0;
    let cy = 0;
    let cz = 0;
    const indices: number[] = [];
    // biome-ignore lint/nursery/noIncrementDecrement: standard loop counter pattern
    for (let index_ = 0; index_ < nVerts; index_++) {
      const vi = at(polys, index + index_);
      indices.push(vi);
      cx += at(inPoints, vi * XYZ_COMPONENTS);
      cy += at(inPoints, vi * XYZ_COMPONENTS + 1);
      cz += at(inPoints, vi * XYZ_COMPONENTS + 2);
    }

    cx /= nVerts;
    cy /= nVerts;
    cz /= nVerts;
    resultPolys.push(nVerts);
    // biome-ignore lint/nursery/noIncrementDecrement: standard loop counter pattern
    for (let k = 0; k < nVerts; k++) {
      const pi = indices[k] ?? 0;
      const px = at(inPoints, pi * XYZ_COMPONENTS);
      const py = at(inPoints, pi * XYZ_COMPONENTS + 1);
      const pz = at(inPoints, pi * XYZ_COMPONENTS + 2);
      resultPoints.push(
        cx + (px - cx) * shrinkFactor,
        cy + (py - cy) * shrinkFactor,
        cz + (pz - cz) * shrinkFactor,
      );
      resultPolys.push(offset + k);
    }

    offset += nVerts;
    index += nVerts;
  }

  // biome-ignore lint/correctness/noUndeclaredVariables: vtk globals are declared in vtk.d.ts
  const outputPd = vtk.Common.DataModel.vtkPolyData.newInstance();
  outputPd.getPoints().setData(new Float32Array(resultPoints), XYZ_COMPONENTS);
  outputPd.getPolys().setData(new Uint32Array(resultPolys));
  return { output: outputPd, isFilter: false };
}

/**
 * Apply a tube filter to thicken line geometry.
 * @param sourceResult
 * @param radius
 * @param numberOfSides
 * @returns A {@link SourceResult} with a tube filter applied to the line geometry.
 */
function applyTubeFilter(
  sourceResult: SourceResult,
  radius: number,
  numberOfSides: number,
): SourceResult {
  // biome-ignore lint/correctness/noUndeclaredVariables: vtk globals are declared in vtk.d.ts
  const tubeFilter = vtk.Filters.General.vtkTubeFilter.newInstance({
    radius,
    numberOfSides,
  });
  connectInput(tubeFilter, sourceResult);
  return { output: tubeFilter, isFilter: true };
}

/**
 * Clip geometry by a plane, using vtk.js if available or falling back to manual clipping.
 * @param sourceResult
 * @param normal
 * @param origin
 * @param invert
 * @returns A {@link SourceResult} with the clipped geometry.
 */
function applyClipFilter(
  sourceResult: SourceResult,
  normal: [number, number, number],
  origin: [number, number, number],
  invert: boolean,
): SourceResult {
  // biome-ignore lint/correctness/noUndeclaredVariables: vtk globals are declared in vtk.d.ts
  const plane = vtk.Common.DataModel.vtkPlane.newInstance();
  plane.setOrigin(origin[0], origin[1], origin[2]);
  plane.setNormal(normal[0], normal[1], normal[2]);

  // biome-ignore lint/correctness/noUndeclaredVariables: vtk globals are declared in vtk.d.ts
  const clipFactory = vtk.Filters.General.vtkClipClosedSurface;
  if (clipFactory) {
    const clipper = clipFactory.newInstance();
    clipper.setClippingPlanes?.([plane]);
    connectInput(clipper, sourceResult);
    return { output: clipper, isFilter: true };
  }

  return applyClipManual(sourceResult, normal, origin, invert);
}

/**
 * Manual clip fallback — discard cells whose centroid lies on the
 * wrong side of the clipping plane.
 * @param sourceResult
 * @param normal
 * @param origin
 * @param invert
 * @returns A {@link SourceResult} containing only the cells on the kept side of the plane.
 */
/** Clip plane definition for {@link applyClipManual}. */
interface ClipPlane {
  normal: [number, number, number];
  origin: [number, number, number];
  invert: boolean;
}

/**
 * Determine whether a cell centroid is on the kept side of a clip plane.
 * @param cellIndices
 * @param inPoints
 * @param plane
 * @returns True if the cell should be kept.
 */
function shouldKeepCell(cellIndices: number[], inPoints: Float32Array, plane: ClipPlane): boolean {
  const nVerts = cellIndices.length;
  let cx = 0;
  let cy = 0;
  let cz = 0;
  for (const vi of cellIndices) {
    cx += at(inPoints, vi * XYZ_COMPONENTS);
    cy += at(inPoints, vi * XYZ_COMPONENTS + 1);
    cz += at(inPoints, vi * XYZ_COMPONENTS + 2);
  }

  cx /= nVerts;
  cy /= nVerts;
  cz /= nVerts;
  const dot =
    (cx - plane.origin[0]) * plane.normal[0] +
    (cy - plane.origin[1]) * plane.normal[1] +
    (cz - plane.origin[2]) * plane.normal[2];
  // biome-ignore lint/nursery/noTernary: ternary is idiomatic for concise conditional returns
  return plane.invert ? dot >= 0 : dot <= 0;
}

/** Mutable state for collecting clipped geometry in {@link applyClipManual}. */
interface ClipState {
  inPoints: Float32Array;
  resultPoints: number[];
  resultPolys: number[];
  pointMap: Map<number, number>;
  nextIndex: number;
}

/**
 * Emit a kept cell into the clip state, deduplicating points via pointMap.
 * @param cellIndices
 * @param state
 */
function emitClippedCell(cellIndices: number[], state: ClipState): void {
  state.resultPolys.push(cellIndices.length);
  for (const pi of cellIndices) {
    if (!state.pointMap.has(pi)) {
      // biome-ignore lint/nursery/noIncrementDecrement: standard loop counter pattern
      state.pointMap.set(pi, state.nextIndex++);
      state.resultPoints.push(
        at(state.inPoints, pi * XYZ_COMPONENTS),
        at(state.inPoints, pi * XYZ_COMPONENTS + 1),
        at(state.inPoints, pi * XYZ_COMPONENTS + 2),
      );
    }

    state.resultPolys.push(state.pointMap.get(pi) ?? 0);
  }
}

/**
 * Manual clip filter — keep only cells whose centroid is on one side of a plane.
 * @param sourceResult
 * @param normal
 * @param origin
 * @param invert
 * @returns A {@link SourceResult} containing only the cells on the kept side of the plane.
 */
function applyClipManual(
  sourceResult: SourceResult,
  normal: [number, number, number],
  origin: [number, number, number],
  invert: boolean,
): SourceResult {
  const inputPd = getPolyData(sourceResult);
  const inPoints = inputPd.getPoints().getData();
  const polys = inputPd.getPolys().getData();
  if (polys.length === 0) {
    return sourceResult;
  }

  const plane: ClipPlane = { normal, origin, invert };
  const state: ClipState = {
    inPoints,
    resultPoints: [],
    resultPolys: [],
    pointMap: new Map<number, number>(),
    nextIndex: 0,
  };
  let index = 0;
  while (index < polys.length) {
    const nVerts = at(polys, index);
    // biome-ignore lint/nursery/noIncrementDecrement: standard loop counter pattern
    index++;
    const cellIndices: number[] = [];
    // biome-ignore lint/nursery/noIncrementDecrement: standard loop counter pattern
    for (let index_ = 0; index_ < nVerts; index_++) {
      cellIndices.push(at(polys, index + index_));
    }

    if (shouldKeepCell(cellIndices, inPoints, plane)) {
      emitClippedCell(cellIndices, state);
    }

    index += nVerts;
  }

  // biome-ignore lint/correctness/noUndeclaredVariables: vtk globals are declared in vtk.d.ts
  const outputPd = vtk.Common.DataModel.vtkPolyData.newInstance();
  outputPd.getPoints().setData(new Float32Array(state.resultPoints), XYZ_COMPONENTS);
  outputPd.getPolys().setData(new Uint32Array(state.resultPolys));
  return { output: outputPd, isFilter: false };
}

/**
 * Inject scalar data into PolyData and extract isocontour lines.
 * @param sourceResult
 * @param values
 * @param scalarName
 * @param scalarData
 * @returns A {@link SourceResult} containing the extracted isocontour lines.
 */
function applyContourFilter(
  sourceResult: SourceResult,
  values: number[],
  scalarName: string,
  scalarData: number[],
): SourceResult {
  const inputPd = getPolyData(sourceResult);

  // biome-ignore lint/correctness/noUndeclaredVariables: vtk globals are declared in vtk.d.ts
  const scalars = vtk.Common.Core.vtkDataArray.newInstance({
    numberOfComponents: 1,
    values: Float32Array.from(scalarData),
    name: scalarName,
  });
  inputPd.getPointData().addArray(scalars);
  inputPd.getPointData().setActiveScalars(scalarName);

  return applyContourManual(inputPd, values, scalarName);
}

/**
 * Collect the intersection points of a contour value along the edges of a triangle.
 * @param tri
 * @param value
 * @param inPoints
 * @returns Flat array of intersection coordinates (0 or 6 elements).
 */
function collectEdgeIntersections(
  tri: [number, number, number, number][],
  value: number,
  inPoints: Float32Array | Uint32Array,
): number[] {
  const edgePoints: number[] = [];
  for (const edge of tri) {
    const [ai, bi, sa, sb] = edge;
    if ((sa <= value && value < sb) || (sb <= value && value < sa)) {
      const t = (value - sa) / (sb - sa);
      edgePoints.push(
        at(inPoints, ai * XYZ_COMPONENTS) +
          t * (at(inPoints, bi * XYZ_COMPONENTS) - at(inPoints, ai * XYZ_COMPONENTS)),
        at(inPoints, ai * XYZ_COMPONENTS + 1) +
          t * (at(inPoints, bi * XYZ_COMPONENTS + 1) - at(inPoints, ai * XYZ_COMPONENTS + 1)),
        at(inPoints, ai * XYZ_COMPONENTS + 2) +
          t * (at(inPoints, bi * XYZ_COMPONENTS + 2) - at(inPoints, ai * XYZ_COMPONENTS + 2)),
      );
    }
  }

  return edgePoints;
}

/**
 * Manual marching-triangles contour extraction.
 *
 * For each triangle, linearly interpolate along edges to find intersection
 * points at each contour value and emit line segments.
 * @param inputPd
 * @param values
 * @param scalarName
 * @returns A {@link SourceResult} containing the marching-triangles contour line segments.
 */
/** Mutable state for collecting contour line segments. */
interface ContourState {
  polys: Uint32Array;
  scalarValues: Float32Array;
  inPoints: Float32Array;
  values: number[];
  outPoints: number[];
  outPolys: number[];
  pointIndex: number;
}

/**
 * Process a single triangle for contour extraction at all given values.
 * @param state
 * @param index
 */
function processContourTriangle(state: ContourState, index: number): void {
  const index0 = at(state.polys, index);
  const index1 = at(state.polys, index + 1);
  const index2 = at(state.polys, index + 2);
  const s0 = at(state.scalarValues, index0);
  const s1 = at(state.scalarValues, index1);
  const s2 = at(state.scalarValues, index2);
  const tri: [number, number, number, number][] = [
    [index0, index1, s0, s1],
    [index1, index2, s1, s2],
    [index2, index0, s2, s0],
  ];
  for (const value of state.values) {
    const edgePoints = collectEdgeIntersections(tri, value, state.inPoints);

    if (edgePoints.length === TWO_POINTS_XYZ) {
      state.outPoints.push(
        edgePoints[0] ?? 0,
        edgePoints[1] ?? 0,
        edgePoints[2] ?? 0,
        edgePoints[3] ?? 0,
        edgePoints[4] ?? 0,
        edgePoints[5] ?? 0,
      );
      state.outPolys.push(2, state.pointIndex, state.pointIndex + 1);
      state.pointIndex += 2;
    }
  }
}

/**
 * Marching-triangles contour extraction.
 *
 * For each triangle, linearly interpolate along edges to find intersection
 * points at each contour value and emit line segments.
 * @param inputPd
 * @param values
 * @param scalarName
 * @returns A {@link SourceResult} containing the marching-triangles contour line segments.
 */
function applyContourManual(
  inputPd: VtkPolyData,
  values: number[],
  scalarName: string,
): SourceResult {
  const inPoints = inputPd.getPoints().getData();
  const polys = inputPd.getPolys().getData();
  const scalarsArray = inputPd.getPointData().getArrayByName(scalarName);
  if (polys.length === 0 || !scalarsArray) {
    return { output: inputPd, isFilter: false };
  }

  const scalarValues = scalarsArray.getData();

  const state: ContourState = {
    polys,
    scalarValues,
    inPoints,
    values,
    outPoints: [],
    outPolys: [],
    pointIndex: 0,
  };

  let index = 0;
  while (index < polys.length) {
    const nVerts = at(polys, index);
    // biome-ignore lint/nursery/noIncrementDecrement: standard loop counter pattern
    index++;
    if (nVerts === TRIANGLE_VERTS) {
      processContourTriangle(state, index);
    }

    index += nVerts;
  }

  // biome-ignore lint/correctness/noUndeclaredVariables: vtk globals are declared in vtk.d.ts
  const outputPd = vtk.Common.DataModel.vtkPolyData.newInstance();
  if (state.outPoints.length > 0) {
    outputPd.getPoints().setData(new Float32Array(state.outPoints), XYZ_COMPONENTS);
    outputPd.getLines().setData(new Uint32Array(state.outPolys));
  }

  return { output: outputPd, isFilter: false };
}

/**
 * Build an adjacency map of boundary edges (edges shared by exactly one cell).
 * @param polys - The polygon connectivity array.
 * @returns A map from vertex index to its boundary-adjacent vertex indices.
 */
function buildBoundaryAdjacency(polys: Uint32Array): Map<number, number[]> {
  const edgeCount = new Map<string, number>();
  let index = 0;
  while (index < polys.length) {
    const nVerts = at(polys, index);
    // biome-ignore lint/nursery/noIncrementDecrement: standard loop counter pattern
    index++;
    // biome-ignore lint/nursery/noIncrementDecrement: standard loop counter pattern
    for (let k = 0; k < nVerts; k++) {
      const a = at(polys, index + k);
      const b = at(polys, index + ((k + 1) % nVerts));
      const key = `${String(Math.min(a, b))}_${String(Math.max(a, b))}`;
      edgeCount.set(key, (edgeCount.get(key) ?? 0) + 1);
    }

    index += nVerts;
  }

  const boundaryAdj = new Map<number, number[]>();
  for (const [key, count] of edgeCount) {
    if (count !== 1) {
      // biome-ignore lint/nursery/noContinue: early-skip in loop improves readability
      continue;
    }
    const parts = key.split("_");
    const a = Number(parts[0]);
    const b = Number(parts[1]);
    const adjA = boundaryAdj.get(a);
    if (adjA) {
      adjA.push(b);
    } else {
      boundaryAdj.set(a, [b]);
    }

    const adjB = boundaryAdj.get(b);
    if (adjB) {
      adjB.push(a);
    } else {
      boundaryAdj.set(b, [a]);
    }
  }

  return boundaryAdj;
}

/**
 * Walk a single boundary loop starting from a given node.
 * @param startNode
 * @param boundaryAdj
 * @param visited
 * @returns The loop as an array of vertex indices.
 */
function walkLoop(
  startNode: number,
  boundaryAdj: Map<number, number[]>,
  visited: Set<number>,
): number[] {
  const loop: number[] = [];
  let current = startNode;
  let previous = -1;
  let stuck = false;
  while (!stuck) {
    visited.add(current);
    loop.push(current);
    const neighbors = boundaryAdj.get(current) ?? [];
    let next = -1;
    for (const n of neighbors) {
      if (n !== previous && !visited.has(n)) {
        next = n;
        break;
      }
    }

    if (next === -1) {
      stuck = true;
    } else {
      previous = current;
      current = next;
    }
  }

  return loop;
}

/**
 * Trace closed loops from boundary adjacency.
 * @param boundaryAdj - Boundary adjacency map from {@link buildBoundaryAdjacency}.
 * @returns An array of loops, each being an array of vertex indices.
 */
function traceBoundaryLoops(boundaryAdj: Map<number, number[]>): number[][] {
  const visited = new Set<number>();
  const loops: number[][] = [];
  for (const startNode of boundaryAdj.keys()) {
    if (visited.has(startNode)) {
      // biome-ignore lint/nursery/noContinue: early-skip in loop improves readability
      continue;
    }
    const loop = walkLoop(startNode, boundaryAdj, visited);
    if (loop.length > 2) {
      loops.push(loop);
    }
  }

  return loops;
}

/**
 * Fill holes in a polygonal mesh by finding boundary edges, linking them
 * into loops, and fan-triangulating each loop whose perimeter is within
 * the given size threshold.
 *
 * This replicates the behaviour of the vtk.js FillHolesFilter example.
 * @param sourceResult
 * @param holeSize
 * @returns A {@link SourceResult} with holes filled.
 */
/**
 * Compute the perimeter of a boundary loop.
 * @param loop
 * @param inPoints
 * @returns The perimeter length.
 */
function computeLoopPerimeter(loop: number[], inPoints: Float32Array): number {
  let perimeter = 0;
  // biome-ignore lint/nursery/noIncrementDecrement: standard loop counter pattern
  for (let k = 0; k < loop.length; k++) {
    const a = loop[k] ?? 0;
    const b = loop[(k + 1) % loop.length] ?? 0;
    const dx = at(inPoints, b * XYZ_COMPONENTS) - at(inPoints, a * XYZ_COMPONENTS);
    const dy = at(inPoints, b * XYZ_COMPONENTS + 1) - at(inPoints, a * XYZ_COMPONENTS + 1);
    const dz = at(inPoints, b * XYZ_COMPONENTS + 2) - at(inPoints, a * XYZ_COMPONENTS + 2);
    perimeter += Math.hypot(dx, dy, dz);
  }

  return perimeter;
}

/**
 * Fan-triangulate a boundary loop into triangle polygons.
 * @param loop
 * @param newPolys
 */
function triangulateLoop(loop: number[], newPolys: number[]): void {
  const v0 = loop[0] ?? 0;
  // biome-ignore lint/nursery/noIncrementDecrement: standard loop counter pattern
  for (let k = 1; k < loop.length - 1; k++) {
    const v1 = loop[k] ?? 0;
    const v2 = loop[k + 1] ?? 0;
    newPolys.push(TRIANGLE_VERTS, v0, v1, v2);
  }
}

/**
 * Fill holes in a polygonal mesh by finding boundary edges, linking them
 * into loops, and fan-triangulating each loop whose perimeter is within
 * the given size threshold.
 * @param sourceResult
 * @param holeSize
 * @returns A {@link SourceResult} with holes filled.
 */
function applyFillHolesFilter(sourceResult: SourceResult, holeSize: number): SourceResult {
  const inputPd = getPolyData(sourceResult);
  const inPoints = inputPd.getPoints().getData();
  const polys = inputPd.getPolys().getData();
  if (polys.length === 0) {
    return sourceResult;
  }

  const boundaryAdj = buildBoundaryAdjacency(polys);
  if (boundaryAdj.size === 0) {
    return sourceResult;
  }

  const loops = traceBoundaryLoops(boundaryAdj);

  const newPolys: number[] = [];
  for (const loop of loops) {
    if (computeLoopPerimeter(loop, inPoints) <= holeSize) {
      triangulateLoop(loop, newPolys);
    }
  }

  if (newPolys.length === 0) {
    return sourceResult;
  }

  const mergedPolys = new Uint32Array([...polys, ...newPolys]);

  // biome-ignore lint/correctness/noUndeclaredVariables: vtk globals are declared in vtk.d.ts
  const outputPd = vtk.Common.DataModel.vtkPolyData.newInstance();
  outputPd.getPoints().setData(new Float32Array(inPoints), XYZ_COMPONENTS);
  outputPd.getPolys().setData(mergedPolys);
  return { output: outputPd, isFilter: false };
}
