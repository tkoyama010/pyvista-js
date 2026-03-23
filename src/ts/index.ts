// Main entry point for PyVista JS TypeScript bundle

// Export vtk compatibility namespace for existing templates
export { vtk } from "./vtk_compat";

// Export rendering utilities
export { 
  initializeRenderer, 
  createActor,
  vtkActor,
  vtkMapper,
  type RenderingContext 
} from "./rendering";

// Export all sources
export { createMeshSource } from "./sources/mesh_source";
export { createCircleSource, type CircleSourceParams } from "./sources/circle_source";
export { createConeSource, type ConeSourceParams } from "./sources/cone_source";
export { createPlaneSource, type PlaneSourceParams } from "./sources/plane_source";
export { createDiskSource, type DiskSourceParams } from "./sources/disk_source";
export { createPointsSource } from "./sources/points_source";
export { createSphereSource, type SphereSourceParams } from "./sources/sphere_source";
export { createCubeSource, type CubeSourceParams } from "./sources/cube_source";
export { createLineSource, type LineSourceParams } from "./sources/line_source";
export { createCylinderSource, type CylinderSourceParams } from "./sources/cylinder_source";
export { createArrowSource, type ArrowSourceParams } from "./sources/arrow_source";

// Export all readers
export { createStlReader, type StlReaderResult } from "./readers/stl_reader";
export { createVtkReader, type VtkReaderResult } from "./readers/vtk_reader";
export { createObjReader, type ObjReaderResult } from "./readers/obj_reader";
export { createPlyReader, type PlyReaderResult } from "./readers/ply_reader";

// Make vtk available globally for template compatibility
import { vtk as vtkCompat } from "./vtk_compat";
if (typeof window !== "undefined") {
  (window as any).vtk = vtkCompat;
}
