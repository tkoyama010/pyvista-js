/**
 * Python Algorithm Interface for pyvista-js
 * 
 * This module provides TypeScript interfaces to call Python algorithms
 * that have been migrated from the original TypeScript implementation.
 * Uses the Pyodide runtime to execute Python code in the browser.
 */

import type { SourceConfig, SourceResult, FilterConfig } from "./types.js";

// Global Pyodide instance
let pyodide: any = null;
let pyodideReady = false;

/**
 * Initialize Pyodide runtime and load Python algorithms module
 */
export async function initializePythonAlgorithms(): Promise<void> {
  if (pyodideReady) return;
  
  try {
    // Load Pyodide from CDN
    const pyodideScript = document.createElement('script');
    pyodideScript.src = 'https://cdn.jsdelivr.net/pyodide/v0.24.1/full/pyodide.js';
    document.head.appendChild(pyodideScript);
    
    await new Promise<void>((resolve) => {
      pyodideScript.onload = () => resolve();
    });
    
    // @ts-ignore - loadPyodide is added by the script
    pyodide = await loadPyodide();
    
    // Install numpy
    await pyodide.loadPackage('numpy');
    
    // Load our algorithms module
    const algorithmsCode = `
import numpy as np
from typing import Dict, List, Optional, Tuple, Union

class GeometricAlgorithms:
    @staticmethod
    def create_sphere(center=(0.0, 0.0, 0.0), radius=1.0, theta_resolution=32, phi_resolution=32):
        theta = np.linspace(0, 2 * np.pi, theta_resolution, endpoint=False)
        phi = np.linspace(0, np.pi, phi_resolution)
        
        points = []
        for j, phi_val in enumerate(phi):
            for i, theta_val in enumerate(theta):
                x = radius * np.sin(phi_val) * np.cos(theta_val)
                y = radius * np.sin(phi_val) * np.sin(theta_val)
                z = radius * np.cos(phi_val)
                points.append([x + center[0], y + center[1], z + center[2]])
        
        points.append([center[0], center[1], center[2] + radius])
        points.append([center[0], center[1], center[2] - radius])
        
        polys = []
        for j in range(phi_resolution - 2):
            for i in range(theta_resolution):
                i_next = (i + 1) % theta_resolution
                p1 = j * theta_resolution + i
                p2 = j * theta_resolution + i_next
                p3 = (j + 1) * theta_resolution + i_next
                p4 = (j + 1) * theta_resolution + i
                polys.extend([4, p1, p2, p3, p4])
        
        north_pole_idx = len(points) - 2
        for i in range(theta_resolution):
            i_next = (i + 1) % theta_resolution
            p1 = (phi_resolution - 2) * theta_resolution + i
            p2 = (phi_resolution - 2) * theta_resolution + i_next
            polys.extend([3, p1, p2, north_pole_idx])
        
        south_pole_idx = len(points) - 1
        for i in range(theta_resolution):
            i_next = (i + 1) % theta_resolution
            p1 = i
            p2 = i_next
            polys.extend([3, p1, south_pole_idx, p2])
        
        tcoords = []
        for j in range(phi_resolution):
            for i in range(theta_resolution):
                u = i / (theta_resolution - 1) if theta_resolution > 1 else 0
                v = j / (phi_resolution - 1) if phi_resolution > 1 else 0
                tcoords.append([u, v])
        
        tcoords.append([0.5, 1.0])
        tcoords.append([0.5, 0.0])
        
        return {
            'points': [[float(x), float(y), float(z)] for x, y, z in points],
            'polys': [int(x) for x in polys],
            'tcoords': [[float(u), float(v)] for u, v in tcoords]
        }
    
    @staticmethod
    def create_cone(height=1.0, radius=0.5, resolution=32, center=(0.0, 0.0, 0.0)):
        points = []
        polys = []
        
        base_center = [center[0], center[1], center[2] - height/2]
        points.append(base_center)
        
        for i in range(resolution):
            angle = 2 * np.pi * i / resolution
            x = center[0] + radius * np.cos(angle)
            y = center[1] + radius * np.sin(angle)
            z = center[2] - height/2
            points.append([x, y, z])
        
        apex = [center[0], center[1], center[2] + height/2]
        points.append(apex)
        
        for i in range(resolution):
            i_next = (i + 1) % resolution
            polys.extend([3, 0, i + 1, i_next + 1])
        
        for i in range(resolution):
            i_next = (i + 1) % resolution
            polys.extend([3, i + 1, i_next + 1, len(points) - 1])
        
        return {
            'points': [[float(x), float(y), float(z)] for x, y, z in points],
            'polys': [int(x) for x in polys]
        }
    
    @staticmethod
    def create_cube(x_length=1.0, y_length=1.0, z_length=1.0, center=(0.0, 0.0, 0.0)):
        hx, hy, hz = x_length/2, y_length/2, z_length/2
        
        points = [
            [center[0] - hx, center[1] - hy, center[2] - hz],
            [center[0] + hx, center[1] - hy, center[2] - hz],
            [center[0] + hx, center[1] + hy, center[2] - hz],
            [center[0] - hx, center[1] + hy, center[2] - hz],
            [center[0] - hx, center[1] - hy, center[2] + hz],
            [center[0] + hx, center[1] - hy, center[2] + hz],
            [center[0] + hx, center[1] + hy, center[2] + hz],
            [center[0] - hx, center[1] + hy, center[2] + hz],
        ]
        
        polys = [
            4, 0, 1, 2, 3,
            4, 4, 7, 6, 5,
            4, 0, 4, 5, 1,
            4, 2, 6, 7, 3,
            4, 0, 3, 7, 4,
            4, 1, 5, 6, 2,
        ]
        
        return {
            'points': [[float(x), float(y), float(z)] for x, y, z in points],
            'polys': [int(x) for x in polys]
        }
    
    @staticmethod
    def create_cylinder(height=1.0, radius=0.5, resolution=32, center=(0.0, 0.0, 0.0)):
        points = []
        polys = []
        
        bottom_center = [center[0], center[1], center[2] - height/2]
        top_center = [center[0], center[1], center[2] + height/2]
        points.append(bottom_center)
        points.append(top_center)
        
        for i in range(resolution):
            angle = 2 * np.pi * i / resolution
            x = center[0] + radius * np.cos(angle)
            y = center[1] + radius * np.sin(angle)
            points.append([x, y, bottom_center[2]])
            points.append([x, y, top_center[2]])
        
        for i in range(resolution):
            i_next = (i + 1) % resolution
            polys.extend([3, 0, 2 + i*2, 2 + i_next*2])
        
        for i in range(resolution):
            i_next = (i + 1) % resolution
            polys.extend([3, 1, 3 + i_next*2, 3 + i*2])
        
        for i in range(resolution):
            i_next = (i + 1) % resolution
            p1 = 2 + i*2
            p2 = 2 + i_next*2
            p3 = 3 + i_next*2
            p4 = 3 + i*2
            polys.extend([4, p1, p2, p3, p4])
        
        return {
            'points': [[float(x), float(y), float(z)] for x, y, z in points],
            'polys': [int(x) for x in polys]
        }

class MeshProcessingAlgorithms:
    @staticmethod
    def apply_shrink_filter(points, polys, shrink_factor=0.8):
        if len(polys) == 0:
            return {'points': points, 'polys': polys}
        
        result_points = []
        result_polys = []
        offset = 0
        index = 0
        
        while index < len(polys):
            n_verts = int(polys[index])
            index += 1
            
            centroid = [0.0, 0.0, 0.0]
            indices = []
            
            for i in range(n_verts):
                vi = int(polys[index + i])
                indices.append(vi)
                centroid[0] += points[vi][0]
                centroid[1] += points[vi][1]
                centroid[2] += points[vi][2]
            
            centroid[0] /= n_verts
            centroid[1] /= n_verts
            centroid[2] /= n_verts
            
            result_polys.append(n_verts)
            for i in range(n_verts):
                pi = indices[i]
                point = points[pi]
                shrunk_point = [
                    centroid[0] + (point[0] - centroid[0]) * shrink_factor,
                    centroid[1] + (point[1] - centroid[1]) * shrink_factor,
                    centroid[2] + (point[2] - centroid[2]) * shrink_factor,
                ]
                result_points.append(shrunk_point)
                result_polys.append(offset + i)
            
            offset += n_verts
            index += n_verts
        
        return {
            'points': result_points,
            'polys': [int(x) for x in result_polys]
        }
    
    @staticmethod
    def apply_clip_filter(points, polys, normal, origin, invert=False):
        if len(polys) == 0:
            return {'points': points, 'polys': polys}
        
        result_points = []
        result_polys = []
        point_map = {}
        next_index = 0
        index = 0
        
        while index < len(polys):
            n_verts = int(polys[index])
            index += 1
            
            centroid = [0.0, 0.0, 0.0]
            cell_indices = []
            
            for i in range(n_verts):
                vi = int(polys[index + i])
                cell_indices.append(vi)
                centroid[0] += points[vi][0]
                centroid[1] += points[vi][1]
                centroid[2] += points[vi][2]
            
            centroid[0] /= n_verts
            centroid[1] /= n_verts
            centroid[2] /= n_verts
            
            dot_product = (centroid[0] - origin[0]) * normal[0] + (centroid[1] - origin[1]) * normal[1] + (centroid[2] - origin[2]) * normal[2]
            keep = (dot_product <= 0) if not invert else (dot_product >= 0)
            
            if keep:
                result_polys.append(n_verts)
                for i in range(n_verts):
                    pi = cell_indices[i]
                    if pi not in point_map:
                        point_map[pi] = next_index
                        next_index += 1
                        result_points.append(points[pi])
                    result_polys.append(point_map[pi])
            
            index += n_verts
        
        return {
            'points': result_points,
            'polys': [int(x) for x in result_polys]
        }
    
    @staticmethod
    def apply_contour_filter(points, polys, scalar_data, values):
        if len(polys) == 0 or len(scalar_data) == 0:
            return {'points': [], 'lines': []}
        
        out_points = []
        out_lines = []
        point_index = 0
        index = 0
        
        def interpolate_edge(p1, p2, s1, s2, value):
            if (s1 <= value < s2) or (s2 <= value < s1):
                t = (value - s1) / (s2 - s1)
                return [
                    points[p1][0] + t * (points[p2][0] - points[p1][0]),
                    points[p1][1] + t * (points[p2][1] - points[p1][1]),
                    points[p1][2] + t * (points[p2][2] - points[p1][2]),
                ]
            return None
        
        while index < len(polys):
            n_verts = int(polys[index])
            index += 1
            
            if n_verts == 3:
                idx0 = int(polys[index])
                idx1 = int(polys[index + 1])
                idx2 = int(polys[index + 2])
                
                s0 = scalar_data[idx0]
                s1 = scalar_data[idx1]
                s2 = scalar_data[idx2]
                
                for value in values:
                    intersections = []
                    
                    edges = [(idx0, idx1, s0, s1), (idx1, idx2, s1, s2), (idx2, idx0, s2, s0)]
                    
                    for edge in edges:
                        intersection = interpolate_edge(*edge, value)
                        if intersection:
                            intersections.append(intersection)
                    
                    if len(intersections) == 2:
                        out_points.extend(intersections[0])
                        out_points.extend(intersections[1])
                        out_lines.extend([2, point_index, point_index + 1])
                        point_index += 2
            
            index += n_verts
        
        return {
            'points': out_points,
            'lines': [int(x) for x in out_lines]
        }
`;
    
    pyodide.runPython(algorithmsCode);
    pyodideReady = true;
  } catch (error) {
    console.warn('Failed to initialize Python algorithms:', error);
    pyodideReady = false;
  }
}

