// Gaussian Splat Renderer using WebGL custom shaders
// Parses Gaussian splat data and renders using point sprites with custom shaders

interface GaussianSplatData {
  positions: Float32Array;
  scales: Float32Array;
  rotations: Float32Array;
  opacities: Float32Array;
  colors: Float32Array;
  count: number;
}

// Parse Gaussian splat data from the PLY content
function parseGaussianSplatData(base64Data: string): GaussianSplatData {
  const bytes = Uint8Array.from(atob(base64Data), (c) => c.charCodeAt(0));
  const view = new DataView(bytes.buffer);

  // Parse PLY header to find properties
  const text = new TextDecoder().decode(bytes);
  const headerEnd = text.indexOf('end_header');
  const header = text.substring(0, headerEnd);

  // Extract vertex count
  const vertexMatch = header.match(/element vertex (\d+)/);
  if (!vertexMatch) {
    throw new Error('Invalid Gaussian splat PLY: no vertex count');
  }
  const count = parseInt(vertexMatch[1], 10);

  // Check format
  const formatMatch = header.match(/format (\S+)/);
  const format = formatMatch ? formatMatch[1] : 'ascii';

  // Parse properties to find byte layout
  const properties: Array<{name: string; type: string; offset: number; size: number}> = [];
  let currentOffset = 0;
  const propertyRegex = /property (\S+) (\S+)/g;
  let match;

  while ((match = propertyRegex.exec(header)) !== null) {
    const type = match[1];
    const name = match[2];
    let size = 4; // float is 4 bytes
    if (type === 'double') size = 8;
    if (type === 'uchar' || type === 'char') size = 1;
    if (type === 'ushort' || type === 'short') size = 2;

    properties.push({name, type, offset: currentOffset, size});
    currentOffset += size;
  }

  const stride = currentOffset;

  // Find property indices
  const findProp = (name: string) => properties.findIndex(p => p.name === name);
  const xIdx = findProp('x');
  const yIdx = findProp('y');
  const zIdx = findProp('z');

  // Scale properties (can be scale_0/1/2 or scale_x/y/z)
  let scaleXIdx = findProp('scale_0');
  let scaleYIdx = findProp('scale_1');
  let scaleZIdx = findProp('scale_2');
  if (scaleXIdx === -1) scaleXIdx = findProp('scale_x');
  if (scaleYIdx === -1) scaleYIdx = findProp('scale_y');
  if (scaleZIdx === -1) scaleZIdx = findProp('scale_z');

  // Rotation quaternion properties (rot_0/1/2/3)
  const rot0Idx = findProp('rot_0');
  const rot1Idx = findProp('rot_1');
  const rot2Idx = findProp('rot_2');
  const rot3Idx = findProp('rot_3');

  // Opacity
  const opacityIdx = findProp('opacity');

  // Color (spherical harmonics DC coefficients: f_dc_0/1/2 or r/g/b)
  let colorRIdx = findProp('f_dc_0');
  let colorGIdx = findProp('f_dc_1');
  let colorBIdx = findProp('f_dc_2');
  if (colorRIdx === -1) colorRIdx = findProp('r');
  if (colorGIdx === -1) colorGIdx = findProp('g');
  if (colorBIdx === -1) colorBIdx = findProp('b');

  // Initialize arrays
  const positions = new Float32Array(count * 3);
  const scales = new Float32Array(count * 3);
  const rotations = new Float32Array(count * 4);
  const opacities = new Float32Array(count);
  const colors = new Float32Array(count * 3);

  // Parse data based on format
  if (format.startsWith('binary')) {
    // Find data start (after "end_header\n")
    const dataStart = bytes.indexOf(0x0a, headerEnd) + 1;

    for (let i = 0; i < count; i++) {
      const offset = dataStart + i * stride;

      // Position
      if (xIdx >= 0 && yIdx >= 0 && zIdx >= 0) {
        positions[i * 3 + 0] = view.getFloat32(offset + properties[xIdx].offset, format.includes('little'));
        positions[i * 3 + 1] = view.getFloat32(offset + properties[yIdx].offset, format.includes('little'));
        positions[i * 3 + 2] = view.getFloat32(offset + properties[zIdx].offset, format.includes('little'));
      }

      // Scale (default to 1.0 if not present)
      scales[i * 3 + 0] = scaleXIdx >= 0 ? Math.exp(view.getFloat32(offset + properties[scaleXIdx].offset, format.includes('little'))) : 1.0;
      scales[i * 3 + 1] = scaleYIdx >= 0 ? Math.exp(view.getFloat32(offset + properties[scaleYIdx].offset, format.includes('little'))) : 1.0;
      scales[i * 3 + 2] = scaleZIdx >= 0 ? Math.exp(view.getFloat32(offset + properties[scaleZIdx].offset, format.includes('little'))) : 1.0;

      // Rotation quaternion (default to identity if not present)
      rotations[i * 4 + 0] = rot0Idx >= 0 ? view.getFloat32(offset + properties[rot0Idx].offset, format.includes('little')) : 1.0;
      rotations[i * 4 + 1] = rot1Idx >= 0 ? view.getFloat32(offset + properties[rot1Idx].offset, format.includes('little')) : 0.0;
      rotations[i * 4 + 2] = rot2Idx >= 0 ? view.getFloat32(offset + properties[rot2Idx].offset, format.includes('little')) : 0.0;
      rotations[i * 4 + 3] = rot3Idx >= 0 ? view.getFloat32(offset + properties[rot3Idx].offset, format.includes('little')) : 0.0;

      // Opacity (apply sigmoid if needed, default to 1.0)
      const rawOpacity = opacityIdx >= 0 ? view.getFloat32(offset + properties[opacityIdx].offset, format.includes('little')) : 0.0;
      opacities[i] = 1.0 / (1.0 + Math.exp(-rawOpacity));

      // Color (apply sigmoid for spherical harmonics, default to gray)
      const SH_C0 = 0.28209479177387814;
      colors[i * 3 + 0] = colorRIdx >= 0 ? 0.5 + SH_C0 * view.getFloat32(offset + properties[colorRIdx].offset, format.includes('little')) : 0.5;
      colors[i * 3 + 1] = colorGIdx >= 0 ? 0.5 + SH_C0 * view.getFloat32(offset + properties[colorGIdx].offset, format.includes('little')) : 0.5;
      colors[i * 3 + 2] = colorBIdx >= 0 ? 0.5 + SH_C0 * view.getFloat32(offset + properties[colorBIdx].offset, format.includes('little')) : 0.5;

      // Clamp colors to [0, 1]
      colors[i * 3 + 0] = Math.max(0, Math.min(1, colors[i * 3 + 0]));
      colors[i * 3 + 1] = Math.max(0, Math.min(1, colors[i * 3 + 1]));
      colors[i * 3 + 2] = Math.max(0, Math.min(1, colors[i * 3 + 2]));
    }
  } else {
    // ASCII format - parse text after header
    const lines = text.substring(headerEnd + 11).split('\n');
    let dataLineIdx = 0;

    for (let i = 0; i < count; i++) {
      const line = lines[dataLineIdx++];
      if (!line || !line.trim()) {
        dataLineIdx++;
        i--;
        continue;
      }

      const values = line.trim().split(/\s+/).map(parseFloat);

      // Position
      if (xIdx >= 0 && yIdx >= 0 && zIdx >= 0) {
        positions[i * 3 + 0] = values[xIdx];
        positions[i * 3 + 1] = values[yIdx];
        positions[i * 3 + 2] = values[zIdx];
      }

      // Scale
      scales[i * 3 + 0] = scaleXIdx >= 0 ? Math.exp(values[scaleXIdx]) : 1.0;
      scales[i * 3 + 1] = scaleYIdx >= 0 ? Math.exp(values[scaleYIdx]) : 1.0;
      scales[i * 3 + 2] = scaleZIdx >= 0 ? Math.exp(values[scaleZIdx]) : 1.0;

      // Rotation
      rotations[i * 4 + 0] = rot0Idx >= 0 ? values[rot0Idx] : 1.0;
      rotations[i * 4 + 1] = rot1Idx >= 0 ? values[rot1Idx] : 0.0;
      rotations[i * 4 + 2] = rot2Idx >= 0 ? values[rot2Idx] : 0.0;
      rotations[i * 4 + 3] = rot3Idx >= 0 ? values[rot3Idx] : 0.0;

      // Opacity
      const rawOpacity = opacityIdx >= 0 ? values[opacityIdx] : 0.0;
      opacities[i] = 1.0 / (1.0 + Math.exp(-rawOpacity));

      // Color
      const SH_C0 = 0.28209479177387814;
      colors[i * 3 + 0] = colorRIdx >= 0 ? 0.5 + SH_C0 * values[colorRIdx] : 0.5;
      colors[i * 3 + 1] = colorGIdx >= 0 ? 0.5 + SH_C0 * values[colorGIdx] : 0.5;
      colors[i * 3 + 2] = colorBIdx >= 0 ? 0.5 + SH_C0 * values[colorBIdx] : 0.5;

      // Clamp colors
      colors[i * 3 + 0] = Math.max(0, Math.min(1, colors[i * 3 + 0]));
      colors[i * 3 + 1] = Math.max(0, Math.min(1, colors[i * 3 + 1]));
      colors[i * 3 + 2] = Math.max(0, Math.min(1, colors[i * 3 + 2]));
    }
  }

  return {
    positions,
    scales,
    rotations,
    opacities,
    colors,
    count
  };
}

// Create a dummy vtkPolyData source for compatibility with pyvista-js rendering pipeline
// The actual rendering will be done with custom WebGL in the renderer
const _splatData = parseGaussianSplatData(base64Data);

// Store the splat data globally for the renderer to access
(window as any)[`_gaussianSplatData${splatIndex}`] = _splatData;

// Create a simple point cloud as a placeholder for vtk.js
const _source = vtk.Common.DataModel.vtkPolyData.newInstance();
_source.getPoints().setData(_splatData.positions, 3);

// Add point data for colors
const colorData = vtk.Common.Core.vtkDataArray.newInstance({
  numberOfComponents: 3,
  values: _splatData.colors,
  name: 'Colors',
});
_source.getPointData().setScalars(colorData);
