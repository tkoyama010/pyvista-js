"use strict";
(() => {
  // ts/pyvista-renderer.ts
  var sceneData = typeof __pvjsSceneData !== "undefined" ? __pvjsSceneData : JSON.parse(document.getElementById("scene-data").textContent);
  var container = typeof __pvjsContainer !== "undefined" ? __pvjsContainer : document.getElementById(sceneData.containerId);
  var bg = sceneData.background;
  var renderer = vtk.Rendering.Core.vtkRenderer.newInstance();
  renderer.setBackground(bg[0], bg[1], bg[2]);
  var renderWindow = vtk.Rendering.Core.vtkRenderWindow.newInstance();
  renderWindow.addRenderer(renderer);
  var openGLRenderWindow = vtk.Rendering.OpenGL.vtkRenderWindow.newInstance();
  renderWindow.addView(openGLRenderWindow);
  openGLRenderWindow.setContainer(container);
  var bbox = container.getBoundingClientRect();
  openGLRenderWindow.setSize(bbox.width || 600, bbox.height || 400);
  var interactor = vtk.Rendering.Core.vtkRenderWindowInteractor.newInstance();
  var interactorStyle = vtk.Interaction.Style.vtkInteractorStyleTrackballCamera.newInstance();
  interactor.setInteractorStyle(interactorStyle);
  interactor.setView(openGLRenderWindow);
  interactor.initialize();
  interactor.bindEvents(container);
  window.renderer = renderer;
  window.renderWindow = renderWindow;
  window.openGLRenderWindow = openGLRenderWindow;
  window.interactor = interactor;
  if (sceneData.lightingMode === null && (!sceneData.lights || sceneData.lights.length === 0)) {
    renderer.removeAllLights();
    renderer.setAutomaticLightCreation(false);
  } else {
    setupLights(sceneData.lights, renderer);
  }
  sceneData.actors.forEach((actorConfig, idx) => {
    setupActor(actorConfig, idx, renderer, renderWindow);
  });
  if (sceneData.textActors) {
    sceneData.textActors.forEach((textConfig) => {
      setupTextActor(textConfig, container);
    });
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
    if (!lightsConfig || lightsConfig.length === 0) {
      return;
    }
    ren.removeAllLights();
    ren.setAutomaticLightCreation(false);
    lightsConfig.forEach((cfg) => {
      const light = vtk.Rendering.Core.vtkLight.newInstance();
      const typeMap = {
        scene: "setLightTypeToSceneLight",
        camera: "setLightTypeToCameraLight",
        head: "setLightTypeToHeadLight"
      };
      const setter = typeMap[cfg.type] || "setLightTypeToSceneLight";
      light[setter]();
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
    });
  }
  function createSource(cfg) {
    switch (cfg.type) {
      case "sphere":
        return createSphereSource(cfg);
      case "cone":
        return createConeSource(cfg);
      case "cube":
        return createCubeSource(cfg);
      case "cylinder":
        return createCylinderSource(cfg);
      case "disk":
        return createDiskSource(cfg);
      case "circle":
        return createCircleSource(cfg);
      case "arrow":
        return createArrowSource(cfg);
      case "line":
        return createLineSource(cfg);
      case "plane":
        return createPlaneSource(cfg);
      case "mesh":
        return createMeshSource(cfg);
      case "points":
        return createPointsSource(cfg);
      case "plyReader":
        return createReaderSource(cfg, "IO.Geometry.vtkPLYReader", "parseAsArrayBuffer");
      case "stlReader":
        return createReaderSource(cfg, "IO.Geometry.vtkSTLReader", "parseAsArrayBuffer");
      case "objReader":
        return createReaderSource(cfg, "IO.Misc.vtkOBJReader", "parseAsText");
      case "vtkReader":
        return createReaderSource(cfg, "IO.Legacy.vtkPolyDataReader", "parseAsText");
      default:
        console.error("Unknown source type:", cfg.type);
        return null;
    }
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
    const source = vtk.Filters.Sources.vtkDiskSource ? vtk.Filters.Sources.vtkDiskSource.newInstance({
      innerRadius: cfg.innerRadius,
      outerRadius: cfg.outerRadius,
      radialResolution: 1,
      circumferentialResolution: cfg.resolution
    }) : null;
    return { output: source, isFilter: true };
  }
  function createCircleSource(cfg) {
    return createDiskSource({
      type: "disk",
      innerRadius: 0,
      outerRadius: cfg.radius,
      resolution: cfg.resolution
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
    const source = vtk.Filters.Sources.vtkPlaneSource.newInstance({
      origin: cfg.origin
    });
    if (cfg.normal) {
      source.setNormal(
        cfg.normal[0],
        cfg.normal[1],
        cfg.normal[2]
      );
    }
    return { output: source, isFilter: true };
  }
  function createMeshSource(cfg) {
    const polydata = vtk.Common.DataModel.vtkPolyData.newInstance();
    const pointsArray = Float32Array.from(cfg.points);
    const vtkPoints = vtk.Common.Core.vtkPoints.newInstance();
    vtkPoints.setData(pointsArray, 3);
    polydata.setPoints(vtkPoints);
    if (cfg.polys) {
      const polysArray = Uint32Array.from(cfg.polys);
      polydata.getPolys().setData(polysArray);
    }
    return { output: polydata, isFilter: false };
  }
  function createPointsSource(cfg) {
    const polydata = vtk.Common.DataModel.vtkPolyData.newInstance();
    const pointsArray = Float32Array.from(cfg.points);
    const vtkPoints = vtk.Common.Core.vtkPoints.newInstance();
    vtkPoints.setData(pointsArray, 3);
    polydata.setPoints(vtkPoints);
    return { output: polydata, isFilter: false };
  }
  function createReaderSource(cfg, readerPath, parseMethod) {
    const binary = atob(cfg.data);
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) {
      bytes[i] = binary.charCodeAt(i);
    }
    const parts = readerPath.split(".");
    let ns = vtk;
    for (let j = 0; j < parts.length; j++) {
      ns = ns[parts[j]];
    }
    const reader = ns.newInstance();
    if (parseMethod === "parseAsText") {
      reader.parseAsText(new TextDecoder().decode(bytes));
    } else {
      reader.parseAsArrayBuffer(bytes.buffer);
    }
    return { output: reader, isFilter: true };
  }
  function injectPointData(polydata, pointDataArrays) {
    if (!pointDataArrays) {
      return;
    }
    pointDataArrays.forEach((arr) => {
      const dataArray = vtk.Common.Core.vtkDataArray.newInstance({
        numberOfComponents: arr.numberOfComponents,
        values: Float32Array.from(arr.values),
        name: arr.name
      });
      polydata.getPointData().addArray(dataArray);
    });
  }
  function injectTCoords(polydata, tCoords) {
    if (!tCoords) {
      return;
    }
    const tcArray = vtk.Common.Core.vtkDataArray.newInstance({
      numberOfComponents: 2,
      values: Float32Array.from(tCoords),
      name: "TextureCoordinates"
    });
    polydata.getPointData().setTCoords(tcArray);
  }
  function setupNormals(sourceResult, normalsConfig) {
    if (!normalsConfig) {
      return sourceResult;
    }
    const normals = vtk.Filters.Core.vtkPolyDataNormals.newInstance();
    normals.setComputePointNormals(
      normalsConfig.computePointNormals
    );
    normals.setComputeCellNormals(
      normalsConfig.computeCellNormals
    );
    if (sourceResult.isFilter) {
      normals.setInputConnection(sourceResult.output.getOutputPort());
    } else {
      normals.setInputData(sourceResult.output);
    }
    return { output: normals, isFilter: true };
  }
  function setupActor(cfg, _idx, ren, renWin) {
    const sourceResult = createSource(cfg.source);
    if (!sourceResult || !sourceResult.output) {
      return;
    }
    if (cfg.source.pointData || cfg.source.tCoords) {
      let pd;
      if (sourceResult.isFilter) {
        sourceResult.output.update();
        pd = sourceResult.output.getOutputData();
      } else {
        pd = sourceResult.output;
      }
      injectPointData(pd, cfg.source.pointData);
      injectTCoords(pd, cfg.source.tCoords);
    }
    let currentResult = sourceResult;
    if (cfg.source.filters && cfg.source.filters.length > 0) {
      currentResult = applyFilters(sourceResult, cfg.source.filters);
    }
    const mapperInput = setupNormals(currentResult, cfg.normals);
    const MapperClass = cfg.actorType === "points" && cfg.renderPointsAsSpheres ? vtk.Rendering.Core.vtkSphereMapper : vtk.Rendering.Core.vtkMapper;
    const mapper = MapperClass.newInstance();
    if (mapperInput.isFilter) {
      mapper.setInputConnection(mapperInput.output.getOutputPort());
    } else {
      mapper.setInputData(mapperInput.output);
    }
    const actor = vtk.Rendering.Core.vtkActor.newInstance();
    actor.setMapper(mapper);
    actor.getProperty().setColor(cfg.color[0], cfg.color[1], cfg.color[2]);
    actor.getProperty().setOpacity(cfg.opacity);
    const styleMap = {
      surface: 2,
      wireframe: 1,
      points: 0
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
        mapper.setRadius((cfg.pointSize || 5) * 0.01);
      } else {
        actor.getProperty().setPointSize(cfg.pointSize || 5);
        actor.getProperty().setRepresentationToPoints();
      }
    }
    if (cfg.texture) {
      const texture = vtk.Rendering.Core.vtkTexture.newInstance();
      texture.setInterpolate(true);
      actor.addTexture(texture);
      const img = new Image();
      img.crossOrigin = "anonymous";
      img.onload = () => {
        texture.setImage(img);
        renWin.render();
      };
      img.src = cfg.texture.url;
    }
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
    if (camConfig.viewVector) {
      cam.setPosition(camConfig.viewVector[0], camConfig.viewVector[1], camConfig.viewVector[2]);
      cam.setViewUp(camConfig.viewUp[0], camConfig.viewUp[1], camConfig.viewUp[2]);
      cam.setFocalPoint(0, 0, 0);
      ren.resetCamera();
      ren.resetCameraClippingRange();
    }
  }
  function setupAxes(interactorObj) {
    const axes = vtk.Rendering.Core.vtkAxesActor.newInstance();
    const orientationWidget = vtk.Interaction.Widgets.vtkOrientationMarkerWidget.newInstance({
      actor: axes,
      interactor: interactorObj
    });
    orientationWidget.setEnabled(true);
    orientationWidget.setViewportCorner(
      vtk.Interaction.Widgets.vtkOrientationMarkerWidget.Corners.BOTTOM_LEFT
    );
    orientationWidget.setViewportSize(0.15);
    orientationWidget.setMinPixelSize(100);
    orientationWidget.setMaxPixelSize(300);
  }
  function setupTextActor(cfg, containerEl) {
    const div = document.createElement("div");
    div.innerText = cfg.text;
    div.style.position = "absolute";
    div.style.left = cfg.position[0] * 100 + "%";
    div.style.bottom = cfg.position[1] * 100 + "%";
    const r = Math.round(cfg.color[0] * 255);
    const g = Math.round(cfg.color[1] * 255);
    const b = Math.round(cfg.color[2] * 255);
    div.style.color = "rgba(" + r + "," + g + "," + b + "," + cfg.opacity + ")";
    div.style.fontSize = cfg.fontSize + "px";
    div.style.fontWeight = cfg.bold ? "bold" : "normal";
    div.style.fontStyle = cfg.italic ? "italic" : "normal";
    div.style.pointerEvents = "none";
    div.style.zIndex = "10";
    div.style.whiteSpace = "pre";
    div.style.textShadow = "1px 1px 2px rgba(0,0,0,0.8), -1px -1px 2px rgba(0,0,0,0.8)";
    containerEl.appendChild(div);
  }
  function applyFilters(sourceResult, filters) {
    let current = sourceResult;
    filters.forEach((f) => {
      if (f.type === "shrink") {
        current = applyShrinkFilter(current, f.shrinkFactor);
      } else if (f.type === "tube") {
        current = applyTubeFilter(current, f.radius, f.numberOfSides);
      } else if (f.type === "clip") {
        current = applyClipFilter(current, f.normal, f.origin, f.invert);
      } else if (f.type === "contour") {
        current = applyContourFilter(current, f.values, f.scalarName, f.scalarData);
      }
    });
    return current;
  }
  function applyShrinkFilter(sourceResult, shrinkFactor) {
    let inputPD;
    if (sourceResult.isFilter) {
      sourceResult.output.update();
      inputPD = sourceResult.output.getOutputData();
    } else {
      inputPD = sourceResult.output;
    }
    const inPoints = inputPD.getPoints().getData();
    const polys = inputPD.getPolys() ? inputPD.getPolys().getData() : null;
    if (!polys || polys.length === 0) {
      return sourceResult;
    }
    const newPoints = [];
    const newPolys = [];
    let offset = 0;
    let i = 0;
    while (i < polys.length) {
      const nVerts = polys[i];
      i++;
      let cx = 0, cy = 0, cz = 0;
      const indices = [];
      for (let j = 0; j < nVerts; j++) {
        const vi = polys[i + j];
        indices.push(vi);
        cx += inPoints[vi * 3];
        cy += inPoints[vi * 3 + 1];
        cz += inPoints[vi * 3 + 2];
      }
      cx /= nVerts;
      cy /= nVerts;
      cz /= nVerts;
      newPolys.push(nVerts);
      for (let k = 0; k < nVerts; k++) {
        const pi = indices[k];
        const px = inPoints[pi * 3];
        const py = inPoints[pi * 3 + 1];
        const pz = inPoints[pi * 3 + 2];
        newPoints.push(
          cx + (px - cx) * shrinkFactor,
          cy + (py - cy) * shrinkFactor,
          cz + (pz - cz) * shrinkFactor
        );
        newPolys.push(offset + k);
      }
      offset += nVerts;
      i += nVerts;
    }
    const outputPD = vtk.Common.DataModel.vtkPolyData.newInstance();
    outputPD.getPoints().setData(new Float32Array(newPoints), 3);
    outputPD.getPolys().setData(new Uint32Array(newPolys));
    return { output: outputPD, isFilter: false };
  }
  function applyTubeFilter(sourceResult, radius, numberOfSides) {
    const tubeFilter = vtk.Filters.General.vtkTubeFilter.newInstance({
      radius,
      numberOfSides
    });
    if (sourceResult.isFilter) {
      tubeFilter.setInputConnection(sourceResult.output.getOutputPort());
    } else {
      tubeFilter.setInputData(sourceResult.output);
    }
    return { output: tubeFilter, isFilter: true };
  }
  function applyClipFilter(sourceResult, normal, origin, invert) {
    const plane = vtk.Common.DataModel.vtkPlane.newInstance();
    plane.setOrigin(origin[0], origin[1], origin[2]);
    plane.setNormal(normal[0], normal[1], normal[2]);
    const clipper = vtk.Filters.General.vtkClipClosedSurface ? vtk.Filters.General.vtkClipClosedSurface.newInstance() : null;
    if (clipper) {
      clipper.setClippingPlanes([
        plane
      ]);
      if (sourceResult.isFilter) {
        clipper.setInputConnection(sourceResult.output.getOutputPort());
      } else {
        clipper.setInputData(sourceResult.output);
      }
      return { output: clipper, isFilter: true };
    }
    return applyClipManual(sourceResult, normal, origin, invert);
  }
  function applyClipManual(sourceResult, normal, origin, invert) {
    let inputPD;
    if (sourceResult.isFilter) {
      sourceResult.output.update();
      inputPD = sourceResult.output.getOutputData();
    } else {
      inputPD = sourceResult.output;
    }
    const inPoints = inputPD.getPoints().getData();
    const polys = inputPD.getPolys() ? inputPD.getPolys().getData() : null;
    if (!polys || polys.length === 0) {
      return sourceResult;
    }
    const nx = normal[0], ny = normal[1], nz = normal[2];
    const ox = origin[0], oy = origin[1], oz = origin[2];
    const newPoints = [];
    const newPolys = [];
    const pointMap = {};
    let nextIdx = 0;
    let i = 0;
    while (i < polys.length) {
      const nVerts = polys[i];
      i++;
      let cx = 0, cy = 0, cz = 0;
      const cellIndices = [];
      for (let j = 0; j < nVerts; j++) {
        const vi = polys[i + j];
        cellIndices.push(vi);
        cx += inPoints[vi * 3];
        cy += inPoints[vi * 3 + 1];
        cz += inPoints[vi * 3 + 2];
      }
      cx /= nVerts;
      cy /= nVerts;
      cz /= nVerts;
      const dot = (cx - ox) * nx + (cy - oy) * ny + (cz - oz) * nz;
      const keep = invert ? dot >= 0 : dot <= 0;
      if (keep) {
        newPolys.push(nVerts);
        for (let k = 0; k < nVerts; k++) {
          const pi = cellIndices[k];
          if (pointMap[pi] === void 0) {
            pointMap[pi] = nextIdx++;
            newPoints.push(inPoints[pi * 3], inPoints[pi * 3 + 1], inPoints[pi * 3 + 2]);
          }
          newPolys.push(pointMap[pi]);
        }
      }
      i += nVerts;
    }
    const outputPD = vtk.Common.DataModel.vtkPolyData.newInstance();
    outputPD.getPoints().setData(new Float32Array(newPoints), 3);
    outputPD.getPolys().setData(new Uint32Array(newPolys));
    return { output: outputPD, isFilter: false };
  }
  function applyContourFilter(sourceResult, values, scalarName, scalarData) {
    let inputPD;
    if (sourceResult.isFilter) {
      sourceResult.output.update();
      inputPD = sourceResult.output.getOutputData();
    } else {
      inputPD = sourceResult.output;
    }
    const scalars = vtk.Common.Core.vtkDataArray.newInstance({
      numberOfComponents: 1,
      values: Float32Array.from(scalarData),
      name: scalarName
    });
    inputPD.getPointData().addArray(scalars);
    inputPD.getPointData().setActiveScalars(scalarName);
    if (vtk.Filters.General && vtk.Filters.General.vtkContourTriangulator) {
    }
    return applyContourManual(inputPD, values, scalarName);
  }
  function applyContourManual(inputPD, values, scalarName) {
    const inPoints = inputPD.getPoints().getData();
    const polys = inputPD.getPolys() ? inputPD.getPolys().getData() : null;
    const scalarsArr = inputPD.getPointData().getArrayByName(scalarName);
    if (!polys || !scalarsArr) {
      return { output: inputPD, isFilter: false };
    }
    const scalarValues = scalarsArr.getData();
    const outPoints = [];
    const outPolys = [];
    let pointIdx = 0;
    let i = 0;
    while (i < polys.length) {
      const nVerts = polys[i];
      i++;
      if (nVerts === 3) {
        const i0 = polys[i], i1 = polys[i + 1], i2 = polys[i + 2];
        const s0 = scalarValues[i0], s1 = scalarValues[i1], s2 = scalarValues[i2];
        const tri = [
          [i0, i1, s0, s1],
          [i1, i2, s1, s2],
          [i2, i0, s2, s0]
        ];
        values.forEach((val) => {
          const edgePoints = [];
          tri.forEach((edge) => {
            const sa = edge[2], sb = edge[3];
            if (sa <= val && val < sb || sb <= val && val < sa) {
              const t = (val - sa) / (sb - sa);
              const ai = edge[0], bi = edge[1];
              edgePoints.push(
                inPoints[ai * 3] + t * (inPoints[bi * 3] - inPoints[ai * 3]),
                inPoints[ai * 3 + 1] + t * (inPoints[bi * 3 + 1] - inPoints[ai * 3 + 1]),
                inPoints[ai * 3 + 2] + t * (inPoints[bi * 3 + 2] - inPoints[ai * 3 + 2])
              );
            }
          });
          if (edgePoints.length === 6) {
            outPoints.push(edgePoints[0], edgePoints[1], edgePoints[2]);
            outPoints.push(edgePoints[3], edgePoints[4], edgePoints[5]);
            outPolys.push(2, pointIdx, pointIdx + 1);
            pointIdx += 2;
          }
        });
      }
      i += nVerts;
    }
    const outputPD = vtk.Common.DataModel.vtkPolyData.newInstance();
    if (outPoints.length > 0) {
      outputPD.getPoints().setData(new Float32Array(outPoints), 3);
      outputPD.getLines().setData(new Uint32Array(outPolys));
    }
    return { output: outputPD, isFilter: false };
  }
})();