/**
 * Check if Python algorithms are available
 */
export function isPythonAlgorithmsReady(): boolean {
  return pyodideReady;
}

/**
 * Create sphere source using Python algorithm
 */
export async function createSphereSourcePython(cfg: SourceConfig): Promise<SourceResult> {
  if (!pyodideReady) {
    throw new Error('Python algorithms not initialized');
  }
  
  const result = pyodide.runPython(`
GeometricAlgorithms.create_sphere(
    center=(${cfg.center?.[0] ?? 0.0}, ${cfg.center?.[1] ?? 0.0}, ${cfg.center?.[2] ?? 0.0}),
    radius=${cfg.radius ?? 1.0},
    theta_resolution=${cfg.thetaResolution ?? 32},
    phi_resolution=${cfg.phiResolution ?? 32}
)
  `);
  
  return createPolyDataFromPython(result);
}

/**
 * Create cone source using Python algorithm
 */
export async function createConeSourcePython(cfg: SourceConfig): Promise<SourceResult> {
  if (!pyodideReady) {
    throw new Error('Python algorithms not initialized');
  }
  
  const result = pyodide.runPython(`
GeometricAlgorithms.create_cone(
    height=${cfg.height ?? 1.0},
    radius=${cfg.radius ?? 0.5},
    resolution=${cfg.resolution ?? 32},
    center=(${cfg.center?.[0] ?? 0.0}, ${cfg.center?.[1] ?? 0.0}, ${cfg.center?.[2] ?? 0.0})
)
  `);
  
  return createPolyDataFromPython(result);
}

