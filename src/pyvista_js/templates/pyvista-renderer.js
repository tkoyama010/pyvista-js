/**
 * pyvista-js renderer — reads scene configuration from JSON and creates
 * vtk.js objects. No Jinja template variables are used in this file.
 */
(function () {
  "use strict";

  // Find scene-data element: try unique ID first (JupyterLite path),
  // then fall back to fixed "scene-data" ID (standalone HTML path).
  var sceneDataEl = null;
  var jsonScripts = document.querySelectorAll('script[type="application/json"]');
  for (var i = jsonScripts.length - 1; i >= 0; i--) {
    if (jsonScripts[i].id && jsonScripts[i].id.startsWith("scene-data")) {
      sceneDataEl = jsonScripts[i];
      break;
    }
  }
  var sceneData = JSON.parse(sceneDataEl.textContent);
  var container = document.getElementById(sceneData.containerId);
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
  if (sceneData.lightingMode === null) {
    renderer.removeAllLights();
    renderer.setAutomaticLightCreation(false);
  } else {
    setupLights(sceneData.lights, renderer);
  }

  // --- Actors ---
  sceneData.actors.forEach(function (actorConfig, idx) {
    setupActor(actorConfig, idx, renderer, renderWindow);
  });

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
      vtk.Interaction.Widgets.vtkOrientationMarkerWidget.Corners.BOTTOM_LEFT
    );
    orientationWidget.setViewportSize(0.15);
    orientationWidget.setMinPixelSize(100);
    orientationWidget.setMaxPixelSize(300);
  }
})();
