import type {
  ActorConfig,
  CameraConfig,
  FilterConfig,
  LightConfig,
  NormalsConfig,
  PbrConfig,
  PointDataArray,
  SceneData,
  SourceConfig,
  TextActorConfig,
  TextureConfig,
} from "./types";

// Constants — mirror pyvista-js/ts/renderer.ts
const XYZ_COMPONENTS = 3;
const UV_COMPONENTS = 2;
const DEFAULT_WIDTH = 600;
const DEFAULT_HEIGHT = 400;
const COLOR_BYTE_SCALE = 255;
const PERCENT = 100;
const DEFAULT_RADIUS = 1;
const DEFAULT_RESOLUTION = 50;
const POINT_SPHERE_RADIUS_SCALE = 0.01;
const DEFAULT_POINT_SIZE = 5;
const PBR_AMBIENT = 0.1;
const PBR_SPECULAR_METALLIC_WEIGHT = 0.75;
const PBR_SPECULAR_BASE = 0.25;
const PBR_SPECULAR_POWER_SCALE = 100;
const PBR_DIFFUSE_BASE = 0.65;
const PBR_DIFFUSE_METALLIC_WEIGHT = 0.35;
const AXES_VIEWPORT_SIZE = 0.15;
const AXES_MIN_PIXEL_SIZE = 100;
const AXES_MAX_PIXEL_SIZE = 300;
const DISK_RADIAL_RESOLUTION = 1;
const TRIANGLE_VERTS = 3;
const TWO_POINTS_XYZ = 6;
const VTK_REPRESENTATION_SURFACE = 2;
const VTK_REPRESENTATION_WIREFRAME = 1;
const VTK_REPRESENTATION_POINTS = 0;

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type AnyVtk = any;

function getVtk(): AnyVtk {
  return (window as unknown as { vtk: AnyVtk }).vtk;
}

function at(array: Float32Array | Uint32Array, index: number): number {
  return array[index] ?? 0;
}

interface SourceResult {
  output: AnyVtk;
  isFilter: boolean;
}

function getPolyData(sourceResult: SourceResult): AnyVtk {
  if (sourceResult.isFilter) {
    sourceResult.output.update();
    return sourceResult.output.getOutputData();
  }
  return sourceResult.output;
}

function connectInput(filter: AnyVtk, sourceResult: SourceResult): void {
  if (sourceResult.isFilter) {
    filter.setInputConnection(sourceResult.output.getOutputPort());
  } else {
    filter.setInputData(sourceResult.output);
  }
}

/**
 * PyVistaRenderer renders a pyvista-js SceneData object using vtk.js.
 * vtk.js must already be loaded as a CDN global (window.vtk) before
 * constructing this class. Use loadVtkJs() to ensure it is ready.
 */
export class PyVistaRenderer {
  private _renderer: AnyVtk;
  private _renderWindow: AnyVtk;
  private _openGlRenderWindow: AnyVtk;
  private _interactor: AnyVtk;
  private _container: HTMLElement;

  constructor(container: HTMLElement, sceneData: SceneData) {
    this._container = container;
    const vtk = getVtk();

    this._renderer = vtk.Rendering.Core.vtkRenderer.newInstance();
    const bg = sceneData.background;
    this._renderer.setBackground(bg[0], bg[1], bg[2]);

    this._renderWindow = vtk.Rendering.Core.vtkRenderWindow.newInstance();
    this._renderWindow.addRenderer(this._renderer);

    this._openGlRenderWindow = vtk.Rendering.OpenGL.vtkRenderWindow.newInstance();
    this._renderWindow.addView(this._openGlRenderWindow);
    this._openGlRenderWindow.setContainer(container);

    const bbox = container.getBoundingClientRect();
    this._openGlRenderWindow.setSize(bbox.width || DEFAULT_WIDTH, bbox.height || DEFAULT_HEIGHT);

    const interactorStyle = vtk.Interaction.Style.vtkInteractorStyleTrackballCamera.newInstance();
    this._interactor = vtk.Rendering.Core.vtkRenderWindowInteractor.newInstance();
    this._interactor.setInteractorStyle(interactorStyle);
    this._interactor.setView(this._openGlRenderWindow);
    this._interactor.initialize();
    this._interactor.bindEvents(container);

    if (sceneData.lightingMode === null && sceneData.lights.length === 0) {
      this._renderer.removeAllLights();
      this._renderer.setAutomaticLightCreation(false);
    } else {
      this._setupLights(sceneData.lights);
    }

    for (const [index, actorConfig] of sceneData.actors.entries()) {
      this._setupActor(actorConfig, index);
    }

    if (sceneData.textActors) {
      for (const textConfig of sceneData.textActors) {
        this._setupTextActor(textConfig);
      }
    }

    if (sceneData.axes) {
      this._setupAxes();
    }

    this._renderer.resetCamera();
    if (sceneData.camera) {
      this._setupCamera(sceneData.camera);
    }

    this._renderWindow.render();
  }