/**
 * Create cube source using Python algorithm
 */
export async function createCubeSourcePython(cfg: SourceConfig): Promise<SourceResult> {
  if (!pyodideReady) {
    throw new Error('Python algorithms not initialized');
  }
  
  const result = pyodide.runPython(`
GeometricAlgorithms.create_cube(
    x_length=${cfg.xLength ?? 1.0},
    y_length=${cfg.yLength ?? 1.0},
    z_length=${cfg.zLength ?? 1.0},
    center=(${cfg.center?.[0] ?? 0.0}, ${cfg.center?.[1] ?? 0.0}, ${cfg.center?.[2] ?? 0.0})
)
  `);
  
  return createPolyDataFromPython(result);
}

/**
 * Create cylinder source using Python algorithm
 */
export async function createCylinderSourcePython(cfg: SourceConfig): Promise<SourceResult> {
  if (!pyodideReady) {
    throw new Error('Python algorithms not initialized');
  }
  
  const result = pyodide.runPython(`
GeometricAlgorithms.create_cylinder(
    height=${cfg.height ?? 1.0},
    radius=${cfg.radius ?? 0.5},
    resolution=${cfg.resolution ?? 32},
    center=(${cfg.center?.[0] ?? 0.0}, ${cfg.center?.[1] ?? 0.0}, ${cfg.center?.[2] ?? 0.0})
)
  `);
  
  return createPolyDataFromPython(result);
}

