import { build } from "esbuild";

const result = await build({
  entryPoints: ["src/ts/index.ts"],
  bundle: true,
  format: "iife",
  globalName: "PyVistaJS",
  minify: true,
  treeShaking: true,
  outfile: "src/pyvista_js/static/pyvista_js.js",
  // External dependencies are now bundled instead of loaded from CDN
  external: [],
  logLevel: "info",
  metafile: true,
});

console.log("Built: src/pyvista_js/static/pyvista_js.js");
console.log("⚠️  Note: Bundle includes @kitware/vtk.js (large size expected)");

// Show bundle size breakdown
if (result.metafile) {
  const outputs = Object.values(result.metafile.outputs);
  if (outputs.length > 0) {
    const output = outputs[0];
    console.log(`\nBundle size: ${(output.bytes / 1024).toFixed(1)} KB`);
  }
}


