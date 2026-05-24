import { createContext, useContext } from 'react'

export interface PyVistaConfig {
  vtkJsCdnUrl?: string
  pyodideUrl?: string
}

export const PyVistaContext = createContext<PyVistaConfig>({})

export function usePyVistaConfig(): PyVistaConfig {
  return useContext(PyVistaContext)
}