/**
 * Apply shrink filter using Python algorithm
 */
export async function applyShrinkFilterPython(
  sourceResult: SourceResult,
  shrinkFactor: number
): Promise<SourceResult> {
  if (!pyodideReady) {
    throw new Error('Python algorithms not initialized');
  }
  
  const inputData = extractPolyDataForPython(sourceResult);
  
  const result = pyodide.runPython(`
MeshProcessingAlgorithms.apply_shrink_filter(
    points=${JSON.stringify(inputData.points)},
    polys=${JSON.stringify(inputData.polys)},
    shrink_factor=${shrinkFactor}
)
  `);
  
  return createPolyDataFromPython(result);
}

/**
 * Apply clip filter using Python algorithm
 */
export async function applyClipFilterPython(
  sourceResult: SourceResult,
  normal: [number, number, number],
  origin: [number, number, number],
  invert: boolean
): Promise<SourceResult> {
  if (!pyodideReady) {
    throw new Error('Python algorithms not initialized');
  }
  
  const inputData = extractPolyDataForPython(sourceResult);
  
  const result = pyodide.runPython(`
MeshProcessingAlgorithms.apply_clip_filter(
    points=${JSON.stringify(inputData.points)},
    polys=${JSON.stringify(inputData.polys)},
    normal=${JSON.stringify(normal)},
    origin=${JSON.stringify(origin)},
    invert=${invert}
)
  `);
  
  return createPolyDataFromPython(result);
}

