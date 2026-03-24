/**
 * pyvista-js renderer — reads scene configuration from JSON and creates
 * vtk.js objects. No Jinja template variables are used in this file.
 */
(function () {
  "use strict";

  // In JupyterLite path, _generate_render_js() sets __pvjsSceneData and
  // __pvjsContainer before calling this code. In standalone HTML path,
  // read from the DOM.
  var sceneData =
    typeof __pvjsSceneData !== "undefined"
      ? __pvjsSceneData
      : JSON.parse(document.getElementById("scene-data").textContent);
  var container =
    typeof __pvjsContainer !== "undefined"
      ? __pvjsContainer
      : document.getElementById(sceneData.containerId);
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

  // Store for later use
  window.renderer = renderer;
  window.renderWindow = renderWindow;
  window.openGLRenderWindow = openGLRenderWindow;
  window.interactor = interactor;

  // --- Lights ---
  if (sceneData.lightingMode === null && (!sceneData.lights || sceneData.lights.length === 0)) {
    // lighting=None with no custom lights: disable all lighting
    renderer.removeAllLights();
    renderer.setAutomaticLightCreation(false);
  } else {
    setupLights(sceneData.lights, renderer);
  }

  // --- Actors ---
  sceneData.actors.forEach(function (actorConfig, idx) {
    setupActor(actorConfig, idx, renderer, renderWindow);
  });

  // --- Text Actors ---
  if (sceneData.textActors) {
    sceneData.textActors.forEach(function (textConfig) {
      setupTextActor(textConfig, container);
    });
  }

  // --- Axes ---
  if (sceneData.axes) {
    setupAxes(interactor);
  }

  // --- Camera ---
  renderer.resetCamera();
  if (sceneData.camera) {
    setupCamera(renderer, sceneData.camera);
  }

  renderWindow.render();

  // ========== Helper functions ==========

  function setupLights(lightsConfig, ren) {
    if (!lightsConfig || lightsConfig.length === 0) {
      return;
    }
    ren.removeAllLights();
    ren.setAutomaticLightCreation(false);
    lightsConfig.forEach(function (cfg) {
      var light = vtk.Rendering.Core.vtkLight.newInstance();
      var typeMap = {
        scene: "setLightTypeToSceneLight",
        camera: "setLightTypeToCameraLight",
        head: "setLightTypeToHeadLight",
      };
      var setter = typeMap[cfg.type] || "setLightTypeToSceneLight";
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
        cfg.attenuationValues[2],
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
    var source = vtk.Filters.Sources.vtkSphereSource.newInstance({
      center: cfg.center,
      radius: cfg.radius,
      thetaResolution: cfg.thetaResolution,
      phiResolution: cfg.phiResolution,
    });
    var texMap = vtk.Filters.Texture.vtkTextureMapToSphere.newInstance();
    texMap.setInputConnection(source.getOutputPort());
    return { output: texMap, isFilter: true };
  }

  function createConeSource(cfg) {
    var source = vtk.Filters.Sources.vtkConeSource.newInstance({
      height: cfg.height,
      radius: cfg.radius,
      resolution: cfg.resolution,
    });
    return { output: source, isFilter: true };
  }

  function createCubeSource(cfg) {
    var source = vtk.Filters.Sources.vtkCubeSource.newInstance({
      xLength: cfg.xLength,
      yLength: cfg.yLength,
      zLength: cfg.zLength,
    });
    return { output: source, isFilter: false };
  }

  function createCylinderSource(cfg) {
    var source = vtk.Filters.Sources.vtkCylinderSource.newInstance({
      height: cfg.height,
      radius: cfg.radius,
      resolution: cfg.resolution,
    });
    return { output: source, isFilter: true };
  }

  function createDiskSource(cfg) {
    var source = vtk.Filters.Sources.vtkDiskSource
      ? vtk.Filters.Sources.vtkDiskSource.newInstance({
          innerRadius: cfg.innerRadius,
          outerRadius: cfg.outerRadius,
          radialResolution: 1,
          circumferentialResolution: cfg.resolution,
        })
      : null;
    return { output: source, isFilter: true };
  }

  function createCircleSource(cfg) {
    // Circle is a disk with innerRadius=0
    return createDiskSource({
      innerRadius: 0,
      outerRadius: cfg.radius,
      resolution: cfg.resolution,
    });
  }

  function createArrowSource(cfg) {
    var source = vtk.Filters.Sources.vtkArrowSource.newInstance({
      tipLength: cfg.tipLength,
      tipRadius: cfg.tipRadius,
      shaftRadius: cfg.shaftRadius,
    });
    return { output: source, isFilter: true };
  }

  function createLineSource(cfg) {
    var source = vtk.Filters.Sources.vtkLineSource.newInstance({
      point1: cfg.point1,
      point2: cfg.point2,
    });
    return { output: source, isFilter: true };
  }

  function createPlaneSource(cfg) {
    var source = vtk.Filters.Sources.vtkPlaneSource.newInstance({
      origin: cfg.origin,
    });
    if (cfg.normal) {
      source.setNormal(cfg.normal[0], cfg.normal[1], cfg.normal[2]);
    }
    return { output: source, isFilter: true };
  }

  function createMeshSource(cfg) {
    var polydata = vtk.Common.DataModel.vtkPolyData.newInstance();
    var pointsArray = Float32Array.from(cfg.points);
    var vtkPoints = vtk.Common.Core.vtkPoints.newInstance();
    vtkPoints.setData(pointsArray, 3);
    polydata.setPoints(vtkPoints);
    if (cfg.polys) {
      var polysArray = Uint32Array.from(cfg.polys);
      polydata.getPolys().setData(polysArray);
    }
    return { output: polydata, isFilter: false };
  }

  function createPointsSource(cfg) {
    var polydata = vtk.Common.DataModel.vtkPolyData.newInstance();
    var pointsArray = Float32Array.from(cfg.points);
    var vtkPoints = vtk.Common.Core.vtkPoints.newInstance();
    vtkPoints.setData(pointsArray, 3);
    polydata.setPoints(vtkPoints);
    return { output: polydata, isFilter: false };
  }

  function createReaderSource(cfg, readerPath, parseMethod) {
    // Decode base64 data and parse with vtk.js reader
    var binary = atob(cfg.data);
    var bytes = new Uint8Array(binary.length);
    for (var i = 0; i < binary.length; i++) {
      bytes[i] = binary.charCodeAt(i);
    }
    // Navigate to the correct vtk.js namespace
    var parts = readerPath.split(".");
    var ns = vtk;
    for (var j = 0; j < parts.length; j++) {
      ns = ns[parts[j]];
    }
    var reader = ns.newInstance();
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
    pointDataArrays.forEach(function (arr) {
      var dataArray = vtk.Common.Core.vtkDataArray.newInstance({
        numberOfComponents: arr.numberOfComponents,
        values: Float32Array.from(arr.values),
        name: arr.name,
      });
      polydata.getPointData().addArray(dataArray);
    });
  }

  function injectTCoords(polydata, tCoords) {
    if (!tCoords) {
      return;
    }
    var tcArray = vtk.Common.Core.vtkDataArray.newInstance({
      numberOfComponents: 2,
      values: Float32Array.from(tCoords),
      name: "TextureCoordinates",
    });
    polydata.getPointData().setTCoords(tcArray);
  }

  function setupNormals(sourceResult, normalsConfig) {
    if (!normalsConfig) {
      return sourceResult;
    }
    var normals = vtk.Filters.Core.vtkPolyDataNormals.newInstance();
    normals.setComputePointNormals(normalsConfig.computePointNormals);
    normals.setComputeCellNormals(normalsConfig.computeCellNormals);
    if (sourceResult.isFilter) {
      normals.setInputConnection(sourceResult.output.getOutputPort());
    } else {
      normals.setInputData(sourceResult.output);
    }
    return { output: normals, isFilter: true };
  }

  function setupActor(cfg, idx, ren, renWin) {
    var sourceResult = createSource(cfg.source);
    if (!sourceResult || !sourceResult.output) {
      return;
    }

    // Inject point data and texture coordinates if needed
    if (cfg.source.pointData || cfg.source.tCoords) {
      var pd;
      if (sourceResult.isFilter) {
        sourceResult.output.update();
        pd = sourceResult.output.getOutputData();
      } else {
        pd = sourceResult.output;
      }
      injectPointData(pd, cfg.source.pointData);
      injectTCoords(pd, cfg.source.tCoords);
    }

    // Apply filters (shrink, clip, tube, contour)
    if (cfg.source.filters && cfg.source.filters.length > 0) {
      sourceResult = applyFilters(sourceResult, cfg.source.filters);
    }

    // Normals
    var mapperInput = setupNormals(sourceResult, cfg.normals);

    // Mapper
    var MapperClass =
      cfg.actorType === "points" && cfg.renderPointsAsSpheres
        ? vtk.Rendering.Core.vtkSphereMapper
        : vtk.Rendering.Core.vtkMapper;
    var mapper = MapperClass.newInstance();
    if (mapperInput.isFilter) {
      mapper.setInputConnection(mapperInput.output.getOutputPort());
    } else {
      mapper.setInputData(mapperInput.output);
    }

    // Actor
    var actor = vtk.Rendering.Core.vtkActor.newInstance();
    actor.setMapper(mapper);
    actor.getProperty().setColor(cfg.color[0], cfg.color[1], cfg.color[2]);
    actor.getProperty().setOpacity(cfg.opacity);

    // Style
    var styleMap = { surface: 2, wireframe: 1, points: 0 };
    var rep = styleMap[cfg.style];
    if (rep !== undefined) {
      actor.getProperty().setRepresentation(rep);
    }

    // Shading
    if (cfg.shading === "gouraud") {
      actor.getProperty().setInterpolationToGouraud();
    } else if (cfg.shading === "flat") {
      actor.getProperty().setInterpolationToFlat();
    }

    // Edges
    if (cfg.edges) {
      actor.getProperty().setEdgeVisibility(true);
      actor.getProperty().setEdgeColor(cfg.edges.color[0], cfg.edges.color[1], cfg.edges.color[2]);
    }

    // PBR
    if (cfg.pbr) {
      actor.getProperty().setInterpolationToPhong();
      var m = cfg.pbr.metallic;
      var r = cfg.pbr.roughness;
      actor.getProperty().setMetallic(m);
      actor.getProperty().setRoughness(r);
      actor.getProperty().setAmbient(0.1);
      actor.getProperty().setSpecular(0.75 * m + 0.25);
      actor.getProperty().setSpecularPower(Math.max(1, 100 * (1 - r)));
      actor.getProperty().setDiffuse(0.65 + 0.35 * (1 - m));
    }

    // Point cloud specific
    if (cfg.actorType === "points") {
      if (cfg.renderPointsAsSpheres && mapper.setRadius) {
        mapper.setRadius((cfg.pointSize || 5) * 0.01);
      } else {
        actor.getProperty().setPointSize(cfg.pointSize || 5);
        actor.getProperty().setRepresentationToPoints();
      }
    }

    // Texture
    if (cfg.texture) {
      var texture = vtk.Rendering.Core.vtkTexture.newInstance();
      texture.setInterpolate(true);
      actor.addTexture(texture);
      var img = new Image();
      img.crossOrigin = "anonymous";
      img.onload = function () {
        texture.setImage(img);
        renWin.render();
      };
      img.src = cfg.texture.url;
    }

    ren.addActor(actor);
  }

  function setupCamera(ren, camConfig) {
    var cam = ren.getActiveCamera();
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
    if (camConfig.viewVector) {
      cam.setPosition(camConfig.viewVector[0], camConfig.viewVector[1], camConfig.viewVector[2]);
      cam.setViewUp(camConfig.viewUp[0], camConfig.viewUp[1], camConfig.viewUp[2]);
      cam.setFocalPoint(0, 0, 0);
      ren.resetCamera();
      ren.resetCameraClippingRange();
    }
  }

  function setupAxes(interactorObj) {
    var axes = vtk.Rendering.Core.vtkAxesActor.newInstance();
    var orientationWidget = vtk.Interaction.Widgets.vtkOrientationMarkerWidget.newInstance({
      actor: axes,
      interactor: interactorObj,
    });
    orientationWidget.setEnabled(true);
    orientationWidget.setViewportCorner(
      vtk.Interaction.Widgets.vtkOrientationMarkerWidget.Corners.BOTTOM_LEFT,
    );
    orientationWidget.setViewportSize(0.15);
    orientationWidget.setMinPixelSize(100);
    orientationWidget.setMaxPixelSize(300);
  }

  function setupTextActor(cfg, containerEl) {
    var div = document.createElement("div");
    div.innerText = cfg.text;
    div.style.position = "absolute";
    div.style.left = cfg.position[0] * 100 + "%";
    div.style.bottom = cfg.position[1] * 100 + "%";
    var r = Math.round(cfg.color[0] * 255);
    var g = Math.round(cfg.color[1] * 255);
    var b = Math.round(cfg.color[2] * 255);
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
    var current = sourceResult;
    filters.forEach(function (f) {
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
    // vtk.js does not have vtkShrinkFilter, so implement manually:
    // For each cell, move vertices toward the cell centroid.
    var inputPD;
    if (sourceResult.isFilter) {
      sourceResult.output.update();
      inputPD = sourceResult.output.getOutputData();
    } else {
      inputPD = sourceResult.output;
    }
    var inPoints = inputPD.getPoints().getData();
    var polys = inputPD.getPolys ? inputPD.getPolys().getData() : null;
    if (!polys || polys.length === 0) {
      return sourceResult;
    }

    // Build new points: each cell gets its own copy of vertices
    var newPoints = [];
    var newPolys = [];
    var offset = 0;
    var i = 0;
    while (i < polys.length) {
      var nVerts = polys[i];
      i++;
      // Compute centroid
      var cx = 0,
        cy = 0,
        cz = 0;
      var indices = [];
      for (var j = 0; j < nVerts; j++) {
        var vi = polys[i + j];
        indices.push(vi);
        cx += inPoints[vi * 3];
        cy += inPoints[vi * 3 + 1];
        cz += inPoints[vi * 3 + 2];
      }
      cx /= nVerts;
      cy /= nVerts;
      cz /= nVerts;
      // Shrink vertices toward centroid
      newPolys.push(nVerts);
      for (var k = 0; k < nVerts; k++) {
        var pi = indices[k];
        var px = inPoints[pi * 3];
        var py = inPoints[pi * 3 + 1];
        var pz = inPoints[pi * 3 + 2];
        newPoints.push(
          cx + (px - cx) * shrinkFactor,
          cy + (py - cy) * shrinkFactor,
          cz + (pz - cz) * shrinkFactor,
        );
        newPolys.push(offset + k);
      }
      offset += nVerts;
      i += nVerts;
    }

    var outputPD = vtk.Common.DataModel.vtkPolyData.newInstance();
    outputPD.getPoints().setData(new Float32Array(newPoints), 3);
    outputPD.getPolys().setData(new Uint32Array(newPolys));
    return { output: outputPD, isFilter: false };
  }

  function applyTubeFilter(sourceResult, radius, numberOfSides) {
    var tubeFilter = vtk.Filters.General.vtkTubeFilter.newInstance({
      radius: radius,
      numberOfSides: numberOfSides,
    });
    if (sourceResult.isFilter) {
      tubeFilter.setInputConnection(sourceResult.output.getOutputPort());
    } else {
      tubeFilter.setInputData(sourceResult.output);
    }
    return { output: tubeFilter, isFilter: true };
  }

  function applyClipFilter(sourceResult, normal, origin, invert) {
    var plane = vtk.Common.DataModel.vtkPlane.newInstance();
    plane.setOrigin(origin[0], origin[1], origin[2]);
    plane.setNormal(normal[0], normal[1], normal[2]);

    var clipper = vtk.Filters.General.vtkClipClosedSurface
      ? vtk.Filters.General.vtkClipClosedSurface.newInstance()
      : null;
    if (clipper) {
      clipper.setClippingPlanes([plane]);
      if (sourceResult.isFilter) {
        clipper.setInputConnection(sourceResult.output.getOutputPort());
      } else {
        clipper.setInputData(sourceResult.output);
      }
      return { output: clipper, isFilter: true };
    }
    // Fallback: manual clip by discarding cells on one side of the plane
    return applyClipManual(sourceResult, normal, origin, invert);
  }

  function applyClipManual(sourceResult, normal, origin, invert) {
    var inputPD;
    if (sourceResult.isFilter) {
      sourceResult.output.update();
      inputPD = sourceResult.output.getOutputData();
    } else {
      inputPD = sourceResult.output;
    }
    var inPoints = inputPD.getPoints().getData();
    var polys = inputPD.getPolys ? inputPD.getPolys().getData() : null;
    if (!polys || polys.length === 0) {
      return sourceResult;
    }
    var nx = normal[0],
      ny = normal[1],
      nz = normal[2];
    var ox = origin[0],
      oy = origin[1],
      oz = origin[2];

    // Keep cells whose centroid is on the correct side of the plane
    var newPoints = [];
    var newPolys = [];
    var pointMap = {};
    var nextIdx = 0;
    var i = 0;
    while (i < polys.length) {
      var nVerts = polys[i];
      i++;
      // Compute centroid
      var cx = 0,
        cy = 0,
        cz = 0;
      var cellIndices = [];
      for (var j = 0; j < nVerts; j++) {
        var vi = polys[i + j];
        cellIndices.push(vi);
        cx += inPoints[vi * 3];
        cy += inPoints[vi * 3 + 1];
        cz += inPoints[vi * 3 + 2];
      }
      cx /= nVerts;
      cy /= nVerts;
      cz /= nVerts;
      var dot = (cx - ox) * nx + (cy - oy) * ny + (cz - oz) * nz;
      var keep = invert ? dot >= 0 : dot <= 0;
      if (keep) {
        newPolys.push(nVerts);
        for (var k = 0; k < nVerts; k++) {
          var pi = cellIndices[k];
          if (pointMap[pi] === undefined) {
            pointMap[pi] = nextIdx++;
            newPoints.push(inPoints[pi * 3], inPoints[pi * 3 + 1], inPoints[pi * 3 + 2]);
          }
          newPolys.push(pointMap[pi]);
        }
      }
      i += nVerts;
    }

    var outputPD = vtk.Common.DataModel.vtkPolyData.newInstance();
    outputPD.getPoints().setData(new Float32Array(newPoints), 3);
    outputPD.getPolys().setData(new Uint32Array(newPolys));
    return { output: outputPD, isFilter: false };
  }

  function applyContourFilter(sourceResult, values, scalarName, scalarData) {
    // Inject scalar data, then use vtk.js contour filter if available
    var inputPD;
    if (sourceResult.isFilter) {
      sourceResult.output.update();
      inputPD = sourceResult.output.getOutputData();
    } else {
      inputPD = sourceResult.output;
    }

    // Add scalar array to polydata
    var scalars = vtk.Common.Core.vtkDataArray.newInstance({
      numberOfComponents: 1,
      values: Float32Array.from(scalarData),
      name: scalarName,
    });
    inputPD.getPointData().addArray(scalars);
    inputPD.getPointData().setActiveScalars(scalarName);

    // Try vtk.js built-in contour filter
    if (vtk.Filters.General && vtk.Filters.General.vtkContourTriangulator) {
      // vtk.js doesn't have a standard marching-cubes contour for polydata,
      // fall back to manual isocontour extraction
    }

    // Manual contour: for each contour value, extract iso-lines from triangles
    // using marching triangles (linear interpolation on edges)
    return applyContourManual(inputPD, values, scalarName);
  }

  function applyContourManual(inputPD, values, scalarName) {
    var inPoints = inputPD.getPoints().getData();
    var polys = inputPD.getPolys ? inputPD.getPolys().getData() : null;
    var scalarsArr = inputPD.getPointData().getArrayByName(scalarName);
    if (!polys || !scalarsArr) {
      return { output: inputPD, isFilter: false };
    }
    var scalarValues = scalarsArr.getData();

    var outPoints = [];
    var outPolys = [];
    var pointIdx = 0;

    // For each triangle, for each contour value, extract intersection edges
    var i = 0;
    while (i < polys.length) {
      var nVerts = polys[i];
      i++;
      if (nVerts === 3) {
        var i0 = polys[i],
          i1 = polys[i + 1],
          i2 = polys[i + 2];
        var s0 = scalarValues[i0],
          s1 = scalarValues[i1],
          s2 = scalarValues[i2];
        var tri = [
          [i0, i1, s0, s1],
          [i1, i2, s1, s2],
          [i2, i0, s2, s0],
        ];
        values.forEach(function (val) {
          var edgePoints = [];
          tri.forEach(function (edge) {
            var sa = edge[2],
              sb = edge[3];
            if ((sa <= val && val < sb) || (sb <= val && val < sa)) {
              var t = (val - sa) / (sb - sa);
              var ai = edge[0],
                bi = edge[1];
              edgePoints.push(
                inPoints[ai * 3] + t * (inPoints[bi * 3] - inPoints[ai * 3]),
                inPoints[ai * 3 + 1] + t * (inPoints[bi * 3 + 1] - inPoints[ai * 3 + 1]),
                inPoints[ai * 3 + 2] + t * (inPoints[bi * 3 + 2] - inPoints[ai * 3 + 2]),
              );
            }
          });
          // If we found exactly 2 intersection points, create a line segment
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

    var outputPD = vtk.Common.DataModel.vtkPolyData.newInstance();
    if (outPoints.length > 0) {
      outputPD.getPoints().setData(new Float32Array(outPoints), 3);
      outputPD.getLines().setData(new Uint32Array(outPolys));
    }
    return { output: outputPD, isFilter: false };
  }
})();
