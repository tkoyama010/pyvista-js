import vtkRenderer from "@kitware/vtk.js/Rendering/Core/Renderer";
import vtkRenderWindow from "@kitware/vtk.js/Rendering/Core/RenderWindow";
import vtkRenderWindowInteractor from "@kitware/vtk.js/Rendering/Core/RenderWindowInteractor";
import vtkInteractorStyleTrackballCamera from "@kitware/vtk.js/Interaction/Style/InteractorStyleTrackballCamera";
import vtkOpenGLRenderWindow from "@kitware/vtk.js/Rendering/OpenGL/RenderWindow";
import vtkActor from "@kitware/vtk.js/Rendering/Core/Actor";
import vtkMapper from "@kitware/vtk.js/Rendering/Core/Mapper";

export interface RenderingContext {
  renderer: any;
  renderWindow: any;
  openGLRenderWindow: any;
  interactor: any;
  interactorStyle: any;
}

export function initializeRenderer(
  container: HTMLElement,
  backgroundColor: [number, number, number]
): RenderingContext {
  const renderer = vtkRenderer.newInstance();
  renderer.setBackground(...backgroundColor);

  const renderWindow = vtkRenderWindow.newInstance();
  renderWindow.addRenderer(renderer);

  const openGLRenderWindow = vtkOpenGLRenderWindow.newInstance();
  renderWindow.addView(openGLRenderWindow);
  openGLRenderWindow.setContainer(container);

  const bbox = container.getBoundingClientRect();
  openGLRenderWindow.setSize(bbox.width || 600, bbox.height || 400);

  const interactor = vtkRenderWindowInteractor.newInstance();
  const interactorStyle = vtkInteractorStyleTrackballCamera.newInstance();
  interactor.setInteractorStyle(interactorStyle);
  interactor.setView(openGLRenderWindow);
  interactor.initialize();
  interactor.bindEvents(container);

  return {
    renderer,
    renderWindow,
    openGLRenderWindow,
    interactor,
    interactorStyle,
  };
}

export function createActor(source: any): any {
  const mapper = vtkMapper.newInstance();
  mapper.setInputData(source);

  const actor = vtkActor.newInstance();
  actor.setMapper(mapper);

  return actor;
}

export { vtkActor, vtkMapper };
