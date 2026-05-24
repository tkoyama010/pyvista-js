/**
 * Pyodide Web Worker for react-pyvista.
 *
 * This worker loads Pyodide, installs pyvista-js via micropip, and executes
 * Python code on behalf of the usePyVista hook. Plotter.show() is intercepted
 * to capture scene JSON and postMessage it to the main thread instead of
 * attempting DOM rendering.
 */

// eslint-disable-next-line @typescript-eslint/no-explicit-any
declare const loadPyodide: (options?: Record<string, unknown>) => Promise<any>

// importScripts is available in classic workers; type it explicitly
declare function importScripts(...urls: string[]): void

const DEFAULT_PYODIDE_INDEX =
  'https://cdn.jsdelivr.net/pyodide/stable/full/'

interface InitMessage {
  type: 'init'
  packages: string[]
  pyodideUrl?: string
}

interface RunMessage {
  type: 'run'
  id: string
  code: string
}

type WorkerInput = InitMessage | RunMessage

// eslint-disable-next-line @typescript-eslint/no-explicit-any
let pyodide: any = null

async function initialize(packages: string[], pyodideUrl?: string): Promise<void> {
  const indexURL = pyodideUrl ?? DEFAULT_PYODIDE_INDEX

  // Load Pyodide bootstrap
  importScripts(indexURL + 'pyodide.js')

  pyodide = await loadPyodide({ indexURL })

  // Redirect stdout to main thread
  pyodide.setStdout({
    batched: (text: string) => {
      self.postMessage({ type: 'stdout', text })
    },
  })
  pyodide.setStderr({
    batched: (text: string) => {
      self.postMessage({ type: 'stderr', text })
    },
  })

  // Install pyvista-js
  await pyodide.loadPackage('micropip')
  const micropip = pyodide.pyimport('micropip')
  await micropip.install('pyvista-js')

  // Install any additional packages requested by the caller
  if (packages.length > 0) {
    await micropip.install(packages)
  }

  // Intercept Plotter.show() so it emits scene JSON instead of trying to
  // render into a DOM that doesn't exist inside a Web Worker.
  await pyodide.runPythonAsync(`
import pyvista_js as pv
import json as _json

_rp_captured_scene = None

_rp_original_show = pv.Plotter.show

def _rp_capturing_show(self, *args, **kwargs):
    global _rp_captured_scene
    _rp_captured_scene = self.get_scene_dict()

pv.Plotter.show = _rp_capturing_show
`)

  self.postMessage({ type: 'ready' })
}

async function run(id: string, code: string): Promise<void> {
  if (!pyodide) {
    self.postMessage({ type: 'error', id, message: 'Pyodide is not initialised yet.' })
    return
  }

  try {
    // Reset the captured scene before each run
    await pyodide.runPythonAsync('_rp_captured_scene = None')

    // Execute user code
    await pyodide.runPythonAsync(code)

    // Retrieve scene JSON
    const sceneJson: string = await pyodide.runPythonAsync(
      '_json.dumps(_rp_captured_scene) if _rp_captured_scene is not None else "null"',
    )

    if (sceneJson === 'null') {
      self.postMessage({
        type: 'error',
        id,
        message:
          'No scene was captured. Make sure your code calls plotter.show().',
      })
    } else {
      self.postMessage({ type: 'scene', id, data: JSON.parse(sceneJson) })
    }
  } catch (err: unknown) {
    self.postMessage({
      type: 'error',
      id,
      message: err instanceof Error ? err.message : String(err),
    })
  }
}

self.addEventListener('message', (e: MessageEvent<WorkerInput>) => {
  const msg = e.data
  if (msg.type === 'init') {
    initialize(msg.packages, msg.pyodideUrl).catch((err: unknown) => {
      self.postMessage({
        type: 'error',
        message: `Pyodide initialisation failed: ${String(err)}`,
      })
    })
  } else if (msg.type === 'run') {
    run(msg.id, msg.code).catch((err: unknown) => {
      self.postMessage({
        type: 'error',
        id: msg.id,
        message: String(err),
      })
    })
  }
})
