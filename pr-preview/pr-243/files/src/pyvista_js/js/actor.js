{{ SOURCE_CODE }} // Create mapper const mapper{{ INDEX }} =
vtk.Rendering.Core.vtkMapper.newInstance(); {{ MAPPER_SETUP }}

{{ SCALAR_CODE }}
// Create actor const actor{{ INDEX }} =
vtk.Rendering.Core.vtkActor.newInstance();
actor{{ INDEX }}.setMapper(mapper{{ INDEX }});
actor{{ INDEX }}.getProperty().setColor({{ COLOR_R }}, {{ COLOR_G }},
{{ COLOR_B }}); actor{{ INDEX }}.getProperty().setOpacity({{ OPACITY }});
{{ EDGE_CODE }}
{{ STYLE_CODE }}
{{ PBR_CODE }}
{{ TEXTURE_CODE }}
// Add actor to renderer renderer.addActor(actor{{ INDEX }});
