"use strict";
(() => {
  // ts/renderer.ts
  var XYZ_COMPONENTS = 3;
  var UV_COMPONENTS = 2;
  var DEFAULT_WIDTH = 600;
  var DEFAULT_HEIGHT = 400;
  var COLOR_BYTE_SCALE = 255;
  var PERCENT = 100;
  var DEFAULT_RADIUS = 1;
  var DEFAULT_RESOLUTION = 50;
  var POINT_SPHERE_RADIUS_SCALE = 0.01;
  var DEFAULT_POINT_SIZE = 5;
  var PBR_AMBIENT = 0.1;
  var PBR_SPECULAR_METALLIC_WEIGHT = 0.75;
  var PBR_SPECULAR_BASE = 0.25;
  var PBR_SPECULAR_POWER_SCALE = 100;
  var PBR_DIFFUSE_BASE = 0.65;
  var PBR_DIFFUSE_METALLIC_WEIGHT = 0.35;
  var AXES_VIEWPORT_SIZE = 0.15;
  var AXES_MIN_PIXEL_SIZE = 100;
  var AXES_MAX_PIXEL_SIZE = 300;
  var VTK_REPRESENTATION_SURFACE = 2;
  var VTK_REPRESENTATION_WIREFRAME = 1;
  var VTK_REPRESENTATION_POINTS = 0;
  var DISK_RADIAL_RESOLUTION = 1;
  var TRIANGLE_VERTS = 3;
  var TWO_POINTS_XYZ = 6;
  function at(array, index) {
    var _a3;
    return (_a3 = array[index]) != null ? _a3 : 0;
  }
  function getPolyData(sourceResult) {
    if (sourceResult.isFilter) {
      sourceResult.output.update();
      return sourceResult.output.getOutputData();
    }
    return sourceResult.output;
  }
  function connectInput(filter, sourceResult) {
    if (sourceResult.isFilter) {
      filter.setInputConnection(sourceResult.output.getOutputPort());
    } else {
      filter.setInputData(sourceResult.output);
    }
  }
  var _a, _b;
  var sceneData = (
    // biome-ignore lint/nursery/noTernary lint/correctness/noUndeclaredVariables: ternary is idiomatic for concise conditional returns
    typeof __pvjsSceneData === "undefined" ? JSON.parse((_b = (_a = document.querySelector("#scene-data")) == null ? void 0 : _a.textContent) != null ? _b : "{}") : (
      // biome-ignore lint/correctness/noUndeclaredVariables: vtk globals are declared in vtk.d.ts
      __pvjsSceneData
    )
  );
  var _a2;
  var container = (
    // biome-ignore lint/nursery/noTernary lint/correctness/noUndeclaredVariables: ternary is idiomatic for concise conditional returns
    typeof __pvjsContainer === "undefined" ? (_a2 = document.querySelector(`#${CSS.escape(sceneData.containerId)}`)) != null ? _a2 : document.createElement("div") : (
      // biome-ignore lint/correctness/noUndeclaredVariables: vtk globals are declared in vtk.d.ts
      __pvjsContainer
    )
  );
  var bg = sceneData.background;
  var renderer = vtk.Rendering.Core.vtkRenderer.newInstance();
  renderer.setBackground(bg[0], bg[1], bg[2]);
  var renderWindow = vtk.Rendering.Core.vtkRenderWindow.newInstance();
  renderWindow.addRenderer(renderer);
  var openGlRenderWindow = vtk.Rendering.OpenGL.vtkRenderWindow.newInstance();
  renderWindow.addView(openGlRenderWindow);
  openGlRenderWindow.setContainer(container);
  var bbox = container.getBoundingClientRect();
  openGlRenderWindow.setSize(bbox.width || DEFAULT_WIDTH, bbox.height || DEFAULT_HEIGHT);
  var interactor = vtk.Rendering.Core.vtkRenderWindowInteractor.newInstance();
  var interactorStyle = vtk.Interaction.Style.vtkInteractorStyleTrackballCamera.newInstance();
  interactor.setInteractorStyle(interactorStyle);
  interactor.setView(openGlRenderWindow);
  interactor.initialize();
  interactor.bindEvents(container);
  window.renderer = renderer;
  window.renderWindow = renderWindow;
  window.openGlRenderWindow = openGlRenderWindow;
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
  function setupLights(lightsConfig, ren) {
    var _a3;
    if (lightsConfig.length === 0) {
      return;
    }
    ren.removeAllLights();
    ren.setAutomaticLightCreation(false);
    for (const cfg of lightsConfig) {
      const light = vtk.Rendering.Core.vtkLight.newInstance();
      const typeMap = {
        // biome-ignore lint/security/noSecrets: vtk.js method name, not a secret
        scene: "setLightTypeToSceneLight",
        // biome-ignore lint/security/noSecrets: vtk.js method name, not a secret
        camera: "setLightTypeToCameraLight",
        // biome-ignore lint/security/noSecrets: vtk.js method name, not a secret
        head: "setLightTypeToHeadLight"
      };
      const setter = (_a3 = typeMap[cfg.type]) != null ? _a3 : "setLightTypeToSceneLight";
      const setterFunction = light[setter];
      if (typeof setterFunction === "function") {
        setterFunction.call(light);
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
        cfg.attenuationValues[2]
      );
      ren.addLight(light);
    }
  }
  function getReaderMap() {
    return {
      plyReader: {
        // biome-ignore lint/correctness/noUndeclaredVariables: vtk globals are declared in vtk.d.ts
        factory: vtk.IO.Geometry.vtkPLYReader,
        parseMethod: "parseAsArrayBuffer"
      },
      stlReader: {
        // biome-ignore lint/correctness/noUndeclaredVariables: vtk globals are declared in vtk.d.ts
        factory: vtk.IO.Geometry.vtkSTLReader,
        parseMethod: "parseAsArrayBuffer"
      },
      objReader: {
        // biome-ignore lint/correctness/noUndeclaredVariables: vtk globals are declared in vtk.d.ts
        factory: vtk.IO.Misc.vtkOBJReader,
        parseMethod: "parseAsText"
      },
      vtkReader: {
        // biome-ignore lint/correctness/noUndeclaredVariables: vtk globals are declared in vtk.d.ts
        factory: vtk.IO.Legacy.vtkPolyDataReader,
        parseMethod: "parseAsText"
      }
    };
  }
  function createSource(cfg) {
    const sourceFactoryMap = {
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
      vtkReader: createReaderSource
    };
    const factory = sourceFactoryMap[cfg.type];
    if (!factory) {
      return;
    }
    return factory(cfg);
  }
  function createSphereSource(cfg) {
    const source = vtk.Filters.Sources.vtkSphereSource.newInstance({
      center: cfg.center,
      radius: cfg.radius,
      thetaResolution: cfg.thetaResolution,
      phiResolution: cfg.phiResolution
    });
    const texMap = vtk.Filters.Texture.vtkTextureMapToSphere.newInstance();
    texMap.setInputConnection(source.getOutputPort());
    return { output: texMap, isFilter: true };
  }
  function createConeSource(cfg) {
    const source = vtk.Filters.Sources.vtkConeSource.newInstance({
      height: cfg.height,
      radius: cfg.radius,
      resolution: cfg.resolution
    });
    return { output: source, isFilter: true };
  }
  function createCubeSource(cfg) {
    const source = vtk.Filters.Sources.vtkCubeSource.newInstance({
      xLength: cfg.xLength,
      yLength: cfg.yLength,
      zLength: cfg.zLength
    });
    return { output: source, isFilter: false };
  }
  function createCylinderSource(cfg) {
    const source = vtk.Filters.Sources.vtkCylinderSource.newInstance({
      height: cfg.height,
      radius: cfg.radius,
      resolution: cfg.resolution
    });
    return { output: source, isFilter: true };
  }
  function createDiskSource(cfg) {
    const diskFactory = vtk.Filters.Sources.vtkDiskSource;
    const source = diskFactory ? diskFactory.newInstance({
      innerRadius: cfg.innerRadius,
      outerRadius: cfg.outerRadius,
      radialResolution: DISK_RADIAL_RESOLUTION,
      circumferentialResolution: cfg.resolution
    }) : void 0;
    return {
      // biome-ignore lint/correctness/noUndeclaredVariables: vtk globals are declared in vtk.d.ts
      output: source != null ? source : vtk.Common.DataModel.vtkPolyData.newInstance(),
      isFilter: true
    };
  }
  function createCircleSource(cfg) {
    var _a3, _b2;
    return createDiskSource({
      type: "disk",
      innerRadius: 0,
      outerRadius: (_a3 = cfg.radius) != null ? _a3 : DEFAULT_RADIUS,
      resolution: (_b2 = cfg.resolution) != null ? _b2 : DEFAULT_RESOLUTION
    });
  }
  function createArrowSource(cfg) {
    const source = vtk.Filters.Sources.vtkArrowSource.newInstance({
      tipLength: cfg.tipLength,
      tipRadius: cfg.tipRadius,
      shaftRadius: cfg.shaftRadius
    });
    return { output: source, isFilter: true };
  }
  function createLineSource(cfg) {
    const source = vtk.Filters.Sources.vtkLineSource.newInstance({
      point1: cfg.point1,
      point2: cfg.point2
    });
    return { output: source, isFilter: true };
  }
  function createPlaneSource(cfg) {
    var _a3;
    const source = vtk.Filters.Sources.vtkPlaneSource.newInstance({
      origin: cfg.origin
    });
    if (cfg.normal) {
      (_a3 = source.setNormal) == null ? void 0 : _a3.call(source, cfg.normal[0], cfg.normal[1], cfg.normal[2]);
    }
    return { output: source, isFilter: true };
  }
  function createMeshSource(cfg) {
    var _a3;
    const polydata = vtk.Common.DataModel.vtkPolyData.newInstance();
    const pointsArray = Float32Array.from((_a3 = cfg.points) != null ? _a3 : []);
    const vtkPts = vtk.Common.Core.vtkPoints.newInstance();
    vtkPts.setData(pointsArray, XYZ_COMPONENTS);
    polydata.setPoints(vtkPts);
    if (cfg.polys) {
      const polysArray = Uint32Array.from(cfg.polys);
      polydata.getPolys().setData(polysArray);
    }
    return { output: polydata, isFilter: false };
  }
  function createPointsSource(cfg) {
    var _a3;
    const polydata = vtk.Common.DataModel.vtkPolyData.newInstance();
    const pointsArray = Float32Array.from((_a3 = cfg.points) != null ? _a3 : []);
    const vtkPts = vtk.Common.Core.vtkPoints.newInstance();
    vtkPts.setData(pointsArray, XYZ_COMPONENTS);
    polydata.setPoints(vtkPts);
    return { output: polydata, isFilter: false };
  }
  function createReaderSource(cfg) {
    var _a3;
    const entry = getReaderMap()[cfg.type];
    if (!entry) {
      throw new Error(`Unknown reader type: ${cfg.type}`);
    }
    const bytes = Uint8Array.from(atob((_a3 = cfg.data) != null ? _a3 : ""), (char) => {
      var _a4;
      return (_a4 = char.codePointAt(0)) != null ? _a4 : 0;
    });
    const reader = entry.factory.newInstance();
    if (entry.parseMethod === "parseAsText") {
      reader.parseAsText(new TextDecoder().decode(bytes));
    } else {
      reader.parseAsArrayBuffer(new Uint8Array(bytes).buffer);
    }
    return {
      output: reader,
      isFilter: true
    };
  }
  function injectPointData(polydata, pointDataArrays) {
    if (!pointDataArrays) {
      return;
    }
    for (const array of pointDataArrays) {
      const dataArray = vtk.Common.Core.vtkDataArray.newInstance({
        numberOfComponents: array.numberOfComponents,
        values: Float32Array.from(array.values),
        name: array.name
      });
      polydata.getPointData().addArray(dataArray);
    }
  }
  function injectTcoords(polydata, tCoords) {
    if (!tCoords) {
      return;
    }
    const tcArray = vtk.Common.Core.vtkDataArray.newInstance({
      numberOfComponents: UV_COMPONENTS,
      values: Float32Array.from(tCoords),
      name: "TextureCoordinates"
    });
    polydata.getPointData().setTcoords(tcArray);
  }
  function setupNormals(sourceResult, normalsConfig) {
    var _a3, _b2;
    if (!normalsConfig) {
      return sourceResult;
    }
    const normals = vtk.Filters.Core.vtkPolyDataNormals.newInstance();
    (_a3 = normals.setComputePointNormals) == null ? void 0 : _a3.call(normals, normalsConfig.computePointNormals);
    (_b2 = normals.setComputeCellNormals) == null ? void 0 : _b2.call(normals, normalsConfig.computeCellNormals);
    connectInput(normals, sourceResult);
    return { output: normals, isFilter: true };
  }
  function applyPbr(actor, pbr) {
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
  function applyTexture(actor, renWin, textureCfg) {
    if (!textureCfg) {
      return;
    }
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
  function applyActorStyle(actor, cfg) {
    const styleMap = {
      surface: VTK_REPRESENTATION_SURFACE,
      wireframe: VTK_REPRESENTATION_WIREFRAME,
      points: VTK_REPRESENTATION_POINTS
    };
    const rep = styleMap[cfg.style];
    if (rep !== void 0) {
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
  function applyPointStyle(actor, mapper, cfg) {
    var _a3, _b2;
    if (cfg.actorType !== "points") {
      return;
    }
    if (cfg.renderPointsAsSpheres && mapper.setRadius) {
      mapper.setRadius(((_a3 = cfg.pointSize) != null ? _a3 : DEFAULT_POINT_SIZE) * POINT_SPHERE_RADIUS_SCALE);
    } else {
      actor.getProperty().setPointSize((_b2 = cfg.pointSize) != null ? _b2 : DEFAULT_POINT_SIZE);
      actor.getProperty().setRepresentationToPoints();
    }
  }
  function createMapper(mapperInput, cfg) {
    const mapperClass = (
      // biome-ignore lint/nursery/noTernary: ternary is idiomatic for concise conditional returns
      cfg.actorType === "points" && cfg.renderPointsAsSpheres ? (
        // biome-ignore lint/correctness/noUndeclaredVariables: vtk globals are declared in vtk.d.ts
        vtk.Rendering.Core.vtkSphereMapper
      ) : (
        // biome-ignore lint/correctness/noUndeclaredVariables: vtk globals are declared in vtk.d.ts
        vtk.Rendering.Core.vtkMapper
      )
    );
    const mapper = mapperClass.newInstance();
    if (mapperInput.isFilter) {
      mapper.setInputConnection(mapperInput.output.getOutputPort());
    } else {
      mapper.setInputData(mapperInput.output);
    }
    return mapper;
  }
  function setupActor(cfg, _index, ren, renWin) {
    var _a3;
    const sourceResult = createSource(cfg.source);
    if (!(sourceResult == null ? void 0 : sourceResult.output)) {
      return;
    }
    if ((_a3 = cfg.source.pointData) != null ? _a3 : cfg.source.tCoords) {
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
  function setupCamera(ren, camConfig) {
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
    if (camConfig.viewAngle !== void 0) {
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
  function setupAxes(interactorObject) {
    const axes = vtk.Rendering.Core.vtkAxesActor.newInstance();
    const orientationWidget = vtk.Interaction.Widgets.vtkOrientationMarkerWidget.newInstance({
      actor: axes,
      interactor: interactorObject
    });
    orientationWidget.setEnabled(true);
    orientationWidget.setViewportCorner(
      // biome-ignore lint/correctness/noUndeclaredVariables: vtk globals are declared in vtk.d.ts
      vtk.Interaction.Widgets.vtkOrientationMarkerWidget.Corners.BOTTOM_LEFT
    );
    orientationWidget.setViewportSize(AXES_VIEWPORT_SIZE);
    orientationWidget.setMinPixelSize(AXES_MIN_PIXEL_SIZE);
    orientationWidget.setMaxPixelSize(AXES_MAX_PIXEL_SIZE);
  }
  function setupTextActor(cfg, containerElement) {
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
    containerElement.append(div);
  }
  function tryShrinkFilter(current, f) {
    return f.shrinkFactor === void 0 ? current : applyShrinkFilter(current, f.shrinkFactor);
  }
  function tryTubeFilter(current, f) {
    return f.radius === void 0 || f.numberOfSides === void 0 ? current : applyTubeFilter(current, f.radius, f.numberOfSides);
  }
  function tryClipFilter(current, f) {
    return !(f.normal && f.origin) || f.invert === void 0 ? current : applyClipFilter(current, f.normal, f.origin, f.invert);
  }
  function tryContourFilter(current, f) {
    return f.values && f.scalarName && f.scalarData ? applyContourFilter(current, f.values, f.scalarName, f.scalarData) : current;
  }
  function tryFillHolesFilter(current, f) {
    return f.holeSize === void 0 ? current : applyFillHolesFilter(current, f.holeSize);
  }
  function tryTriangulateFilter(current, _f) {
    return applyTriangulateFilter(current);
  }
  function applyTriangulateFilter(sourceResult) {
    const triangleFilter = vtk.Filters.General.vtkTriangleFilter.newInstance();
    connectInput(triangleFilter, sourceResult);
    return { output: triangleFilter, isFilter: true };
  }
  var filterDispatchMap = {
    shrink: tryShrinkFilter,
    tube: tryTubeFilter,
    clip: tryClipFilter,
    contour: tryContourFilter,
    fillHoles: tryFillHolesFilter,
    triangulate: tryTriangulateFilter
  };
  function applyFilters(sourceResult, filters) {
    let current = sourceResult;
    for (const f of filters) {
      const dispatch = filterDispatchMap[f.type];
      if (dispatch) {
        current = dispatch(current, f);
      }
    }
    return current;
  }
  function applyShrinkFilter(sourceResult, shrinkFactor) {
    var _a3;
    const inputPd = getPolyData(sourceResult);
    const inPoints = inputPd.getPoints().getData();
    const polys = inputPd.getPolys().getData();
    if (polys.length === 0) {
      return sourceResult;
    }
    const resultPoints = [];
    const resultPolys = [];
    let offset = 0;
    let index = 0;
    while (index < polys.length) {
      const nVerts = at(polys, index);
      index++;
      let cx = 0;
      let cy = 0;
      let cz = 0;
      const indices = [];
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
      for (let k = 0; k < nVerts; k++) {
        const pi = (_a3 = indices[k]) != null ? _a3 : 0;
        const px = at(inPoints, pi * XYZ_COMPONENTS);
        const py = at(inPoints, pi * XYZ_COMPONENTS + 1);
        const pz = at(inPoints, pi * XYZ_COMPONENTS + 2);
        resultPoints.push(
          cx + (px - cx) * shrinkFactor,
          cy + (py - cy) * shrinkFactor,
          cz + (pz - cz) * shrinkFactor
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
  function applyTubeFilter(sourceResult, radius, numberOfSides) {
    const tubeFilter = vtk.Filters.General.vtkTubeFilter.newInstance({
      radius,
      numberOfSides
    });
    connectInput(tubeFilter, sourceResult);
    return { output: tubeFilter, isFilter: true };
  }
  function applyClipFilter(sourceResult, normal, origin, invert) {
    var _a3;
    const plane = vtk.Common.DataModel.vtkPlane.newInstance();
    plane.setOrigin(origin[0], origin[1], origin[2]);
    plane.setNormal(normal[0], normal[1], normal[2]);
    const clipFactory = vtk.Filters.General.vtkClipClosedSurface;
    if (clipFactory) {
      const clipper = clipFactory.newInstance();
      (_a3 = clipper.setClippingPlanes) == null ? void 0 : _a3.call(clipper, [plane]);
      connectInput(clipper, sourceResult);
      return { output: clipper, isFilter: true };
    }
    return applyClipManual(sourceResult, normal, origin, invert);
  }
  function shouldKeepCell(cellIndices, inPoints, plane) {
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
    const dot = (cx - plane.origin[0]) * plane.normal[0] + (cy - plane.origin[1]) * plane.normal[1] + (cz - plane.origin[2]) * plane.normal[2];
    return plane.invert ? dot >= 0 : dot <= 0;
  }
  function emitClippedCell(cellIndices, state) {
    var _a3;
    state.resultPolys.push(cellIndices.length);
    for (const pi of cellIndices) {
      if (!state.pointMap.has(pi)) {
        state.pointMap.set(pi, state.nextIndex++);
        state.resultPoints.push(
          at(state.inPoints, pi * XYZ_COMPONENTS),
          at(state.inPoints, pi * XYZ_COMPONENTS + 1),
          at(state.inPoints, pi * XYZ_COMPONENTS + 2)
        );
      }
      state.resultPolys.push((_a3 = state.pointMap.get(pi)) != null ? _a3 : 0);
    }
  }
  function applyClipManual(sourceResult, normal, origin, invert) {
    const inputPd = getPolyData(sourceResult);
    const inPoints = inputPd.getPoints().getData();
    const polys = inputPd.getPolys().getData();
    if (polys.length === 0) {
      return sourceResult;
    }
    const plane = { normal, origin, invert };
    const state = {
      inPoints,
      resultPoints: [],
      resultPolys: [],
      pointMap: /* @__PURE__ */ new Map(),
      nextIndex: 0
    };
    let index = 0;
    while (index < polys.length) {
      const nVerts = at(polys, index);
      index++;
      const cellIndices = [];
      for (let index_ = 0; index_ < nVerts; index_++) {
        cellIndices.push(at(polys, index + index_));
      }
      if (shouldKeepCell(cellIndices, inPoints, plane)) {
        emitClippedCell(cellIndices, state);
      }
      index += nVerts;
    }
    const outputPd = vtk.Common.DataModel.vtkPolyData.newInstance();
    outputPd.getPoints().setData(new Float32Array(state.resultPoints), XYZ_COMPONENTS);
    outputPd.getPolys().setData(new Uint32Array(state.resultPolys));
    return { output: outputPd, isFilter: false };
  }
  function applyContourFilter(sourceResult, values, scalarName, scalarData) {
    const inputPd = getPolyData(sourceResult);
    const scalars = vtk.Common.Core.vtkDataArray.newInstance({
      numberOfComponents: 1,
      values: Float32Array.from(scalarData),
      name: scalarName
    });
    inputPd.getPointData().addArray(scalars);
    inputPd.getPointData().setActiveScalars(scalarName);
    return applyContourManual(inputPd, values, scalarName);
  }
  function collectEdgeIntersections(tri, value, inPoints) {
    const edgePoints = [];
    for (const edge of tri) {
      const [ai, bi, sa, sb] = edge;
      if (sa <= value && value < sb || sb <= value && value < sa) {
        const t = (value - sa) / (sb - sa);
        edgePoints.push(
          at(inPoints, ai * XYZ_COMPONENTS) + t * (at(inPoints, bi * XYZ_COMPONENTS) - at(inPoints, ai * XYZ_COMPONENTS)),
          at(inPoints, ai * XYZ_COMPONENTS + 1) + t * (at(inPoints, bi * XYZ_COMPONENTS + 1) - at(inPoints, ai * XYZ_COMPONENTS + 1)),
          at(inPoints, ai * XYZ_COMPONENTS + 2) + t * (at(inPoints, bi * XYZ_COMPONENTS + 2) - at(inPoints, ai * XYZ_COMPONENTS + 2))
        );
      }
    }
    return edgePoints;
  }
  function processContourTriangle(state, index) {
    var _a3, _b2, _c, _d, _e, _f;
    const index0 = at(state.polys, index);
    const index1 = at(state.polys, index + 1);
    const index2 = at(state.polys, index + 2);
    const s0 = at(state.scalarValues, index0);
    const s1 = at(state.scalarValues, index1);
    const s2 = at(state.scalarValues, index2);
    const tri = [
      [index0, index1, s0, s1],
      [index1, index2, s1, s2],
      [index2, index0, s2, s0]
    ];
    for (const value of state.values) {
      const edgePoints = collectEdgeIntersections(tri, value, state.inPoints);
      if (edgePoints.length === TWO_POINTS_XYZ) {
        state.outPoints.push(
          (_a3 = edgePoints[0]) != null ? _a3 : 0,
          (_b2 = edgePoints[1]) != null ? _b2 : 0,
          (_c = edgePoints[2]) != null ? _c : 0,
          (_d = edgePoints[3]) != null ? _d : 0,
          (_e = edgePoints[4]) != null ? _e : 0,
          (_f = edgePoints[5]) != null ? _f : 0
        );
        state.outPolys.push(2, state.pointIndex, state.pointIndex + 1);
        state.pointIndex += 2;
      }
    }
  }
  function applyContourManual(inputPd, values, scalarName) {
    const inPoints = inputPd.getPoints().getData();
    const polys = inputPd.getPolys().getData();
    const scalarsArray = inputPd.getPointData().getArrayByName(scalarName);
    if (polys.length === 0 || !scalarsArray) {
      return { output: inputPd, isFilter: false };
    }
    const scalarValues = scalarsArray.getData();
    const state = {
      polys,
      scalarValues,
      inPoints,
      values,
      outPoints: [],
      outPolys: [],
      pointIndex: 0
    };
    let index = 0;
    while (index < polys.length) {
      const nVerts = at(polys, index);
      index++;
      if (nVerts === TRIANGLE_VERTS) {
        processContourTriangle(state, index);
      }
      index += nVerts;
    }
    const outputPd = vtk.Common.DataModel.vtkPolyData.newInstance();
    if (state.outPoints.length > 0) {
      outputPd.getPoints().setData(new Float32Array(state.outPoints), XYZ_COMPONENTS);
      outputPd.getLines().setData(new Uint32Array(state.outPolys));
    }
    return { output: outputPd, isFilter: false };
  }
  function buildBoundaryAdjacency(polys) {
    var _a3;
    const edgeCount = /* @__PURE__ */ new Map();
    let index = 0;
    while (index < polys.length) {
      const nVerts = at(polys, index);
      index++;
      for (let k = 0; k < nVerts; k++) {
        const a = at(polys, index + k);
        const b = at(polys, index + (k + 1) % nVerts);
        const key = `${String(Math.min(a, b))}_${String(Math.max(a, b))}`;
        edgeCount.set(key, ((_a3 = edgeCount.get(key)) != null ? _a3 : 0) + 1);
      }
      index += nVerts;
    }
    const boundaryAdj = /* @__PURE__ */ new Map();
    for (const [key, count] of edgeCount) {
      if (count !== 1) {
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
  function walkLoop(startNode, boundaryAdj, visited) {
    var _a3;
    const loop = [];
    let current = startNode;
    let previous = -1;
    let stuck = false;
    while (!stuck) {
      visited.add(current);
      loop.push(current);
      const neighbors = (_a3 = boundaryAdj.get(current)) != null ? _a3 : [];
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
  function traceBoundaryLoops(boundaryAdj) {
    const visited = /* @__PURE__ */ new Set();
    const loops = [];
    for (const startNode of boundaryAdj.keys()) {
      if (visited.has(startNode)) {
        continue;
      }
      const loop = walkLoop(startNode, boundaryAdj, visited);
      if (loop.length > 2) {
        loops.push(loop);
      }
    }
    return loops;
  }
  function computeLoopPerimeter(loop, inPoints) {
    var _a3, _b2;
    let perimeter = 0;
    for (let k = 0; k < loop.length; k++) {
      const a = (_a3 = loop[k]) != null ? _a3 : 0;
      const b = (_b2 = loop[(k + 1) % loop.length]) != null ? _b2 : 0;
      const dx = at(inPoints, b * XYZ_COMPONENTS) - at(inPoints, a * XYZ_COMPONENTS);
      const dy = at(inPoints, b * XYZ_COMPONENTS + 1) - at(inPoints, a * XYZ_COMPONENTS + 1);
      const dz = at(inPoints, b * XYZ_COMPONENTS + 2) - at(inPoints, a * XYZ_COMPONENTS + 2);
      perimeter += Math.hypot(dx, dy, dz);
    }
    return perimeter;
  }
  function triangulateLoop(loop, newPolys) {
    var _a3, _b2, _c;
    const v0 = (_a3 = loop[0]) != null ? _a3 : 0;
    for (let k = 1; k < loop.length - 1; k++) {
      const v1 = (_b2 = loop[k]) != null ? _b2 : 0;
      const v2 = (_c = loop[k + 1]) != null ? _c : 0;
      newPolys.push(TRIANGLE_VERTS, v0, v1, v2);
    }
  }
  function applyFillHolesFilter(sourceResult, holeSize) {
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
    const newPolys = [];
    for (const loop of loops) {
      if (computeLoopPerimeter(loop, inPoints) <= holeSize) {
        triangulateLoop(loop, newPolys);
      }
    }
    if (newPolys.length === 0) {
      return sourceResult;
    }
    const mergedPolys = new Uint32Array([...polys, ...newPolys]);
    const outputPd = vtk.Common.DataModel.vtkPolyData.newInstance();
    outputPd.getPoints().setData(new Float32Array(inPoints), XYZ_COMPONENTS);
    outputPd.getPolys().setData(mergedPolys);
    return { output: outputPd, isFilter: false };
  }
})();
