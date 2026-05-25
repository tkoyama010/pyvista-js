import { useCallback, useEffect, useRef, useState } from "react";
import { usePyVistaConfig } from "../context";
import type { SceneData } from "../types";

export interface UsePyVistaOptions {
  /** Additional Python packages to install via micropip alongside pyvista-js. */
  packages?: string[];
}

export interface UsePyVistaResult {
  /** Run a Python code string. The code should call plotter.show() to emit a scene. */
  runCode: (code: string) => Promise<void>;
  /** The most recently captured SceneData, or null before the first run. */
  scene: SceneData | null;
  /** True while Pyodide or a Python run is in progress. */
  isLoading: boolean;
  /** True once Pyodide and pyvista-js are fully initialised. */
  isReady: boolean;
  /** The last error message, or null if there is none. */
  error: string | null;
  /** Accumulated stdout text from the last run. */
  stdout: string;
}

type WorkerResponse =
  | { type: "ready" }
  | { type: "scene"; id: string; data: SceneData }
  | { type: "error"; id?: string; message: string }
  | { type: "stdout"; text: string }
  | { type: "stderr"; text: string };

let _runIdCounter = 0;
function nextRunId(): string {
  _runIdCounter++;
  return String(_runIdCounter);
}

/**
 * usePyVista — run pyvista-js Python code in a Pyodide Web Worker and
 * receive the rendered SceneData for display in PyVistaViewer.
 *
 * @example
 * ```tsx
 * function App() {
 *   const { runCode, scene, isLoading } = usePyVista()
 *
 *   useEffect(() => {
 *     runCode(`
 * import pyvista_js as pv
 * pl = pv.Plotter()
 * pl.add_mesh(pv.Sphere(), color='red')
 * pl.show()
 *     `)
 *   }, [])
 *
 *   if (isLoading) return <p>Loading…</p>
 *   return scene ? <PyVistaViewer scene={scene} /> : null
 * }
 * ```
 */
export function usePyVista(options: UsePyVistaOptions = {}): UsePyVistaResult {
  const { pyodideUrl } = usePyVistaConfig();

  const [scene, setScene] = useState<SceneData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isReady, setIsReady] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [stdout, setStdout] = useState("");

  const workerRef = useRef<Worker | null>(null);
  // Map from run-id → { resolve, reject } for the pending Promise
  const pendingRef = useRef<Map<string, { resolve: () => void; reject: (e: Error) => void }>>(
    new Map(),
  );

  // biome-ignore lint/correctness/useExhaustiveDependencies: Pyodide initialises once on mount; re-running on URL/package changes is not supported.
  useEffect(() => {
    const worker = new Worker(new URL("../workers/pyodide.worker.ts", import.meta.url), {
      type: "module",
    });
    workerRef.current = worker;

    worker.addEventListener("message", (e: MessageEvent<WorkerResponse>) => {
      const msg = e.data;
      switch (msg.type) {
        case "ready":
          setIsReady(true);
          setIsLoading(false);
          break;

        case "scene": {
          setScene(msg.data);
          setIsLoading(false);
          pendingRef.current.get(msg.id)?.resolve();
          pendingRef.current.delete(msg.id);
          break;
        }

        case "error": {
          setError(msg.message);
          setIsLoading(false);
          if (msg.id) {
            pendingRef.current.get(msg.id)?.reject(new Error(msg.message));
            pendingRef.current.delete(msg.id);
          }
          break;
        }

        case "stdout":
          setStdout((prev) => prev + msg.text);
          break;

        case "stderr":
          setStdout((prev) => prev + msg.text);
          break;

        default:
          break;
      }
    });

    worker.postMessage({
      type: "init",
      packages: options.packages ?? [],
      pyodideUrl,
    });

    return () => {
      worker.terminate();
      workerRef.current = null;
    };
  }, []);

  const runCode = useCallback((code: string): Promise<void> => {
    const worker = workerRef.current;
    if (!worker) return Promise.reject(new Error("Worker not initialised"));

    const id = nextRunId();
    setIsLoading(true);
    setError(null);
    setStdout("");

    return new Promise<void>((resolve, reject) => {
      pendingRef.current.set(id, { resolve, reject });
      worker.postMessage({ type: "run", id, code });
    });
  }, []);

  return { runCode, scene, isLoading, isReady, error, stdout };
}
