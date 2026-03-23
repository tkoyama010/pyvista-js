// TypeScript declarations for vtk.js
// This provides type checking for vtk.js usage in templates

declare namespace vtk {
  namespace Common {
    namespace Core {
      interface vtkPoints {
        setData(data: Float32Array, numberOfComponents: number): void;
      }

      function vtkPoints(): {
        newInstance(): vtkPoints;
      };

      interface vtkCellArray {
        setData(data: Int32Array | Uint32Array): void;
      }

      function vtkCellArray(): {
        newInstance(): vtkCellArray;
      };
    }

    namespace DataModel {
      interface vtkPolyData {
        getPoints(): { getData(): Float32Array; };
        setPoints(points: Common.Core.vtkPoints): void;
        getPolys(): { getData(): Int32Array; };
        setPolys(polys: Common.Core.vtkCellArray): void;
        setLines(lines: Common.Core.vtkCellArray): void;
        getVerts(): { setData(data: Uint32Array): void; };
        getPointData(): {
          getScalars(): { getData(): Float32Array } | null;
        };
        getOutputData(port?: number): vtkPolyData;
        update?(): void;
      }

      function vtkPolyData(): {
        newInstance(): vtkPolyData;
      };
    }
  }

  namespace Rendering {
    namespace Core {
      interface vtkRenderer {
        setBackground(r: number, g: number, b: number): void;
        addActor(actor: vtkActor): void;
        resetCamera(): void;
      }

      function vtkRenderer(): {
        newInstance(): vtkRenderer;
      };

      interface vtkRenderWindow {
        addRenderer(renderer: vtkRenderer): void;
        addView(view: any): void;
        render(): void;
      }

      function vtkRenderWindow(): {
        newInstance(): vtkRenderWindow;
      };

      interface vtkRenderWindowInteractor {
        setInteractorStyle(style: any): void;
        setView(view: any): void;
        initialize(): void;
        bindEvents(element: HTMLElement): void;
      }

      function vtkRenderWindowInteractor(): {
        newInstance(): vtkRenderWindowInteractor;
      };

      interface vtkMapper {
        setInputData(data: Common.DataModel.vtkPolyData): void;
        setInputConnection(connection: any): void;
      }

      function vtkMapper(): {
        newInstance(): vtkMapper;
      };

      interface vtkActor {
        setMapper(mapper: vtkMapper): void;
        getProperty(): {
          setColor(r: number, g: number, b: number): void;
          setOpacity(opacity: number): void;
          setPointSize(size: number): void;
        };
      }

      function vtkActor(): {
        newInstance(): vtkActor;
      };
    }

    namespace OpenGL {
      interface vtkRenderWindow {
        setContainer(element: HTMLElement): void;
        setSize(width: number, height: number): void;
      }

      function vtkRenderWindow(): {
        newInstance(): vtkRenderWindow;
      };
    }
  }

  namespace Interaction {
    namespace Style {
      function vtkInteractorStyleTrackballCamera(): {
        newInstance(): any;
      };
    }
  }

  namespace Filters {
    namespace Sources {
      interface vtkSphereSource {
        getOutputPort(): any;
      }

      function vtkSphereSource(): {
        newInstance(params: {
          center: [number, number, number];
          radius: number;
          thetaResolution: number;
          phiResolution: number;
        }): vtkSphereSource;
      };

      interface vtkCubeSource {
        getOutputPort(): any;
      }

      function vtkCubeSource(): {
        newInstance(params: {
          xLength: number;
          yLength: number;
          zLength: number;
          center: [number, number, number];
        }): vtkCubeSource;
      };

      interface vtkCylinderSource {
        getOutputPort(): any;
      }

      function vtkCylinderSource(): {
        newInstance(params: {
          height: number;
          radius: number;
          resolution: number;
          center: [number, number, number];
        }): vtkCylinderSource;
      };

      interface vtkConeSource {
        getOutputPort(): any;
      }

      function vtkConeSource(): {
        newInstance(params: {
          height: number;
          radius: number;
          resolution: number;
          center: [number, number, number];
          direction: [number, number, number];
        }): vtkConeSource;
      };

      interface vtkArrowSource {
        getOutputPort(): any;
      }

      function vtkArrowSource(): {
        newInstance(): vtkArrowSource;
      };

      interface vtkLineSource {
        getOutputPort(): any;
      }

      function vtkLineSource(): {
        newInstance(params: {
          point1: [number, number, number];
          point2: [number, number, number];
        }): vtkLineSource;
      };

      interface vtkPlaneSource {
        getOutputPort(): any;
      }

      function vtkPlaneSource(): {
        newInstance(params: {
          xResolution: number;
          yResolution: number;
          origin: [number, number, number];
          point1: [number, number, number];
          point2: [number, number, number];
        }): vtkPlaneSource;
      };
    }

    namespace Texture {
      interface vtkTextureMapToSphere {
        setInputConnection(connection: any): void;
        getOutputPort(): any;
      }

      function vtkTextureMapToSphere(): {
        newInstance(): vtkTextureMapToSphere;
      };
    }
  }
}

// Global vtk object available in browser
declare const vtk: typeof vtk;
