{{ SOURCE_CODE }} // Create mapper const {{ MAPPER }} =
vtk.Rendering.Core.vtkMapper.newInstance(); {{ MAPPER_SETUP }}

{{ SCALAR_CODE }}
// Create actor const {{ ACTOR }} = vtk.Rendering.Core.vtkActor.newInstance();
{{ ACTOR }}.setMapper({{ MAPPER }});
{{ ACTOR }}.getProperty().setColor({{ COLOR_R }}, {{ COLOR_G }}, {{ COLOR_B }});
{{ ACTOR }}.getProperty().setOpacity({{ OPACITY }}); {{ EDGE_CODE }}
{{ STYLE_CODE }}
{{ PBR_CODE }}
{{ TEXTURE_CODE }}
// Add actor to renderer renderer.addActor({{ ACTOR }});