/**
 * Apply contour filter using Python algorithm
 */
export async function applyContourFilterPython(
  sourceResult: SourceResult,
  values: number[],
  scalarName: string,
  scalarData: number[]
): Promise<SourceResult> {
  if (!pyodideReady) {
    throw new Error('Python algorithms not initialized');
  }
  
  const inputData = extractPolyDataForPython(sourceResult);
  
  const result = pyodide.runPython(`
MeshProcessingAlgorithms.apply_contour_filter(
    points=${JSON.stringify(inputData.points)},
    polys=${JSON.stringify(inputData.polys)},
    scalar_data=${JSON.stringify(scalarData)},
    values=${JSON.stringify(values)}
)
  `);
  
  return createLineDataFromPython(result);
}

/**
 * Helper function to create PolyData from Python result
 */
function createPolyDataFromPython(pythonResult: any): SourceResult {
  // Import vtk.js dynamically
  const vtk = (window as any).vtk;
  if (!vtk) {
    throw new Error('vtk.js not available');
  }
  
  const polydata = vtk.Common.DataModel.vtkPolyData.newInstance();
  
  // Set points
  if (pythonResult.points && pythonResult.points.length > 0) {
    const pointsArray = new Float32Array(pythonResult.points.flat());
    const vtkPts = vtk.Common.Core.vtkPoints.newInstance();
    vtkPts.setData(pointsArray, 3);
    polydata.setPoints(vtkPts);
  }
  
  // Set polygons
  if (pythonResult.polys && pythonResult.polys.length > 0) {
    const polysArray = new Uint32Array(pythonResult.polys);
    polydata.getPolys().setData(polysArray);
  }
  
  // Set texture coordinates if available
  if (pythonResult.tcoords && pythonResult.tcoords.length > 0) {
    const tcoordsArray = new Float32Array(pythonResult.tcoords.flat());
    const tcoordsData = vtk.Common.Core.vtkDataArray.newInstance({
      numberOfComponents: 2,
      values: tcoordsArray,
      name: 'TextureCoordinates'
    });
    polydata.getPointData().addArray(tcoordsData);
  }
  
  return { output: polydata, isFilter: false };
}

/**
 * Helper function to create line data from Python result
 */
function createLineDataFromPython(pythonResult: any): SourceResult {
  const vtk = (window as any).vtk;
  if (!vtk) {
    throw new Error('vtk.js not available');
  }
  
  const polydata = vtk.Common.DataModel.vtkPolyData.newInstance();
  
  // Set points
  if (pythonResult.points && pythonResult.points.length > 0) {
    const pointsArray = new Float32Array(pythonResult.points.flat());
    const vtkPts = vtk.Common.Core.vtkPoints.newInstance();
    vtkPts.setData(pointsArray, 3);
    polydata.setPoints(vtkPts);
  }
  
  // Set lines
  if (pythonResult.lines && pythonResult.lines.length > 0) {
    const linesArray = new Uint32Array(pythonResult.lines);
    polydata.getLines().setData(linesArray);
  }
  
  return { output: polydata, isFilter: false };
}

/**
 * Helper function to extract PolyData for Python processing
 */
function extractPolyDataForPython(sourceResult: SourceResult): { points: number[][], polys: number[] } {
  const vtk = (window as any).vtk;
  if (!vtk) {
    throw new Error('vtk.js not available');
  }
  
  // Get PolyData from source result
  const polyData = sourceResult.output;
  
  // Extract points
  const pointsData = polyData.getPoints().getData();
  const points: number[][] = [];
  for (let i = 0; i < pointsData.length; i += 3) {
    points.push([
      pointsData[i],
      pointsData[i + 1],
      pointsData[i + 2]
    ]);
  }
  
  // Extract polygons
  const polysData = polyData.getPolys().getData();
  const polys: number[] = Array.from(polysData);
  
  return { points, polys };
}