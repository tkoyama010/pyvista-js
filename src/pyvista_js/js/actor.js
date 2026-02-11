{{SOURCE_CODE}}

      // Create mapper
      const mapper{{INDEX}} = vtk.Rendering.Core.vtkMapper.newInstance();
      {{MAPPER_SETUP}}

      // Create actor
      const actor{{INDEX}} = vtk.Rendering.Core.vtkActor.newInstance();
      actor{{INDEX}}.setMapper(mapper{{INDEX}});
      actor{{INDEX}}.getProperty().setColor({{COLOR_R}}, {{COLOR_G}}, {{COLOR_B}});
      actor{{INDEX}}.getProperty().setOpacity({{OPACITY}});

      // Add actor to renderer
      renderer.addActor(actor{{INDEX}});
