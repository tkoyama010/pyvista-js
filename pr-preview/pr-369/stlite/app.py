"""Streamlit app for the pyvista-js stlite demo."""

import streamlit as st
import streamlit.components.v1 as components

import pyvista_js as pv
from pyvista_js import examples

color = st.selectbox(
    "Color",
    ["gray", "white", "red", "green", "blue", "yellow", "cyan", "magenta"],
)

opacity = st.slider("Opacity", min_value=0.0, max_value=1.0, value=0.8, step=0.1)

plotter = pv.Plotter()

mesh = examples.download_bunny()

plotter.add_mesh(mesh, color=color, opacity=opacity)

html = plotter._renderer._generate_standalone_html()  # noqa: SLF001
components.html(html, height=600)
