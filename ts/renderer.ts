/**
 * pyvista-js renderer — reads scene configuration from JSON and creates
 * vtk.js objects.
 *
 * In JupyterLite, `_generate_render_js()` sets `__pvjsSceneData` and
 * `__pvjsContainer` before evaluating this code. In standalone HTML,
 * the scene data is read from the DOM.
 */

/** Access a typed array element, returning 0 for out-of-bounds. */
function at(array: Float32Array | Uint32Array, index: number): number {
  return array[index] ?? 0;
}

/** Wraps either a vtk.js algorithm (filter/source) or raw PolyData. */
interface SourceResult {
  output: VtkAlgorithm | VtkPolyData;
  isFilter: boolean;
}

/** Resolve a {@link SourceResult} to its underlying PolyData. */
function getPolyData(sourceResult: SourceResult): VtkPolyData {
  if (sourceResult.isFilter) {
    (sourceResult.output as VtkAlgorithm).update();
    return (sourceResult.output as VtkAlgorithm).getOutputData();
  }
  return sourceResult.output as VtkPolyData;
}

/** Wire `filter`'s input to the output of `sourceResult`. */
function connectInput(filter: VtkAlgorithm, sourceResult: SourceResult): void {
  if (sourceResult.isFilter) {
    filter.setInputConnection((sourceResult.output as VtkAlgorithm).getOutputPort());
  } else {
    filter.setInputData(sourceResult.output as VtkPolyData);
  }
}

const sceneData: SceneData =
  typeof __pvjsSceneData === "undefined"
    ? (JSON.parse(document.querySelector("#scene-data")?.textContent ?? "{}") as SceneData)
    : __pvjsSceneData;
const container: HTMLElement =
  typeof __pvjsContainer === "undefined"
    ? (document.querySelector<HTMLElement>(`#${CSS.escape(sceneData.containerId)}`) ??
      document.createElement("div"))
    : __pvjsContainer;
const bg = sceneData.background;

const renderer = vtk.Rendering.Core.vtkRenderer.newInstance();
renderer.setBackground(bg[0], bg[1], bg[2]);

const renderWindow = vtk.Rendering.Core.vtkRenderWindow.newInstance();
renderWindow.addRenderer(renderer);

const openGLRenderWindow = vtk.Rendering.OpenGL.vtkRenderWindow.newInstance();
renderWindow.addView(openGLRenderWindow);
openGLRenderWindow.setContainer(container);

const bbox = container.getBoundingClientRect();
openGLRenderWindow.setSize(bbox.width || 600, bbox.height || 400);

const interactor = vtk.Rendering.Core.vtkRenderWindowInteractor.newInstance();
const interactorStyle = vtk.Interaction.Style.vtkInteractorStyleTrackballCamera.newInstance();
interactor.setInteractorStyle(interactorStyle);
interactor.setView(openGLRenderWindow);
interactor.initialize();
interactor.bindEvents(container);

// eslint-disable-next-line unicorn/prefer-global-this -- Window augmentation requires window
window.renderer = renderer;
// eslint-disable-next-line unicorn/prefer-global-this
window.renderWindow = renderWindow;
// eslint-disable-next-line unicorn/prefer-global-this
window.openGLRenderWindow = openGLRenderWindow;
// eslint-disable-next-line unicorn/prefer-global-this
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

