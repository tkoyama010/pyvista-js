import type { ReactNode } from 'react'
import { PyVistaContext, type PyVistaConfig } from '../context'

interface PyVistaProviderProps extends PyVistaConfig {
  children: ReactNode
}

/**
 * PyVistaProvider configures global options for all react-pyvista components.
 *
 * Wrap your application (or a subtree) with this provider to customise the
 * vtk.js CDN URL or the Pyodide CDN URL used by usePyVista.
 *
 * @example
 * ```tsx
 * <PyVistaProvider vtkJsCdnUrl="https://unpkg.com/vtk.js@29.5.0">
 *   <App />
 * </PyVistaProvider>
 * ```
 */
export function PyVistaProvider({ vtkJsCdnUrl, pyodideUrl, children }: PyVistaProviderProps) {
  return (
    <PyVistaContext.Provider value={{ vtkJsCdnUrl, pyodideUrl }}>
      {children}
    </PyVistaContext.Provider>
  )
}
