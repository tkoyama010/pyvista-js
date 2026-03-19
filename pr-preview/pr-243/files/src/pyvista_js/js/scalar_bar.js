// Create a scalar bar actor const scalarBarActor =
vtk.Rendering.Core.vtkScalarBarActor.newInstance(); // Configure scalar bar
appearance scalarBarActor.setAxisLabel('{{ TITLE }}');
scalarBarActor.setAutomated(true); // Set orientation and position
{{ ORIENTATION_CODE }} // Create a simple lookup table (placeholder for future
scalar support) const lookupTable =
vtk.Rendering.Core.vtkColorTransferFunction.newInstance();
lookupTable.addRGBPoint(0.0, 0.231, 0.299, 0.754); // viridis blue
lookupTable.addRGBPoint(0.25, 0.127, 0.566, 0.550); // viridis teal
lookupTable.addRGBPoint(0.5, 0.207, 0.718, 0.472); // viridis green
lookupTable.addRGBPoint(0.75, 0.993, 0.906, 0.144); // viridis yellow
lookupTable.addRGBPoint(1.0, 0.993, 0.906, 0.144); // viridis yellow
scalarBarActor.setScalarsToColors(lookupTable); // Add to renderer
renderer.addActor2D(scalarBarActor);