  destroy(): void {
    try {
      this._interactor.unbindEvents?.(this._container);
    } catch {
      // ignore — not all vtk.js versions expose unbindEvents
    }
    const canvas = this._container.querySelector("canvas");
    canvas?.remove();
  }

  private _setupLights(lights: LightConfig[]): void {
    if (lights.length === 0) return;
    const vtk = getVtk();
    this._renderer.removeAllLights();
    this._renderer.setAutomaticLightCreation(false);
    const typeMap: Record<string, string> = {
      scene: "setLightTypeToSceneLight",
      camera: "setLightTypeToCameraLight",
      head: "setLightTypeToHeadLight",
    };
    for (const cfg of lights) {
      const light = vtk.Rendering.Core.vtkLight.newInstance();
      const setter = typeMap[cfg.type] ?? "setLightTypeToSceneLight";
      const setterFn = light[setter];
      if (typeof setterFn === "function") {
        (setterFn as () => void).call(light);
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
      this._renderer.addLight(light);
    }
  }

  private _createSource(cfg: SourceConfig): SourceResult | undefined {
    const vtk = getVtk();
    switch (cfg.type) {
      case "sphere":
        return this._createSphereSource(cfg);
      case "cone":
        return {
          output: vtk.Filters.Sources.vtkConeSource.newInstance({
            height: cfg.height,
            radius: cfg.radius,
            resolution: cfg.resolution,
          }),
          isFilter: true,
        };
      case "cube":
        return {
          output: vtk.Filters.Sources.vtkCubeSource.newInstance({
            xLength: cfg.xLength,
            yLength: cfg.yLength,
            zLength: cfg.zLength,
          }),
          isFilter: false,
        };
      case "cylinder":
        return {
          output: vtk.Filters.Sources.vtkCylinderSource.newInstance({
            height: cfg.height,
            radius: cfg.radius,
            resolution: cfg.resolution,
          }),
          isFilter: true,
        };
      case "disk":
        return this._createDiskSource(cfg);
      case "circle":
        return this._createDiskSource({
          type: "disk",
          innerRadius: 0,
          outerRadius: cfg.radius ?? DEFAULT_RADIUS,
          resolution: cfg.resolution ?? DEFAULT_RESOLUTION,
        });
      case "arrow":
        return {
          output: vtk.Filters.Sources.vtkArrowSource.newInstance({
            tipLength: cfg.tipLength,
            tipRadius: cfg.tipRadius,
            shaftRadius: cfg.shaftRadius,
          }),
          isFilter: true,
        };
      case "line":
        return {
          output: vtk.Filters.Sources.vtkLineSource.newInstance({
            point1: cfg.point1,
            point2: cfg.point2,
          }),
          isFilter: true,
        };
      case "plane": {
        const source = vtk.Filters.Sources.vtkPlaneSource.newInstance({
          origin: cfg.origin,
        });
        if (cfg.normal) {
          source.setNormal?.(cfg.normal[0], cfg.normal[1], cfg.normal[2]);
        }
        return { output: source, isFilter: true };
      }
      case "mesh":
        return this._createMeshSource(cfg);
      case "points":
        return this._createPointsSource(cfg);
      case "plyReader":
      case "stlReader":
      case "objReader":
      case "vtkReader":
        return this._createReaderSource(cfg);
      default:
        return;
    }
  }

  private _createSphereSource(cfg: SourceConfig): SourceResult {
    const vtk = getVtk();
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

  private _createDiskSource(cfg: SourceConfig): SourceResult {
    const vtk = getVtk();
    const diskFactory = vtk.Filters.Sources.vtkDiskSource;
    const source = diskFactory
      ? diskFactory.newInstance({
          innerRadius: cfg.innerRadius,
          outerRadius: cfg.outerRadius,
          radialResolution: DISK_RADIAL_RESOLUTION,
          circumferentialResolution: cfg.resolution,
        })
      : undefined;
    return {
      output: source ?? vtk.Common.DataModel.vtkPolyData.newInstance(),
      isFilter: true,
    };
  }

  private _createMeshSource(cfg: SourceConfig): SourceResult {
    const vtk = getVtk();
    const polydata = vtk.Common.DataModel.vtkPolyData.newInstance();
    const pointsArray = Float32Array.from(cfg.points ?? []);
    const vtkPts = vtk.Common.Core.vtkPoints.newInstance();
    vtkPts.setData(pointsArray, XYZ_COMPONENTS);
    polydata.setPoints(vtkPts);
    if (cfg.polys) {
      polydata.getPolys().setData(Uint32Array.from(cfg.polys));
    }
    return { output: polydata, isFilter: false };
  }

  private _createPointsSource(cfg: SourceConfig): SourceResult {
    const vtk = getVtk();
    const polydata = vtk.Common.DataModel.vtkPolyData.newInstance();
    const pointsArray = Float32Array.from(cfg.points ?? []);
    const vtkPts = vtk.Common.Core.vtkPoints.newInstance();
    vtkPts.setData(pointsArray, XYZ_COMPONENTS);
    polydata.setPoints(vtkPts);
    return { output: polydata, isFilter: false };
  }

  private _createReaderSource(cfg: SourceConfig): SourceResult {
    const vtk = getVtk();
    const readerMap: Record<string, { factory: AnyVtk; parseMethod: string }> = {
      plyReader: { factory: vtk.IO.Geometry.vtkPLYReader, parseMethod: "parseAsArrayBuffer" },
      stlReader: { factory: vtk.IO.Geometry.vtkSTLReader, parseMethod: "parseAsArrayBuffer" },
      objReader: { factory: vtk.IO.Misc.vtkOBJReader, parseMethod: "parseAsText" },
      vtkReader: { factory: vtk.IO.Legacy.vtkPolyDataReader, parseMethod: "parseAsText" },
    };
    const entry = readerMap[cfg.type];
    if (!entry) throw new Error(`Unknown reader type: ${cfg.type}`);
    const bytes = Uint8Array.from(atob(cfg.data ?? ""), (char) => char.codePointAt(0) ?? 0);
    const reader = entry.factory.newInstance();
    if (entry.parseMethod === "parseAsText") {
      reader.parseAsText(new TextDecoder().decode(bytes));
    } else {
      reader.parseAsArrayBuffer(new Uint8Array(bytes).buffer);
    }
    return { output: reader, isFilter: true };
  }

  private _injectPointData(polydata: AnyVtk, pointDataArrays: PointDataArray[] | undefined): void {
    if (!pointDataArrays) return;
    const vtk = getVtk();
    for (const array of pointDataArrays) {
      const dataArray = vtk.Common.Core.vtkDataArray.newInstance({
        numberOfComponents: array.numberOfComponents,
        values: Float32Array.from(array.values),
        name: array.name,
      });
      polydata.getPointData().addArray(dataArray);
    }
  }

  private _injectTcoords(polydata: AnyVtk, tCoords: number[] | undefined): void {
    if (!tCoords) return;
    const vtk = getVtk();
    const tcArray = vtk.Common.Core.vtkDataArray.newInstance({
      numberOfComponents: UV_COMPONENTS,
      values: Float32Array.from(tCoords),
      name: "TextureCoordinates",
    });
    polydata.getPointData().setTcoords(tcArray);
  }

  private _setupNormals(
    sourceResult: SourceResult,
    normalsConfig: NormalsConfig | undefined,
  ): SourceResult {
    if (!normalsConfig) return sourceResult;
    const vtk = getVtk();
    const normals = vtk.Filters.Core.vtkPolyDataNormals.newInstance();
    normals.setComputePointNormals?.(normalsConfig.computePointNormals);
    normals.setComputeCellNormals?.(normalsConfig.computeCellNormals);
    connectInput(normals, sourceResult);
    return { output: normals, isFilter: true };
  }

  private _applyFilters(sourceResult: SourceResult, filters: FilterConfig[]): SourceResult {
    let current = sourceResult;
    for (const f of filters) {
      switch (f.type) {
        case "shrink":
          if (f.shrinkFactor !== undefined)
            current = this._applyShrinkFilter(current, f.shrinkFactor);
          break;
        case "tube":
          if (f.radius !== undefined && f.numberOfSides !== undefined)
            current = this._applyTubeFilter(current, f.radius, f.numberOfSides);
          break;
        case "clip":
          if (f.normal && f.origin && f.invert !== undefined)
            current = this._applyClipFilter(current, f.normal, f.origin, f.invert);
          break;
        case "contour":
          if (f.values && f.scalarName && f.scalarData)
            current = this._applyContourFilter(current, f.values, f.scalarName, f.scalarData);
          break;
        case "fillHoles":
          if (f.holeSize !== undefined) current = this._applyFillHolesFilter(current, f.holeSize);
          break;

        default:
          break;
      }
    }
    return current;
  }

  private _applyPbr(actor: AnyVtk, pbr: PbrConfig | undefined): void {
    if (!pbr) return;
    const m = pbr.metallic;
    const r = pbr.roughness;
    actor.getProperty().setInterpolationToPhong();
    actor.getProperty().setMetallic(m);
    actor.getProperty().setRoughness(r);
    actor.getProperty().setAmbient(PBR_AMBIENT);
    actor.getProperty().setSpecular(PBR_SPECULAR_METALLIC_WEIGHT * m + PBR_SPECULAR_BASE);
    actor.getProperty().setSpecularPower(Math.max(1, PBR_SPECULAR_POWER_SCALE * (1 - r)));
    actor.getProperty().setDiffuse(PBR_DIFFUSE_BASE + PBR_DIFFUSE_METALLIC_WEIGHT * (1 - m));
  }

  private _applyTexture(actor: AnyVtk, textureCfg: TextureConfig | undefined): void {
    if (!textureCfg) return;
    const vtk = getVtk();
    const texture = vtk.Rendering.Core.vtkTexture.newInstance();
    texture.setInterpolate(true);
    actor.addTexture(texture);
    const img = new Image();
    img.crossOrigin = "anonymous";
    img.addEventListener("load", () => {
      texture.setImage(img);
      this._renderWindow.render();
    });
    img.src = textureCfg.url;
  }

  private _applyActorStyle(actor: AnyVtk, cfg: ActorConfig): void {
    const styleMap: Record<string, number> = {
      surface: VTK_REPRESENTATION_SURFACE,
      wireframe: VTK_REPRESENTATION_WIREFRAME,
      points: VTK_REPRESENTATION_POINTS,
    };
    const rep = styleMap[cfg.style];
    if (rep !== undefined) actor.getProperty().setRepresentation(rep);
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

  private _applyPointStyle(actor: AnyVtk, mapper: AnyVtk, cfg: ActorConfig): void {
    if (cfg.actorType !== "points") return;
    if (cfg.renderPointsAsSpheres && mapper.setRadius) {
      mapper.setRadius((cfg.pointSize ?? DEFAULT_POINT_SIZE) * POINT_SPHERE_RADIUS_SCALE);
    } else {
      actor.getProperty().setPointSize(cfg.pointSize ?? DEFAULT_POINT_SIZE);
      actor.getProperty().setRepresentationToPoints();
    }
  }

  private _createMapper(mapperInput: SourceResult, cfg: ActorConfig): AnyVtk {
    const vtk = getVtk();
    const mapperClass =
      cfg.actorType === "points" && cfg.renderPointsAsSpheres
        ? vtk.Rendering.Core.vtkSphereMapper
        : vtk.Rendering.Core.vtkMapper;
    const mapper = mapperClass.newInstance();
    if (mapperInput.isFilter) {
      mapper.setInputConnection(mapperInput.output.getOutputPort());
    } else {
      mapper.setInputData(mapperInput.output);
    }
    return mapper;
  }

  private _setupActor(cfg: ActorConfig, _index: number): void {
    const vtk = getVtk();
    const sourceResult = this._createSource(cfg.source);
    if (!sourceResult?.output) return;

    if (cfg.source.pointData ?? cfg.source.tCoords) {
      const pd = getPolyData(sourceResult);
      this._injectPointData(pd, cfg.source.pointData);
      this._injectTcoords(pd, cfg.source.tCoords);
    }

    let currentResult = sourceResult;
    if (cfg.source.filters && cfg.source.filters.length > 0) {
      currentResult = this._applyFilters(sourceResult, cfg.source.filters);
    }

    const mapperInput = this._setupNormals(currentResult, cfg.normals);
    const mapper = this._createMapper(mapperInput, cfg);

    const actor = vtk.Rendering.Core.vtkActor.newInstance();
    actor.setMapper(mapper);
    actor.getProperty().setColor(cfg.color[0], cfg.color[1], cfg.color[2]);
    actor.getProperty().setOpacity(cfg.opacity);

    this._applyActorStyle(actor, cfg);
    this._applyPbr(actor, cfg.pbr);
    this._applyPointStyle(actor, mapper, cfg);
    this._applyTexture(actor, cfg.texture);

    this._renderer.addActor(actor);
  }

  private _setupCamera(camConfig: CameraConfig): void {
    const cam = this._renderer.getActiveCamera();
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
      this._renderer.resetCamera();
      this._renderer.resetCameraClippingRange();
    }
  }

  private _setupAxes(): void {
    const vtk = getVtk();
    const axes = vtk.Rendering.Core.vtkAxesActor.newInstance();
    const orientationWidget = vtk.Interaction.Widgets.vtkOrientationMarkerWidget.newInstance({
      actor: axes,
      interactor: this._interactor,
    });
    orientationWidget.setEnabled(true);
    orientationWidget.setViewportCorner(
      vtk.Interaction.Widgets.vtkOrientationMarkerWidget.Corners.BOTTOM_LEFT,
    );
    orientationWidget.setViewportSize(AXES_VIEWPORT_SIZE);
    orientationWidget.setMinPixelSize(AXES_MIN_PIXEL_SIZE);
    orientationWidget.setMaxPixelSize(AXES_MAX_PIXEL_SIZE);
  }

  private _setupTextActor(cfg: TextActorConfig): void {
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
    div.style.fontWeight = cfg.bold ? "bold" : "normal";
    div.style.fontStyle = cfg.italic ? "italic" : "normal";
    div.style.pointerEvents = "none";
    div.style.zIndex = "10";
    div.style.whiteSpace = "pre";
    div.style.textShadow = "1px 1px 2px rgba(0,0,0,0.8), -1px -1px 2px rgba(0,0,0,0.8)";
    this._container.append(div);
  }

  // --- Filter implementations ---

  private _applyShrinkFilter(sourceResult: SourceResult, shrinkFactor: number): SourceResult {
    const vtk = getVtk();
    const inputPd = getPolyData(sourceResult);
    const inPoints = inputPd.getPoints().getData();
    const polys = inputPd.getPolys().getData();
    if (polys.length === 0) return sourceResult;

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
      for (let i = 0; i < nVerts; i++) {
        const vi = at(polys, index + i);
        indices.push(vi);
        cx += at(inPoints, vi * XYZ_COMPONENTS);
        cy += at(inPoints, vi * XYZ_COMPONENTS + 1);
        cz += at(inPoints, vi * XYZ_COMPONENTS + 2);
      }
      cx /= nVerts;
      cy /= nVerts;
      cz /= nVerts;
      resultPolys.push(nVerts);
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

    const outputPd = vtk.Common.DataModel.vtkPolyData.newInstance();
    outputPd.getPoints().setData(new Float32Array(resultPoints), XYZ_COMPONENTS);
    outputPd.getPolys().setData(new Uint32Array(resultPolys));
    return { output: outputPd, isFilter: false };
  }

  private _applyTubeFilter(
    sourceResult: SourceResult,
    radius: number,
    numberOfSides: number,
  ): SourceResult {
    const vtk = getVtk();
    const tubeFilter = vtk.Filters.General.vtkTubeFilter.newInstance({ radius, numberOfSides });
    connectInput(tubeFilter, sourceResult);
    return { output: tubeFilter, isFilter: true };
  }

  private _applyClipFilter(
    sourceResult: SourceResult,
    normal: [number, number, number],
    origin: [number, number, number],
    invert: boolean,
  ): SourceResult {
    const vtk = getVtk();
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
    return this._applyClipManual(sourceResult, normal, origin, invert);
  }

  private _applyClipManual(
    sourceResult: SourceResult,
    normal: [number, number, number],
    origin: [number, number, number],
    invert: boolean,
  ): SourceResult {
    const vtk = getVtk();
    const inputPd = getPolyData(sourceResult);
    const inPoints = inputPd.getPoints().getData();
    const polys = inputPd.getPolys().getData();
    if (polys.length === 0) return sourceResult;

    const resultPoints: number[] = [];
    const resultPolys: number[] = [];
    const pointMap = new Map<number, number>();
    let nextIndex = 0;
    let index = 0;
    while (index < polys.length) {
      const nVerts = at(polys, index);
      index++;
      const cellIndices: number[] = [];
      for (let i = 0; i < nVerts; i++) cellIndices.push(at(polys, index + i));

      let cx = 0,
        cy = 0,
        cz = 0;
      for (const vi of cellIndices) {
        cx += at(inPoints, vi * XYZ_COMPONENTS);
        cy += at(inPoints, vi * XYZ_COMPONENTS + 1);
        cz += at(inPoints, vi * XYZ_COMPONENTS + 2);
      }
      cx /= nVerts;
      cy /= nVerts;
      cz /= nVerts;
      const dot =
        (cx - origin[0]) * normal[0] + (cy - origin[1]) * normal[1] + (cz - origin[2]) * normal[2];
      const keep = invert ? dot >= 0 : dot <= 0;

      if (keep) {
        resultPolys.push(cellIndices.length);
        for (const pi of cellIndices) {
          if (!pointMap.has(pi)) {
            pointMap.set(pi, nextIndex++);
            resultPoints.push(
              at(inPoints, pi * XYZ_COMPONENTS),
              at(inPoints, pi * XYZ_COMPONENTS + 1),
              at(inPoints, pi * XYZ_COMPONENTS + 2),
            );
          }
          resultPolys.push(pointMap.get(pi) ?? 0);
        }
      }
      index += nVerts;
    }

    const outputPd = vtk.Common.DataModel.vtkPolyData.newInstance();
    outputPd.getPoints().setData(new Float32Array(resultPoints), XYZ_COMPONENTS);
    outputPd.getPolys().setData(new Uint32Array(resultPolys));
    return { output: outputPd, isFilter: false };
  }

  private _applyContourFilter(
    sourceResult: SourceResult,
    values: number[],
    scalarName: string,
    scalarData: number[],
  ): SourceResult {
    const vtk = getVtk();
    const inputPd = getPolyData(sourceResult);
    const scalars = vtk.Common.Core.vtkDataArray.newInstance({
      numberOfComponents: 1,
      values: Float32Array.from(scalarData),
      name: scalarName,
    });
    inputPd.getPointData().addArray(scalars);
    inputPd.getPointData().setActiveScalars(scalarName);

    const inPoints = inputPd.getPoints().getData();
    const polys = inputPd.getPolys().getData();
    const scalarValues = scalars.getData();
    if (polys.length === 0) return { output: inputPd, isFilter: false };

    const outPoints: number[] = [];
    const outPolys: number[] = [];
    let pointIndex = 0;
    let index = 0;
    while (index < polys.length) {
      const nVerts = at(polys, index);
      index++;
      if (nVerts === TRIANGLE_VERTS) {
        const i0 = at(polys, index),
          i1 = at(polys, index + 1),
          i2 = at(polys, index + 2);
        const s0 = at(scalarValues, i0),
          s1 = at(scalarValues, i1),
          s2 = at(scalarValues, i2);
        const edges: [number, number, number, number][] = [
          [i0, i1, s0, s1],
          [i1, i2, s1, s2],
          [i2, i0, s2, s0],
        ];
        for (const value of values) {
          const edgePoints: number[] = [];
          for (const [ai, bi, sa, sb] of edges) {
            if ((sa <= value && value < sb) || (sb <= value && value < sa)) {
              const t = (value - sa) / (sb - sa);
              edgePoints.push(
                at(inPoints, ai * XYZ_COMPONENTS) +
                  t * (at(inPoints, bi * XYZ_COMPONENTS) - at(inPoints, ai * XYZ_COMPONENTS)),
                at(inPoints, ai * XYZ_COMPONENTS + 1) +
                  t *
                    (at(inPoints, bi * XYZ_COMPONENTS + 1) - at(inPoints, ai * XYZ_COMPONENTS + 1)),
                at(inPoints, ai * XYZ_COMPONENTS + 2) +
                  t *
                    (at(inPoints, bi * XYZ_COMPONENTS + 2) - at(inPoints, ai * XYZ_COMPONENTS + 2)),
              );
            }
          }
          if (edgePoints.length === TWO_POINTS_XYZ) {
            outPoints.push(...edgePoints);
            outPolys.push(2, pointIndex, pointIndex + 1);
            pointIndex += 2;
          }
        }
      }
      index += nVerts;
    }

    const outputPd = vtk.Common.DataModel.vtkPolyData.newInstance();
    if (outPoints.length > 0) {
      outputPd.getPoints().setData(new Float32Array(outPoints), XYZ_COMPONENTS);
      outputPd.getLines().setData(new Uint32Array(outPolys));
    }
    return { output: outputPd, isFilter: false };
  }

  private _applyFillHolesFilter(sourceResult: SourceResult, holeSize: number): SourceResult {
    const vtk = getVtk();
    const inputPd = getPolyData(sourceResult);
    const inPoints = inputPd.getPoints().getData();
    const polys = inputPd.getPolys().getData();
    if (polys.length === 0) return sourceResult;

    const edgeCount = new Map<string, number>();
    let index = 0;
    while (index < polys.length) {
      const nVerts = at(polys, index);
      index++;
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
      if (count !== 1) continue;
      const parts = key.split("_");
      const a = Number(parts[0]),
        b = Number(parts[1]);
      // biome-ignore lint/style/noNonNullAssertion: Map.get after Map.set always returns the value
      (boundaryAdj.get(a) ?? boundaryAdj.set(a, []).get(a)!).push(b);
      // biome-ignore lint/style/noNonNullAssertion: Map.get after Map.set always returns the value
      (boundaryAdj.get(b) ?? boundaryAdj.set(b, []).get(b)!).push(a);
    }
    if (boundaryAdj.size === 0) return sourceResult;

    const visited = new Set<number>();
    const loops: number[][] = [];
    for (const startNode of boundaryAdj.keys()) {
      if (visited.has(startNode)) continue;
      const loop: number[] = [];
      let current = startNode,
        previous = -1,
        stuck = false;
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
      if (loop.length > 2) loops.push(loop);
    }

    const newPolys: number[] = [];
    for (const loop of loops) {
      let perimeter = 0;
      for (let k = 0; k < loop.length; k++) {
        const a = loop[k] ?? 0,
          b = loop[(k + 1) % loop.length] ?? 0;
        const dx = at(inPoints, b * XYZ_COMPONENTS) - at(inPoints, a * XYZ_COMPONENTS);
        const dy = at(inPoints, b * XYZ_COMPONENTS + 1) - at(inPoints, a * XYZ_COMPONENTS + 1);
        const dz = at(inPoints, b * XYZ_COMPONENTS + 2) - at(inPoints, a * XYZ_COMPONENTS + 2);
        perimeter += Math.hypot(dx, dy, dz);
      }
      if (perimeter <= holeSize) {
        const v0 = loop[0] ?? 0;
        for (let k = 1; k < loop.length - 1; k++) {
          newPolys.push(TRIANGLE_VERTS, v0, loop[k] ?? 0, loop[k + 1] ?? 0);
        }
      }
    }

    if (newPolys.length === 0) return sourceResult;
    const mergedPolys = new Uint32Array([...polys, ...newPolys]);
    const outputPd = vtk.Common.DataModel.vtkPolyData.newInstance();
    outputPd.getPoints().setData(new Float32Array(inPoints), XYZ_COMPONENTS);
    outputPd.getPolys().setData(mergedPolys);
    return { output: outputPd, isFilter: false };
  }
}
