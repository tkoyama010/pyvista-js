/**
 * Python algorithms integration for PyVista-js
 * Provides synchronous interface to call Python algorithms via Pyodide
 */

// Global pyodide instance
declare let pyodide: any;

/**
 * Check if Pyodide is available and initialized
 */
function isPyodideReady(): boolean {
  return typeof (window as any).pyodide !== 'undefined' && (window as any).pyodide !== null;
}

/**
 * Initialize Pyodide and load Python algorithms module
 */
export async function initializePyodide(): Promise<void> {
  if (!isPyodideReady()) {
    if (typeof (window as any).loadPyodide === 'undefined') {
      throw new Error('Pyodide is not available. Please ensure Pyodide is loaded.');
    }
    
    (window as any).pyodide = await (window as any).loadPyodide();
    
    // Load NumPy
    await (window as any).pyodide.loadPackage('numpy');
    
    // Load our algorithms module
    const algorithmsCode = `
import numpy as np

def create_sphere(radius=1.0, theta_resolution=32, phi_resolution=32):
    """Create a sphere mesh using NumPy vectorization for improved performance."""
    theta = np.linspace(0, 2 * np.pi, theta_resolution)
    phi = np.linspace(0, np.pi, phi_resolution)
    theta_grid, phi_grid = np.meshgrid(theta, phi)
    
    x = radius * np.sin(phi_grid) * np.cos(theta_grid)
    y = radius * np.sin(phi_grid) * np.sin(theta_grid)
    z = radius * np.cos(phi_grid)
    
    points = np.column_stack([x.ravel(), y.ravel(), z.ravel()])
    
    # Create face connectivity
    faces = []
    for i in range(phi_resolution - 1):
        for j in range(theta_resolution - 1):
            p1 = i * theta_resolution + j
            p2 = i * theta_resolution + (j + 1)
            p3 = (i + 1) * theta_resolution + (j + 1)
            p4 = (i + 1) * theta_resolution + j
            
            faces.extend([[3, p1, p2, p4], [3, p2, p3, p4]])
    
    return points.tolist(), [item for sublist in faces for item in sublist]

def create_cone(radius=1.0, height=2.0, resolution=32):
    """Create a cone mesh with optimized NumPy operations."""
    theta = np.linspace(0, 2 * np.pi, resolution, endpoint=False)
    
    # Base circle points
    base_points = np.column_stack([
        radius * np.cos(theta),
        radius * np.sin(theta),
        np.zeros(resolution)
    ])
    
    # Apex point
    apex = np.array([[0.0, 0.0, height]])
    points = np.vstack([base_points, apex])
    
    # Create triangular faces
    faces = []
    for i in range(resolution):
        next_i = (i + 1) % resolution
        faces.append([3, i, next_i, resolution])  # Side triangles
    
    return points.tolist(), [item for sublist in faces for item in sublist]

def create_cube(size=2.0):
    """Create a cube mesh with NumPy optimization."""
    s = size / 2
    points = np.array([
        [-s, -s, -s], [s, -s, -s], [s, s, -s], [-s, s, -s],  # Bottom face
        [-s, -s, s], [s, -s, s], [s, s, s], [-s, s, s]      # Top face
    ])
    
    # Define faces (triangles)
    faces = [
        [3, 0, 1, 2], [3, 0, 2, 3],  # Bottom
        [3, 4, 7, 6], [3, 4, 6, 5],  # Top
        [3, 0, 4, 5], [3, 0, 5, 1],  # Front
        [3, 2, 6, 7], [3, 2, 7, 3],  # Back
        [3, 1, 5, 6], [3, 1, 6, 2],  # Right
        [3, 4, 0, 3], [3, 4, 3, 7]   # Left
    ]
    
    return points.tolist(), [item for sublist in faces for item in sublist]

def create_cylinder(radius=1.0, height=2.0, resolution=32):
    """Create a cylinder mesh with NumPy vectorization."""
    theta = np.linspace(0, 2 * np.pi, resolution, endpoint=False)
    
    # Bottom and top circles
    bottom_points = np.column_stack([
        radius * np.cos(theta),
        radius * np.sin(theta),
        np.zeros(resolution)
    ])
    
    top_points = np.column_stack([
        radius * np.cos(theta),
        radius * np.sin(theta),
        np.full(resolution, height)
    ])
    
    points = np.vstack([bottom_points, top_points])
    
    # Create faces
    faces = []
    for i in range(resolution):
        next_i = (i + 1) % resolution
        # Side quads (as triangles)
        faces.extend([
            [3, i, next_i, i + resolution],
            [3, next_i, next_i + resolution, i + resolution]
        ])
    
    return points.tolist(), [item for sublist in faces for item in sublist]

def shrink_mesh(points, shrink_factor=0.8):
    """Shrink mesh towards its centroid using NumPy vectorization."""
    points_array = np.array(points)
    centroid = np.mean(points_array, axis=0)
    result = centroid + shrink_factor * (points_array - centroid)
    return result.tolist()

def clip_mesh(points, faces, plane_origin, plane_normal):
    """Clip mesh with a plane using NumPy operations."""
    points_array = np.array(points)
    plane_origin_array = np.array(plane_origin)
    plane_normal_array = np.array(plane_normal)
    
    # Simple plane clipping implementation
    plane_normal_normalized = plane_normal_array / np.linalg.norm(plane_normal_array)
    distances = np.dot(points_array - plane_origin_array, plane_normal_normalized)
    
    # Keep points on the positive side of the plane
    keep_mask = distances >= 0
    
    # Filter points and faces
    new_points = points_array[keep_mask].tolist()
    point_map = np.full(len(points_array), -1)
    point_map[keep_mask] = np.arange(np.sum(keep_mask))
    
    # Filter faces that have all vertices kept
    valid_faces = []
    for face in faces:
        if all(point_map[face[1:]] >= 0):
            new_face = [face[0]] + [int(point_map[idx]) for idx in face[1:]]
            valid_faces.append(new_face)
    
    return new_points, [item for sublist in valid_faces for item in sublist]

def compute_contour(points, values, isovalue):
    """Compute contour using NumPy vectorization."""
    points_array = np.array(points)
    values_array = np.array(values)
    mask = values_array >= isovalue
    return points_array[mask].tolist()
`;
    
    (window as any).pyodide.runPython(algorithmsCode);
  }
}

