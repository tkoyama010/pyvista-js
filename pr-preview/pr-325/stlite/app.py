import streamlit as st
import streamlit.components.v1 as components

import pyvista_js as pv
from pyvista_js import examples

st.title("pyvista-js")

geometry = st.selectbox("Geometry", ["Bunny", "Sphere", "Cube", "Cylinder"])

color = st.selectbox(
    "Color", ["gray", "white", "red", "green", "blue", "yellow", "cyan", "magenta"]
)

opacity = st.slider("Opacity", min_value=0.0, max_value=1.0, value=0.8, step=0.1)

plotter = pv.Plotter()

if geometry == "Bunny":
    mesh = examples.download_bunny()
elif geometry == "Sphere":
    mesh = pv.Sphere(radius=1.0)
elif geometry == "Cube":
    mesh = pv.Cube()
else:
    mesh = pv.Cylinder(radius=0.5, height=2.0)

plotter.add_mesh(mesh, color=color, opacity=opacity)

html = plotter._renderer._generate_standalone_html()
components.html(html, height=600)
