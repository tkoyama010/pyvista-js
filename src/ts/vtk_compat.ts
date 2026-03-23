// Re-export vtk.js modules for global namespace compatibility
// This allows existing templates using vtk.* to work with the bundle

import vtkRenderer from "@kitware/vtk.js/Rendering/Core/Renderer";
import vtkRenderWindow from "@kitware/vtk.js/Rendering/Core/RenderWindow";
import vtkRenderWindowInteractor from "@kitware/vtk.js/Rendering/Core/RenderWindowInteractor";
import vtkInteractorStyleTrackballCamera from "@kitware/vtk.js/Interaction/Style/InteractorStyleTrackballCamera";
import vtkOpenGLRenderWindow from "@kitware/vtk.js/Rendering/OpenGL/RenderWindow";
import vtkActor from "@kitware/vtk.js/Rendering/Core/Actor";
import vtkMapper from "@kitware/vtk.js/Rendering/Core/Mapper";
import vtkSphereMapper from "@kitware/vtk.js/Rendering/Core/SphereMapper";
import vtkPolyData from "@kitware/vtk.js/Common/DataModel/PolyData";
import vtkPoints from "@kitware/vtk.js/Common/Core/Points";
import vtkCellArray from "@kitware/vtk.js/Common/Core/CellArray";
import vtkColorTransferFunction from "@kitware/vtk.js/Rendering/Core/ColorTransferFunction";
import vtkScalarBarActor from "@kitware/vtk.js/Rendering/Core/ScalarBarActor";

// Build vtk-like namespace structure for backwards compatibility
export const vtk = {
  Common: {
    Core: {
      vtkPoints,
      vtkCellArray,
    },
    DataModel: {
      vtkPolyData,
    },
  },
  Rendering: {
    Core: {
      vtkRenderer,
      vtkRenderWindow,
      vtkRenderWindowInteractor,
      vtkActor,
      vtkMapper,
      vtkSphereMapper,
      vtkColorTransferFunction,
      vtkScalarBarActor,
    },
    OpenGL: {
      vtkRenderWindow: vtkOpenGLRenderWindow,
    },
  },
  Interaction: {
    Style: {
      vtkInteractorStyleTrackballCamera,
    },
  },
};