/**
 * Call Python sphere algorithm
 */
export async function callPythonSphere(radius: number, thetaResolution: number, phiResolution: number): Promise<{points: number[], faces: number[]}> {
  await initializePyodide();
  const result = (window as any).pyodide.runPython(`create_sphere(${radius}, ${thetaResolution}, ${phiResolution})`);
  const [points, faces] = result.toJs();
  return { points, faces };
}

/**
 * Call Python cone algorithm
 */
export async function callPythonCone(radius: number, height: number, resolution: number): Promise<{points: number[], faces: number[]}> {
  await initializePyodide();
  const result = (window as any).pyodide.runPython(`create_cone(${radius}, ${height}, ${resolution})`);
  const [points, faces] = result.toJs();
  return { points, faces };
}

/**
 * Call Python cube algorithm
 */
export async function callPythonCube(size: number): Promise<{points: number[], faces: number[]}> {
  await initializePyodide();
  const result = (window as any).pyodide.runPython(`create_cube(${size})`);
  const [points, faces] = result.toJs();
  return { points, faces };
}

/**
 * Call Python cylinder algorithm
 */
export async function callPythonCylinder(radius: number, height: number, resolution: number): Promise<{points: number[], faces: number[]}> {
  await initializePyodide();
  const result = (window as any).pyodide.runPython(`create_cylinder(${radius}, ${height}, ${resolution})`);
  const [points, faces] = result.toJs();
  return { points, faces };
}

/**
 * Call Python shrink algorithm
 */
export async function callPythonShrink(points: number[], shrinkFactor: number): Promise<number[]> {
  await initializePyodide();
  (window as any).pyodide.runPython(`import json`);
  (window as any).pyodide.runPython(`points_data = ${JSON.stringify(points)}`);
  const result = (window as any).pyodide.runPython(`shrink_mesh(points_data, ${shrinkFactor})`);
  return result.toJs();
}

/**
 * Call Python clip algorithm
 */
export async function callPythonClip(points: number[], faces: number[], planeOrigin: number[], planeNormal: number[]): Promise<{points: number[], faces: number[]}> {
  await initializePyodide();
  (window as any).pyodide.runPython(`import json`);
  (window as any).pyodide.runPython(`points_data = ${JSON.stringify(points)}`);
  (window as any).pyodide.runPython(`faces_data = ${JSON.stringify(faces)}`);
  (window as any).pyodide.runPython(`plane_origin_data = ${JSON.stringify(planeOrigin)}`);
  (window as any).pyodide.runPython(`plane_normal_data = ${JSON.stringify(planeNormal)}`);
  const result = (window as any).pyodide.runPython(`clip_mesh(points_data, faces_data, plane_origin_data, plane_normal_data)`);
  const [newPoints, newFaces] = result.toJs();
  return { points: newPoints, faces: newFaces };
}

/**
 * Call Python contour algorithm
 */
export async function callPythonContour(points: number[], values: number[], isovalue: number): Promise<number[]> {
  await initializePyodide();
  (window as any).pyodide.runPython(`import json`);
  (window as any).pyodide.runPython(`points_data = ${JSON.stringify(points)}`);
  (window as any).pyodide.runPython(`values_data = ${JSON.stringify(values)}`);
  const result = (window as any).pyodide.runPython(`compute_contour(points_data, values_data, ${isovalue})`);
  return result.toJs();
}