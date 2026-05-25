import { type CSSProperties, useEffect, useRef } from "react";
import { usePyVistaConfig } from "../context";
import { PyVistaRenderer } from "../renderer";
import type { SceneData } from "../types";
import { loadVtkJs } from "../vtkLoader";

export interface PyVistaViewerProps {
  /** Scene data produced by pyvista-js (via usePyVista or fetched from a server). */
  scene: SceneData;
  /** Width of the viewer. Defaults to 600. */
  width?: number | string;
  /** Height of the viewer. Defaults to 400. */
  height?: number | string;
  /** Additional CSS class names for the container element. */
  className?: string;
  /** Additional inline styles merged onto the container element. */
  style?: CSSProperties;
}

/**
 * PyVistaViewer renders a pyvista-js SceneData object using vtk.js.
 *
 * vtk.js is loaded automatically from CDN on first render. The viewer
 * supports full camera interaction (trackball rotate/pan/zoom).
 *
 * @example
 * ```tsx
 * const { scene } = usePyVista()
 * // …run code…
 * return scene ? <PyVistaViewer scene={scene} width={800} height={600} /> : null
 * ```
 */
export function PyVistaViewer({
  scene,
  width = 600,
  height = 400,
  className,
  style,
}: PyVistaViewerProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const rendererRef = useRef<PyVistaRenderer | null>(null);
  const { vtkJsCdnUrl } = usePyVistaConfig();

  useEffect(() => {
    let cancelled = false;

    loadVtkJs(vtkJsCdnUrl)
      .then(() => {
        if (cancelled || !containerRef.current) return;
        rendererRef.current?.destroy();
        rendererRef.current = new PyVistaRenderer(containerRef.current, scene);
      })
      .catch((err: unknown) => {
        // biome-ignore lint/suspicious/noConsole: library-level error reporting
        console.error("[react-pyvista] Failed to initialise vtk.js renderer:", err);
      });

    return () => {
      cancelled = true;
      rendererRef.current?.destroy();
      rendererRef.current = null;
    };
  }, [scene, vtkJsCdnUrl]);

  return (
    <div
      ref={containerRef}
      className={className}
      style={{
        width,
        height,
        position: "relative",
        border: "2px solid #333",
        overflow: "hidden",
        ...style,
      }}
    />
  );
}
