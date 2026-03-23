/**
 * Type definitions for pyvista-js viewer configuration
 *
 * This file provides TypeScript interfaces that are compatible with both:
 * 1. Server-side Jinja2 template injection (Standard Server path)
 * 2. Direct JavaScript invocation from WASM environments (Pyodide/JupyterLite)
 *
 * These types are designed to be OpenAPI-compatible and can be generated
 * from Python Pydantic models.
 */

/**
 * RGB color representation with values in range [0, 1]
 */
export interface RGBColor {
  r: number;
  g: number;
  b: number;
}

/**
 * 3D point or vector
 */
export interface Vector3 {
  x: number;
  y: number;
  z: number;
}

/**
 * Camera configuration
 */
export interface CameraConfig {
  position?: Vector3;
  focalPoint?: Vector3;
  viewUp?: Vector3;
  viewAngle?: number;
  parallelProjection?: boolean;
}

/**
 * Light configuration
 */
export interface LightConfig {
  position?: Vector3;
  focalPoint?: Vector3;
  intensity?: number;
  color?: RGBColor;
}

/**
 * Actor (mesh) configuration
 */
export interface ActorConfig {
  /** Source code for creating the vtk.js data source */
  sourceCode: string;
  /** Mapper class name (e.g., "vtkMapper") */
  mapperClass?: string;
  /** Mapper setup code */
  mapperSetup?: string;
  /** Color of the actor */
  color?: RGBColor;
  /** Opacity [0, 1] */
  opacity?: number;
  /** Whether to show edges */
  showEdges?: boolean;
  /** Edge color if showEdges is true */
  edgeColor?: RGBColor;
  /** Rendering style: "surface" | "wireframe" | "points" */
  style?: string;
  /** Smooth shading */
  smoothShading?: boolean;
  /** PBR (Physically Based Rendering) enabled */
  pbr?: boolean;
  /** Metallic property for PBR [0, 1] */
  metallic?: number;
  /** Roughness property for PBR [0, 1] */
  roughness?: number;
  /** Texture code */
  textureCode?: string;
  /** Normals code */
  normalsCode?: string;
  /** Scalar mapping code */
  scalarCode?: string;
}

/**
 * Text actor configuration
 */
export interface TextConfig {
  text: string;
  position?: Vector3;
  fontSize?: number;
  color?: RGBColor;
}

/**
 * Scalar bar configuration
 */
export interface ScalarBarConfig {
  title?: string;
  numberOfLabels?: number;
  automated?: boolean;
}

/**
 * Environment texture configuration
 */
export interface EnvironmentConfig {
  textureUrl?: string;
}

/**
 * Axes configuration
 */
export interface AxesConfig {
  enabled: boolean;
  xAxisColor?: RGBColor;
  yAxisColor?: RGBColor;
  zAxisColor?: RGBColor;
}

/**
 * Main viewer configuration object
 *
 * This is the primary interface for initializing a pyvista-js viewer.
 * It can be provided either through:
 * - Server-side: Jinja2 template generates JS code that creates this object
 * - WASM-side: JavaScript code directly creates and passes this object
 */
export interface ViewerConfig {
  /** Container element ID where the viewer will be mounted */
  containerId: string;
  /** Background color */
  backgroundColor?: RGBColor;
  /** Width of the viewer */
  width?: number;
  /** Height of the viewer */
  height?: number;
  /** Array of actors (meshes) to render */
  actors?: ActorConfig[];
  /** Array of lights */
  lights?: LightConfig[];
  /** Camera configuration */
  camera?: CameraConfig;
  /** Text actors */
  textActors?: TextConfig[];
  /** Scalar bar configuration */
  scalarBar?: ScalarBarConfig;
  /** Environment texture */
  environment?: EnvironmentConfig;
  /** Axes configuration */
  axes?: AxesConfig;
  /** vtk.js CDN URL (defaults to unpkg) */
  vtkjsCdnUrl?: string;
}

/**
 * Global declarations for server-side mode
 *
 * When using Jinja2 template injection, these globals are available
 * from the template rendering context.
 */
declare global {
  /**
   * In server mode, this contains the pre-rendered config from Jinja2
   */
  var PYVISTA_CONFIG: ViewerConfig | undefined;

  /**
   * The vtk.js library (loaded from CDN)
   */
  var vtk: any;
}

/**
 * Initialize the pyvista-js viewer
 *
 * This function is the main entry point for both server and WASM modes.
 *
 * @param config - Viewer configuration object
 * @returns Object containing the renderer, renderWindow, and interactor
 *
 * @example
 * // Server mode (config injected via Jinja2)
 * if (typeof PYVISTA_CONFIG !== 'undefined') {
 *   initViewer(PYVISTA_CONFIG);
 * }
 *
 * @example
 * // WASM mode (config provided programmatically)
 * import { initViewer } from './viewer';
 * const config = {
 *   containerId: 'my-viewer',
 *   backgroundColor: { r: 1, g: 1, b: 1 },
 *   actors: [...]
 * };
 * initViewer(config);
 */
export function initViewer(config: ViewerConfig): {
  renderer: any;
  renderWindow: any;
  interactor: any;
};

export {};
