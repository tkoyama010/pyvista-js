export const DEFAULT_VTK_CDN = "https://unpkg.com/vtk.js@29.5.0";

let loadPromise: Promise<void> | null = null;

export function loadVtkJs(cdnUrl = DEFAULT_VTK_CDN): Promise<void> {
  if (typeof window === "undefined") {
    return Promise.reject(new Error("vtk.js requires a browser environment"));
  }
  if ((window as unknown as { vtk?: unknown }).vtk) {
    return Promise.resolve();
  }
  if (loadPromise) return loadPromise;

  loadPromise = new Promise((resolve, reject) => {
    const script = document.createElement("script");
    script.src = cdnUrl;
    script.addEventListener("load", () => {
      resolve();
    });
    script.addEventListener("error", () => {
      loadPromise = null;
      reject(new Error(`Failed to load vtk.js from ${cdnUrl}`));
    });
    document.head.appendChild(script);
  });

  return loadPromise;
}
