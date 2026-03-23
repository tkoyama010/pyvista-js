/**
 * Core viewer initialization function for pyvista-js
 *
 * This module provides the `initViewer` function that initializes a vtk.js
 * viewer from a configuration object. It supports both:
 * 1. Server-side mode: Config injected via Jinja2 templates
 * 2. WASM mode: Config passed programmatically from Python/Pyodide
 */

/**
 * Initialize a pyvista-js viewer with the given configuration
 *
 * @param config - Viewer configuration object
 * @returns Object containing renderer, renderWindow, and interactor instances
 */
function initViewer(config) {
  // Validate vtk.js is available
  if (typeof vtk === "undefined") {
    throw new Error("vtk.js library is not loaded. Please include the vtk.js script before calling initViewer.");
  }

  // Get the container element
  const container = document.getElementById(config.containerId);
  if (!container) {
    throw new Error(`Container element with id '${config.containerId}' not found.`);
  }

  // Set default values
  const backgroundColor = config.backgroundColor || { r: 1, g: 1, b: 1 };
  const width = config.width || 600;
  const height = config.height || 400;

  // Create renderer
  const renderer = vtk.Rendering.Core.vtkRenderer.newInstance();
  renderer.setBackground(backgroundColor.r, backgroundColor.g, backgroundColor.b);

  // Create render window
  const renderWindow = vtk.Rendering.Core.vtkRenderWindow.newInstance();
  renderWindow.addRenderer(renderer);

  // Create OpenGL render window
  const openGLRenderWindow = vtk.Rendering.OpenGL.vtkRenderWindow.newInstance();
  renderWindow.addView(openGLRenderWindow);
  openGLRenderWindow.setContainer(container);

  // Set size from container or config
  const bbox = container.getBoundingClientRect();
  openGLRenderWindow.setSize(bbox.width || width, bbox.height || height);

  // Create interactor
  const interactor = vtk.Rendering.Core.vtkRenderWindowInteractor.newInstance();
  const interactorStyle = vtk.Interaction.Style.vtkInteractorStyleTrackballCamera.newInstance();
  interactor.setInteractorStyle(interactorStyle);
  interactor.setView(openGLRenderWindow);
  interactor.initialize();
  interactor.bindEvents(container);

  // Add lights
  if (config.lights && config.lights.length > 0) {
    renderer.setAutomaticLightCreation(false);
    config.lights.forEach((lightConfig) => {
      const light = vtk.Rendering.Core.vtkLight.newInstance();

      if (lightConfig.position) {
        light.setPosition(lightConfig.position.x, lightConfig.position.y, lightConfig.position.z);
      }
      if (lightConfig.focalPoint) {
        light.setFocalPoint(lightConfig.focalPoint.x, lightConfig.focalPoint.y, lightConfig.focalPoint.z);
      }
      if (lightConfig.intensity !== undefined) {
        light.setIntensity(lightConfig.intensity);
      }
      if (lightConfig.color) {
        light.setColor(lightConfig.color.r, lightConfig.color.g, lightConfig.color.b);
      }

      renderer.addLight(light);
    });
  }

  // Add actors
  if (config.actors && config.actors.length > 0) {
    config.actors.forEach((actorConfig, index) => {
      try {
        // Execute the source code to create the vtk.js data source
        // The source code should define a variable called '_source'
        const sourceVarName = `_source${index}`;
        const mapperVarName = `mapper${index}`;
        const actorVarName = `actor${index}`;

        // Create a context for executing the source code
        const sourceCode = actorConfig.sourceCode.replace(/_source/g, sourceVarName);
        eval(sourceCode);
        const source = eval(sourceVarName);

        // Create mapper
        const mapperClass = actorConfig.mapperClass || "vtkMapper";
        const mapper = vtk.Rendering.Core[mapperClass].newInstance();

        // Execute normals code if provided
        if (actorConfig.normalsCode) {
          const normalsCode = actorConfig.normalsCode
            .replace(/_source/g, sourceVarName)
            .replace(/{{ MAPPER }}/g, mapperVarName);
          eval(normalsCode);
        } else {
          // Default: connect source to mapper
          if (source.getOutputPort) {
            mapper.setInputConnection(source.getOutputPort());
          } else {
            mapper.setInputData(source);
          }
        }

        // Execute mapper setup if provided
        if (actorConfig.mapperSetup) {
          const mapperSetup = actorConfig.mapperSetup.replace(/{{ MAPPER }}/g, mapperVarName);
          eval(mapperSetup);
        }

        // Execute scalar code if provided
        if (actorConfig.scalarCode) {
          const scalarCode = actorConfig.scalarCode.replace(/{{ MAPPER }}/g, mapperVarName);
          eval(scalarCode);
        }

        // Create actor
        const actor = vtk.Rendering.Core.vtkActor.newInstance();
        eval(`${actorVarName} = actor`);
        actor.setMapper(mapper);

        // Set color and opacity
        const color = actorConfig.color || { r: 0.5, g: 0.5, b: 0.5 };
        const opacity = actorConfig.opacity !== undefined ? actorConfig.opacity : 1.0;
        actor.getProperty().setColor(color.r, color.g, color.b);
        actor.getProperty().setOpacity(opacity);

        // Set rendering style
        if (actorConfig.style === "wireframe") {
          actor.getProperty().setRepresentationToWireframe();
        } else if (actorConfig.style === "points") {
          actor.getProperty().setRepresentationToPoints();
          actor.getProperty().setPointSize(5);
        }

        // Set edge visibility
        if (actorConfig.showEdges) {
          actor.getProperty().setEdgeVisibility(true);
          if (actorConfig.edgeColor) {
            actor.getProperty().setEdgeColor(
              actorConfig.edgeColor.r,
              actorConfig.edgeColor.g,
              actorConfig.edgeColor.b
            );
          }
        }

        // Set shading
        if (actorConfig.smoothShading !== undefined) {
          actor.getProperty().setInterpolation(actorConfig.smoothShading ? 1 : 0);
        }

        // Set PBR properties
        if (actorConfig.pbr) {
          actor.getProperty().setInterpolationToPhong();
          if (actorConfig.metallic !== undefined) {
            actor.getProperty().setMetallic(actorConfig.metallic);
          }
          if (actorConfig.roughness !== undefined) {
            actor.getProperty().setRoughness(actorConfig.roughness);
          }
        }

        // Execute texture code if provided
        if (actorConfig.textureCode) {
          const textureCode = actorConfig.textureCode
            .replace(/{{ ACTOR }}/g, actorVarName)
            .replace(/renderer/g, "renderer");
          eval(textureCode);
        }

        // Add actor to renderer
        renderer.addActor(actor);
      } catch (e) {
        console.error(`Error creating actor ${index}:`, e);
      }
    });
  }

  // Add scalar bar if configured
  if (config.scalarBar) {
    try {
      const scalarBarActor = vtk.Rendering.Core.vtkScalarBarActor.newInstance();
      renderer.addActor(scalarBarActor);
    } catch (e) {
      console.error("Error creating scalar bar:", e);
    }
  }

  // Add text actors if configured
  if (config.textActors && config.textActors.length > 0) {
    config.textActors.forEach((textConfig, index) => {
      try {
        const textActor = vtk.Rendering.Core.vtkActor2D.newInstance();
        const textMapper = vtk.Rendering.Core.vtkTextMapper.newInstance();
        textMapper.setInput(textConfig.text);
        textActor.setMapper(textMapper);

        if (textConfig.position) {
          textActor.setPosition(textConfig.position.x, textConfig.position.y);
        }

        const textProperty = textMapper.getTextProperty();
        if (textConfig.fontSize) {
          textProperty.setFontSize(textConfig.fontSize);
        }
        if (textConfig.color) {
          textProperty.setColor(textConfig.color.r, textConfig.color.g, textConfig.color.b);
        }

        renderer.addActor2D(textActor);
      } catch (e) {
        console.error(`Error creating text actor ${index}:`, e);
      }
    });
  }

  // Set environment texture if configured
  if (config.environment && config.environment.textureUrl) {
    try {
      renderer.setEnvironmentTexture(config.environment.textureUrl);
    } catch (e) {
      console.error("Error setting environment texture:", e);
    }
  }

  // Add axes if configured
  if (config.axes && config.axes.enabled) {
    // Axes implementation would go here
    // This is a placeholder as the original code doesn't show axes implementation
  }

  // Reset camera
  renderer.resetCamera();

  // Set camera if configured
  if (config.camera) {
    const camera = renderer.getActiveCamera();
    if (config.camera.position) {
      camera.setPosition(
        config.camera.position.x,
        config.camera.position.y,
        config.camera.position.z
      );
    }
    if (config.camera.focalPoint) {
      camera.setFocalPoint(
        config.camera.focalPoint.x,
        config.camera.focalPoint.y,
        config.camera.focalPoint.z
      );
    }
    if (config.camera.viewUp) {
      camera.setViewUp(
        config.camera.viewUp.x,
        config.camera.viewUp.y,
        config.camera.viewUp.z
      );
    }
    if (config.camera.viewAngle !== undefined) {
      camera.setViewAngle(config.camera.viewAngle);
    }
    if (config.camera.parallelProjection !== undefined) {
      camera.setParallelProjection(config.camera.parallelProjection);
    }
  }

  // Render the scene
  renderWindow.render();

  // Return the viewer components for external access
  return {
    renderer,
    renderWindow,
    interactor,
  };
}

// Export for module usage (WASM mode)
if (typeof module !== "undefined" && module.exports) {
  module.exports = { initViewer };
}

// Make available globally for server mode
if (typeof window !== "undefined") {
  window.initViewer = initViewer;
}