/** Add custom lights to the renderer, replacing the defaults. */
function setupLights(lightsConfig: LightConfig[], ren: VtkRenderer): void {
  if (lightsConfig.length === 0) {
    return;
  }
  ren.removeAllLights();
  ren.setAutomaticLightCreation(false);
  for (const cfg of lightsConfig) {
    const light = vtk.Rendering.Core.vtkLight.newInstance();
    const typeMap: Record<string, string> = {
      scene: "setLightTypeToSceneLight",
      camera: "setLightTypeToCameraLight",
      head: "setLightTypeToHeadLight",
    };
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

/** Lazily build the reader factory map to avoid accessing vtk.IO at module load time. */
function getReaderMap(): ReaderFactoryMap {
  return {
    plyReader: {
      factory: vtk.IO.Geometry.vtkPLYReader,
      parseMethod: "parseAsArrayBuffer",
    },
    stlReader: {
      factory: vtk.IO.Geometry.vtkSTLReader,
      parseMethod: "parseAsArrayBuffer",
    },
    objReader: {
      factory: vtk.IO.Misc.vtkOBJReader,
      parseMethod: "parseAsText",
    },
    vtkReader: {
      factory: vtk.IO.Legacy.vtkPolyDataReader,
      parseMethod: "parseAsText",
    },
  };
}

/** Dispatch to the appropriate source factory based on `cfg.type`. */
function createSource(cfg: SourceConfig): SourceResult | undefined {
  switch (cfg.type) {
    case "sphere": {
      return createSphereSource(cfg);
    }
    case "cone": {
      return createConeSource(cfg);
    }
    case "cube": {
      return createCubeSource(cfg);
    }
    case "cylinder": {
      return createCylinderSource(cfg);
    }
    case "disk": {
      return createDiskSource(cfg);
    }
    case "circle": {
      return createCircleSource(cfg);
    }
    case "arrow": {
      return createArrowSource(cfg);
    }
    case "line": {
      return createLineSource(cfg);
    }
    case "plane": {
      return createPlaneSource(cfg);
    }
    case "mesh": {
      return createMeshSource(cfg);
    }
    case "points": {
      return createPointsSource(cfg);
    }
    case "plyReader":
    case "stlReader":
    case "objReader":
    case "vtkReader": {
      return createReaderSource(cfg);
    }
    default: {
      console.error("Unknown source type:", cfg.type);
      return undefined;
    }
  }
}

/** Create a sphere source with texture-map-to-sphere applied. */
function createSphereSource(cfg: SourceConfig): SourceResult {
  const source = vtk.Filters.Sources.vtkSphereSource.newInstance({
    center: cfg.center,
    radius: cfg.radius,
    thetaResolution: cfg.thetaResolution,
    phiResolution: cfg.phiResolution,
  });
  const texMap = vtk.Filters.Texture.vtkTextureMapToSphere.newInstance();
  texMap.setInputConnection(source.getOutputPort());
  return { output: texMap, isFilter: true };
}

/** Create a cone source. */
function createConeSource(cfg: SourceConfig): SourceResult {
  const source = vtk.Filters.Sources.vtkConeSource.newInstance({
    height: cfg.height,
    radius: cfg.radius,
    resolution: cfg.resolution,
  });
  return { output: source, isFilter: true };
}

/** Create a cube source. */
function createCubeSource(cfg: SourceConfig): SourceResult {
  const source = vtk.Filters.Sources.vtkCubeSource.newInstance({
    xLength: cfg.xLength,
    yLength: cfg.yLength,
    zLength: cfg.zLength,
  });
  return { output: source, isFilter: false };
}

/** Create a cylinder source. */
function createCylinderSource(cfg: SourceConfig): SourceResult {
  const source = vtk.Filters.Sources.vtkCylinderSource.newInstance({
    height: cfg.height,
    radius: cfg.radius,
    resolution: cfg.resolution,
  });
  return { output: source, isFilter: true };
}

/** Create a disk source, falling back to empty PolyData if unavailable. */
function createDiskSource(cfg: SourceConfig): SourceResult {
  const diskFactory = vtk.Filters.Sources.vtkDiskSource;
  const source = diskFactory
    ? diskFactory.newInstance({
        innerRadius: cfg.innerRadius,
        outerRadius: cfg.outerRadius,
        radialResolution: 1,
        circumferentialResolution: cfg.resolution,
      })
    : undefined;
  return {
    output: source ?? vtk.Common.DataModel.vtkPolyData.newInstance(),
    isFilter: true,
  };
}

/** Create a circle source (disk with `innerRadius=0`). */
function createCircleSource(cfg: SourceConfig): SourceResult {
  return createDiskSource({
    type: "disk",
    innerRadius: 0,
    outerRadius: cfg.radius ?? 1,
    resolution: cfg.resolution ?? 50,
  });
}

/** Create an arrow source. */
function createArrowSource(cfg: SourceConfig): SourceResult {
  const source = vtk.Filters.Sources.vtkArrowSource.newInstance({
    tipLength: cfg.tipLength,
    tipRadius: cfg.tipRadius,
    shaftRadius: cfg.shaftRadius,
  });
  return { output: source, isFilter: true };
}

/** Create a line source between two points. */
function createLineSource(cfg: SourceConfig): SourceResult {
  const source = vtk.Filters.Sources.vtkLineSource.newInstance({
    point1: cfg.point1,
    point2: cfg.point2,
  });
  return { output: source, isFilter: true };
}

/** Create a plane source with optional normal. */
function createPlaneSource(cfg: SourceConfig): SourceResult {
  const source = vtk.Filters.Sources.vtkPlaneSource.newInstance({
    origin: cfg.origin,
  });
  if (cfg.normal) {
    source.setNormal?.(cfg.normal[0], cfg.normal[1], cfg.normal[2]);
  }
  return { output: source, isFilter: true };
}

/** Create PolyData from raw point and polygon arrays. */
function createMeshSource(cfg: SourceConfig): SourceResult {
  const polydata = vtk.Common.DataModel.vtkPolyData.newInstance();
  const pointsArray = Float32Array.from(cfg.points ?? []);
  const vtkPts = vtk.Common.Core.vtkPoints.newInstance();
  vtkPts.setData(pointsArray, 3);
  polydata.setPoints(vtkPts);
  if (cfg.polys) {
    const polysArray = Uint32Array.from(cfg.polys);
    polydata.getPolys().setData(polysArray);
  }
  return { output: polydata, isFilter: false };
}

/** Create a point cloud PolyData from raw point arrays. */
function createPointsSource(cfg: SourceConfig): SourceResult {
  const polydata = vtk.Common.DataModel.vtkPolyData.newInstance();
  const pointsArray = Float32Array.from(cfg.points ?? []);
  const vtkPts = vtk.Common.Core.vtkPoints.newInstance();
  vtkPts.setData(pointsArray, 3);
  polydata.setPoints(vtkPts);
  return { output: polydata, isFilter: false };
}

/** Decode base64-encoded file data and parse it with the appropriate vtk.js reader. */
function createReaderSource(cfg: SourceConfig): SourceResult {
  const entry = getReaderMap()[cfg.type] as
    | { factory: VtkReaderFactory; parseMethod: "parseAsArrayBuffer" | "parseAsText" }
    | undefined;
  if (!entry) {
    throw new Error(`Unknown reader type: ${cfg.type}`);
  }
  const binary = atob(cfg.data ?? "");
  const bytes = new Uint8Array(binary.length);
  for (let index = 0; index < binary.length; index++) {
    bytes[index] = binary.codePointAt(index) ?? 0;
  }
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

/** Inject per-point scalar/vector data arrays into PolyData. */
function injectPointData(
  polydata: VtkPolyData,
  pointDataArrays: PointDataArray[] | undefined,
): void {
  if (!pointDataArrays) {
    return;
  }
  for (const array of pointDataArrays) {
    const dataArray = vtk.Common.Core.vtkDataArray.newInstance({
      numberOfComponents: array.numberOfComponents,
      values: Float32Array.from(array.values),
      name: array.name,
    });
    polydata.getPointData().addArray(dataArray);
  }
}

/** Inject 2-component texture coordinates into PolyData. */
function injectTCoords(polydata: VtkPolyData, tCoords: number[] | undefined): void {
  if (!tCoords) {
    return;
  }
  const tcArray = vtk.Common.Core.vtkDataArray.newInstance({
    numberOfComponents: 2,
    values: Float32Array.from(tCoords),
    name: "TextureCoordinates",
  });
  polydata.getPointData().setTCoords(tcArray);
}

/** Optionally insert a normals-computation filter between source and mapper. */
function setupNormals(
  sourceResult: SourceResult,
  normalsConfig: NormalsConfig | undefined,
): SourceResult {
  if (!normalsConfig) {
    return sourceResult;
  }
  const normals = vtk.Filters.Core.vtkPolyDataNormals.newInstance();
  normals.setComputePointNormals?.(normalsConfig.computePointNormals);
  normals.setComputeCellNormals?.(normalsConfig.computeCellNormals);
  connectInput(normals, sourceResult);
  return { output: normals, isFilter: true };
}

/** Build a complete vtk.js actor from an {@link ActorConfig} and add it to the renderer. */
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
    injectTCoords(pd, cfg.source.tCoords);
  }

  let currentResult = sourceResult;
  if (cfg.source.filters && cfg.source.filters.length > 0) {
    currentResult = applyFilters(sourceResult, cfg.source.filters);
  }

  const mapperInput = setupNormals(currentResult, cfg.normals);

  const MapperClass =
    cfg.actorType === "points" && cfg.renderPointsAsSpheres
      ? vtk.Rendering.Core.vtkSphereMapper
      : vtk.Rendering.Core.vtkMapper;
  const mapper = MapperClass.newInstance();
  if (mapperInput.isFilter) {
    mapper.setInputConnection((mapperInput.output as VtkAlgorithm).getOutputPort());
  } else {
    mapper.setInputData(mapperInput.output as VtkPolyData);
  }

  const actor = vtk.Rendering.Core.vtkActor.newInstance();
  actor.setMapper(mapper);
  actor.getProperty().setColor(cfg.color[0], cfg.color[1], cfg.color[2]);
  actor.getProperty().setOpacity(cfg.opacity);

  const styleMap: Record<string, number> = {
    surface: 2,
    wireframe: 1,
    points: 0,
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

  if (cfg.pbr) {
    actor.getProperty().setInterpolationToPhong();
    const m = cfg.pbr.metallic;
    const r = cfg.pbr.roughness;
    actor.getProperty().setMetallic(m);
    actor.getProperty().setRoughness(r);
    actor.getProperty().setAmbient(0.1);
    actor.getProperty().setSpecular(0.75 * m + 0.25);
    actor.getProperty().setSpecularPower(Math.max(1, 100 * (1 - r)));
    actor.getProperty().setDiffuse(0.65 + 0.35 * (1 - m));
  }

  if (cfg.actorType === "points") {
    if (cfg.renderPointsAsSpheres && mapper.setRadius) {
      mapper.setRadius((cfg.pointSize ?? 5) * 0.01);
    } else {
      actor.getProperty().setPointSize(cfg.pointSize ?? 5);
      actor.getProperty().setRepresentationToPoints();
    }
  }

  if (cfg.texture) {
    const texture = vtk.Rendering.Core.vtkTexture.newInstance();
    texture.setInterpolate(true);
    actor.addTexture(texture);
    const img = new Image();
    img.crossOrigin = "anonymous";
    img.addEventListener("load", () => {
      texture.setImage(img);
      renWin.render();
    });
    img.src = cfg.texture.url;
  }

  ren.addActor(actor);
}

/** Apply camera settings from the scene configuration. */
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

/** Add an orientation-marker axes widget to the bottom-left corner. */
function setupAxes(interactorObject: VtkInteractor): void {
  const axes = vtk.Rendering.Core.vtkAxesActor.newInstance();
  const orientationWidget = vtk.Interaction.Widgets.vtkOrientationMarkerWidget.newInstance({
    actor: axes,
    interactor: interactorObject,
  });
  orientationWidget.setEnabled(true);
  orientationWidget.setViewportCorner(
    vtk.Interaction.Widgets.vtkOrientationMarkerWidget.Corners.BOTTOM_LEFT,
  );
  orientationWidget.setViewportSize(0.15);
  orientationWidget.setMinPixelSize(100);
  orientationWidget.setMaxPixelSize(300);
}

/** Create an absolutely-positioned HTML overlay for 2D text. */
function setupTextActor(cfg: TextActorConfig, containerElement: HTMLElement): void {
  const div = document.createElement("div");
  div.textContent = cfg.text;
  div.style.position = "absolute";
  div.style.left = `${String(cfg.position[0] * 100)}%`;
  div.style.bottom = `${String(cfg.position[1] * 100)}%`;
  const r = Math.round(cfg.color[0] * 255);
  const g = Math.round(cfg.color[1] * 255);
  const b = Math.round(cfg.color[2] * 255);
  div.style.color = `rgba(${String(r)},${String(g)},${String(b)},${String(cfg.opacity)})`;
  div.style.fontSize = `${String(cfg.fontSize)}px`;
  div.style.fontWeight = cfg.bold ? "bold" : "normal";
  div.style.fontStyle = cfg.italic ? "italic" : "normal";
  div.style.pointerEvents = "none";
  div.style.zIndex = "10";
  div.style.whiteSpace = "pre";
  div.style.textShadow = "1px 1px 2px rgba(0,0,0,0.8), -1px -1px 2px rgba(0,0,0,0.8)";
  containerElement.append(div);
}

/** Apply a chain of filters (shrink, tube, clip, contour) to a source. */
function applyFilters(sourceResult: SourceResult, filters: FilterConfig[]): SourceResult {
  let current = sourceResult;
  for (const f of filters) {
    if (f.type === "shrink" && f.shrinkFactor !== undefined) {
      current = applyShrinkFilter(current, f.shrinkFactor);
    } else if (f.type === "tube" && f.radius !== undefined && f.numberOfSides !== undefined) {
      current = applyTubeFilter(current, f.radius, f.numberOfSides);
    } else if (f.type === "clip" && f.normal && f.origin && f.invert !== undefined) {
      current = applyClipFilter(current, f.normal, f.origin, f.invert);
    } else if (f.type === "contour" && f.values && f.scalarName && f.scalarData) {
      current = applyContourFilter(current, f.values, f.scalarName, f.scalarData);
    }
  }
  return current;
}

/**
 * Manual shrink filter — vtk.js does not provide vtkShrinkFilter.
 *
 * For each cell, duplicate its vertices and move them toward the cell centroid
 * by `shrinkFactor` (0 = collapse to centroid, 1 = no change).
 */
function applyShrinkFilter(sourceResult: SourceResult, shrinkFactor: number): SourceResult {
  const inputPD = getPolyData(sourceResult);
  const inPoints = inputPD.getPoints().getData();
  const polys = inputPD.getPolys().getData();
  if (polys.length === 0) {
    return sourceResult;
  }

  const resultPoints: number[] = [];
  const resultPolys: number[] = [];
  let offset = 0;
  let index = 0;
  while (index < polys.length) {
    const nVerts = at(polys, index);
    index++;
    let cx = 0,
      cy = 0,
      cz = 0;
    const indices: number[] = [];
    for (let index_ = 0; index_ < nVerts; index_++) {
      const vi = at(polys, index + index_);
      indices.push(vi);
      cx += at(inPoints, vi * 3);
      cy += at(inPoints, vi * 3 + 1);
      cz += at(inPoints, vi * 3 + 2);
    }
    cx /= nVerts;
    cy /= nVerts;
    cz /= nVerts;
    resultPolys.push(nVerts);
    for (let k = 0; k < nVerts; k++) {
      const pi = indices[k] ?? 0;
      const px = at(inPoints, pi * 3);
      const py = at(inPoints, pi * 3 + 1);
      const pz = at(inPoints, pi * 3 + 2);
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

  const outputPD = vtk.Common.DataModel.vtkPolyData.newInstance();
  outputPD.getPoints().setData(new Float32Array(resultPoints), 3);
  outputPD.getPolys().setData(new Uint32Array(resultPolys));
  return { output: outputPD, isFilter: false };
}

/** Apply a tube filter to thicken line geometry. */
function applyTubeFilter(
  sourceResult: SourceResult,
  radius: number,
  numberOfSides: number,
): SourceResult {
  const tubeFilter = vtk.Filters.General.vtkTubeFilter.newInstance({
    radius,
    numberOfSides,
  });
  connectInput(tubeFilter, sourceResult);
  return { output: tubeFilter, isFilter: true };
}

/** Clip geometry by a plane, using vtk.js if available or falling back to manual clipping. */
function applyClipFilter(
  sourceResult: SourceResult,
  normal: [number, number, number],
  origin: [number, number, number],
  invert: boolean,
): SourceResult {
  const plane = vtk.Common.DataModel.vtkPlane.newInstance();
  plane.setOrigin(origin[0], origin[1], origin[2]);
  plane.setNormal(normal[0], normal[1], normal[2]);

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
 */
function applyClipManual(
  sourceResult: SourceResult,
  normal: [number, number, number],
  origin: [number, number, number],
  invert: boolean,
): SourceResult {
  const inputPD = getPolyData(sourceResult);
  const inPoints = inputPD.getPoints().getData();
  const polys = inputPD.getPolys().getData();
  if (polys.length === 0) {
    return sourceResult;
  }
  const [nx, ny, nz] = normal;
  const [ox, oy, oz] = origin;

  const resultPoints: number[] = [];
  const resultPolys: number[] = [];
  const pointMap = new Map<number, number>();
  let nextIndex = 0;
  let index = 0;
  while (index < polys.length) {
    const nVerts = at(polys, index);
    index++;
    let cx = 0,
      cy = 0,
      cz = 0;
    const cellIndices: number[] = [];
    for (let index_ = 0; index_ < nVerts; index_++) {
      const vi = at(polys, index + index_);
      cellIndices.push(vi);
      cx += at(inPoints, vi * 3);
      cy += at(inPoints, vi * 3 + 1);
      cz += at(inPoints, vi * 3 + 2);
    }
    cx /= nVerts;
    cy /= nVerts;
    cz /= nVerts;
    const dot = (cx - ox) * nx + (cy - oy) * ny + (cz - oz) * nz;
    const keep = invert ? dot >= 0 : dot <= 0;
    if (keep) {
      resultPolys.push(nVerts);
      for (let k = 0; k < nVerts; k++) {
        const pi = cellIndices[k] ?? 0;
        if (!pointMap.has(pi)) {
          pointMap.set(pi, nextIndex++);
          resultPoints.push(
            at(inPoints, pi * 3),
            at(inPoints, pi * 3 + 1),
            at(inPoints, pi * 3 + 2),
          );
        }
        resultPolys.push(pointMap.get(pi) ?? 0);
      }
    }
    index += nVerts;
  }

  const outputPD = vtk.Common.DataModel.vtkPolyData.newInstance();
  outputPD.getPoints().setData(new Float32Array(resultPoints), 3);
  outputPD.getPolys().setData(new Uint32Array(resultPolys));
  return { output: outputPD, isFilter: false };
}

/** Inject scalar data into PolyData and extract isocontour lines. */
function applyContourFilter(
  sourceResult: SourceResult,
  values: number[],
  scalarName: string,
  scalarData: number[],
): SourceResult {
  const inputPD = getPolyData(sourceResult);

  const scalars = vtk.Common.Core.vtkDataArray.newInstance({
    numberOfComponents: 1,
    values: Float32Array.from(scalarData),
    name: scalarName,
  });
  inputPD.getPointData().addArray(scalars);
  inputPD.getPointData().setActiveScalars(scalarName);

  return applyContourManual(inputPD, values, scalarName);
}

/**
 * Manual marching-triangles contour extraction.
 *
 * For each triangle, linearly interpolate along edges to find intersection
 * points at each contour value and emit line segments.
 */
function applyContourManual(
  inputPD: VtkPolyData,
  values: number[],
  scalarName: string,
): SourceResult {
  const inPoints = inputPD.getPoints().getData();
  const polys = inputPD.getPolys().getData();
  const scalarsArray = inputPD.getPointData().getArrayByName(scalarName);
  if (polys.length === 0 || !scalarsArray) {
    return { output: inputPD, isFilter: false };
  }
  const scalarValues = scalarsArray.getData();

  const outPoints: number[] = [];
  const outPolys: number[] = [];
  let pointIndex = 0;

  let index = 0;
  while (index < polys.length) {
    const nVerts = at(polys, index);
    index++;
    if (nVerts === 3) {
      const index0 = at(polys, index),
        index1 = at(polys, index + 1),
        index2 = at(polys, index + 2);
      const s0 = at(scalarValues, index0),
        s1 = at(scalarValues, index1),
        s2 = at(scalarValues, index2);
      const tri: [number, number, number, number][] = [
        [index0, index1, s0, s1],
        [index1, index2, s1, s2],
        [index2, index0, s2, s0],
      ];
      for (const value of values) {
        const edgePoints: number[] = [];
        for (const edge of tri) {
          const [ai, bi, sa, sb] = edge;
          if ((sa <= value && value < sb) || (sb <= value && value < sa)) {
            const t = (value - sa) / (sb - sa);
            edgePoints.push(
              at(inPoints, ai * 3) + t * (at(inPoints, bi * 3) - at(inPoints, ai * 3)),
              at(inPoints, ai * 3 + 1) + t * (at(inPoints, bi * 3 + 1) - at(inPoints, ai * 3 + 1)),
              at(inPoints, ai * 3 + 2) + t * (at(inPoints, bi * 3 + 2) - at(inPoints, ai * 3 + 2)),
            );
          }
        }
        if (edgePoints.length === 6) {
          outPoints.push(
            edgePoints[0] ?? 0,
            edgePoints[1] ?? 0,
            edgePoints[2] ?? 0,
            edgePoints[3] ?? 0,
            edgePoints[4] ?? 0,
            edgePoints[5] ?? 0,
          );
          outPolys.push(2, pointIndex, pointIndex + 1);
          pointIndex += 2;
        }
      }
    }
    index += nVerts;
  }

  const outputPD = vtk.Common.DataModel.vtkPolyData.newInstance();
  if (outPoints.length > 0) {
    outputPD.getPoints().setData(new Float32Array(outPoints), 3);
    outputPD.getLines().setData(new Uint32Array(outPolys));
  }
  return { output: outputPD, isFilter: false };
}
