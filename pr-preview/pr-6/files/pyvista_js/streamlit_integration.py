"""Streamlit integration for pyvista-js.

Provides components for displaying pyvista-js visualizations in Streamlit and stlite.
"""

import sys

# Check if streamlit is available
try:
    import streamlit as st
    import streamlit.components.v1 as components
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False


def pyvista_chart(plotter, height: int = 600, key: str = None):
    """Display a pyvista-js Plotter in Streamlit.
    
    This function renders a pyvista-js visualization as a Streamlit component.
    It works in both standard Streamlit and stlite environments.
    
    Parameters
    ----------
    plotter : Plotter
        The pyvista-js Plotter instance to display.
    height : int, optional
        Height of the visualization in pixels. Default is 600.
    key : str, optional
        Unique key for the component.
        
    Examples
    --------
    >>> import pyvista_js as pv
    >>> import streamlit as st
    >>> 
    >>> plotter = pv.Plotter()
    >>> sphere = pv.Sphere()
    >>> plotter.add_mesh(sphere, color='red')
    >>> 
    >>> pv.pyvista_chart(plotter, height=500)
    """
    if not STREAMLIT_AVAILABLE:
        raise ImportError(
            "Streamlit is not available. Install with: pip install streamlit"
        )
    
    # Generate HTML for vtk.js visualization
    html_code = _generate_vtkjs_html(plotter, height)
    
    # Display using Streamlit components
    components.html(html_code, height=height, scrolling=False)


def _generate_vtkjs_html(plotter, height: int) -> str:
    """Generate HTML code for vtk.js visualization.
    
    Parameters
    ----------
    plotter : Plotter
        The Plotter instance.
    height : int
        Container height.
        
    Returns
    -------
    str
        HTML code with embedded vtk.js visualization.
    """
    # Extract mesh data from plotter
    meshes_data = []
    for actor_info in plotter.actors:
        mesh = actor_info['mesh']
        meshes_data.append({
            'points': mesh.points.tolist(),
            'n_points': mesh.n_points,
            'color': actor_info['color'],
            'opacity': actor_info['opacity'],
        })
    
    # Generate HTML
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            margin: 0;
            padding: 0;
            overflow: hidden;
        }}
        #container {{
            width: 100%;
            height: {height}px;
        }}
    </style>
    <script src="https://unpkg.com/vtk.js"></script>
</head>
<body>
    <div id="container"></div>
    <script type="module">
        const {{ vtk }} = window;
        
        // Create renderer and render window
        const renderer = vtk.Rendering.Core.vtkRenderer.newInstance();
        renderer.setBackground(0.2, 0.3, 0.4);
        
        const renderWindow = vtk.Rendering.Core.vtkRenderWindow.newInstance();
        renderWindow.addRenderer(renderer);
        
        // Create OpenGL render window
        const openglRenderWindow = vtk.Rendering.OpenGL.vtkRenderWindow.newInstance();
        renderWindow.addView(openglRenderWindow);
        
        // Create interactor
        const interactor = vtk.Rendering.Core.vtkRenderWindowInteractor.newInstance();
        interactor.setView(openglRenderWindow);
        interactor.initialize();
        interactor.bindEvents(document.getElementById('container'));
        
        // Set container
        const container = document.getElementById('container');
        openglRenderWindow.setContainer(container);
        
        const {{ width, height }} = container.getBoundingClientRect();
        openglRenderWindow.setSize(width, height);
        
        // Mesh data from Python
        const meshesData = {meshes_data};
        
        // Add each mesh
        meshesData.forEach(meshData => {{
            // Create polydata
            const polydata = vtk.Common.DataModel.vtkPolyData.newInstance();
            
            // Set points
            const points = new Float32Array(meshData.points.flat());
            polydata.getPoints().setData(points, 3);
            
            // Generate point cloud connectivity (for now)
            const verts = new Uint32Array(meshData.n_points * 2);
            for (let i = 0; i < meshData.n_points; i++) {{
                verts[i * 2] = 1;
                verts[i * 2 + 1] = i;
            }}
            polydata.getVerts().setData(verts);
            
            // Create mapper
            const mapper = vtk.Rendering.Core.vtkMapper.newInstance();
            mapper.setInputData(polydata);
            
            // Create actor
            const actor = vtk.Rendering.Core.vtkActor.newInstance();
            actor.setMapper(mapper);
            
            // Set color
            if (meshData.color) {{
                let rgb;
                if (typeof meshData.color === 'string') {{
                    rgb = nameToRGB(meshData.color);
                }} else {{
                    rgb = meshData.color;
                }}
                actor.getProperty().setColor(...rgb);
            }}
            
            // Set opacity
            actor.getProperty().setOpacity(meshData.opacity || 1.0);
            
            // Set point size for visibility
            actor.getProperty().setPointSize(5);
            
            renderer.addActor(actor);
        }});
        
        // Reset camera and render
        renderer.resetCamera();
        renderWindow.render();
        
        // Color name to RGB conversion
        function nameToRGB(colorName) {{
            const colors = {{
                'red': [1.0, 0.0, 0.0],
                'green': [0.0, 1.0, 0.0],
                'blue': [0.0, 0.0, 1.0],
                'yellow': [1.0, 1.0, 0.0],
                'cyan': [0.0, 1.0, 1.0],
                'magenta': [1.0, 0.0, 1.0],
                'white': [1.0, 1.0, 1.0],
                'black': [0.0, 0.0, 0.0],
            }};
            return colors[colorName.toLowerCase()] || [0.5, 0.5, 0.5];
        }}
        
        // Handle window resize
        window.addEventListener('resize', () => {{
            const {{ width, height }} = container.getBoundingClientRect();
            openglRenderWindow.setSize(width, height);
            renderWindow.render();
        }});
    </script>
</body>
</html>
"""
    return html


# Convenience function for Streamlit
if STREAMLIT_AVAILABLE:
    # Add to streamlit namespace
    st.pyvista_chart = pyvista_chart
