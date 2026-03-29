/**
 * Type definitions for pyvista-js renderer
 */

export interface SourceConfig {
  type?: string;
  center?: [number, number, number];
  radius?: number;
  thetaResolution?: number;
  phiResolution?: number;
  height?: number;
  xLength?: number;
  yLength?: number;
  zLength?: number;
  resolution?: number;
  innerRadius?: number;
  outerRadius?: number;
  tipLength?: number;
  tipRadius?: number;
  shaftRadius?: number;
  point1?: [number, number, number];
  point2?: [number, number, number];
  origin?: [number, number, number];
  normal?: [number, number, number];
  points?: number[];
  polys?: number[];
  data?: string;
}

export interface FilterConfig {
  type: 'shrink' | 'tube' | 'clip' | 'contour';
  shrinkFactor?: number;
  radius?: number;
  numberOfSides?: number;
  normal?: [number, number, number];
  origin?: [number, number, number];
  invert?: boolean;
  values?: number[];
  scalarName?: string;
  scalarData?: number[];
}

export interface SourceResult {
  output: any; // vtk.js algorithm or PolyData
  isFilter: boolean;
}