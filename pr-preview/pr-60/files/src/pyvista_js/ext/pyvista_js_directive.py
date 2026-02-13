"""Sphinx extension for rendering pyvista-js visualizations."""

import hashlib
from typing import Any, ClassVar

from docutils import nodes  # type: ignore[import-untyped]
from docutils.parsers.rst import Directive, directives  # type: ignore[import-untyped]
from sphinx.application import Sphinx


class PyVistaJSNode(nodes.General, nodes.Element):
    """Node for pyvista-js visualizations."""


class PyVistaJSDirective(Directive):
    """Directive to embed pyvista-js visualizations.

    Example usage::

        .. pyvista-js::
            :height: 600

            import pyvista_js as pv
            plotter = pv.Plotter()
            sphere = pv.Sphere()
            plotter.add_mesh(sphere, color="red")
            plotter.show()
    """

    has_content = True
    required_arguments = 0
    optional_arguments = 0
    option_spec: ClassVar[dict[str, Any]] = {
        "height": directives.positive_int,
        "caption": directives.unchanged,
    }

    def run(self) -> list[PyVistaJSNode]:
        """Process the directive."""
        code = "\n".join(self.content)
        height = self.options.get("height", 500)
        caption = self.options.get("caption", "")

        node = PyVistaJSNode()
        node["code"] = code
        node["height"] = height
        node["caption"] = caption

        return [node]


def visit_pyvista_js_node_html(self: Any, node: PyVistaJSNode) -> None:  # noqa: ANN401
    """Generate HTML for pyvista-js visualization."""
    code = node["code"]
    height = node["height"]
    caption = node["caption"]

    # Generate a unique ID for this visualization
    viz_id = hashlib.md5(code.encode()).hexdigest()[:8]  # noqa: S324

    # Create HTML with embedded CSS and JupyterLite/Pyodide
    # Long lines are necessary for HTML/CSS formatting
    html = f"""
    <style>
    .pyvista-js-container {{
        margin: 1em 0;
    }}
    .pyvista-js-container .caption {{
        font-style: italic;
        color: #666;
        margin-bottom: 0.5em;
    }}
    .pyvista-js-code details {{
        margin-bottom: 1em;
    }}
    .pyvista-js-code summary {{
        cursor: pointer;
        color: #007bff;
        user-select: none;
    }}
    .pyvista-js-code pre {{
        background: #f5f5f5;
        padding: 1em;
        border-radius: 4px;
        overflow-x: auto;
    }}
    .pyvista-js-output {{
        background: #fafafa;
    }}
    </style>
    <div class="pyvista-js-container">
        {f'<p class="caption">{caption}</p>' if caption else ""}
        <div class="pyvista-js-code">
            <details>
                <summary>Show code</summary>
                <pre><code class="language-python">{code}</code></pre>
            </details>
        </div>
        <div id="pyvista-js-{viz_id}" class="pyvista-js-output" style="height: {height}px; border: 1px solid #ddd; margin: 1em 0;">
            <div style="display: flex; align-items: center; justify-content: center; height: 100%; color: #666;">
                <div style="text-align: center;">
                    <p>Interactive 3D visualization (requires JupyterLite)</p>
                    <p>
                        <a href="https://tkoyama010.github.io/pyvista-js/" target="_blank"
                           style="display: inline-block; padding: 10px 20px; background: #007bff; color: white; text-decoration: none; border-radius: 4px;">
                            Open in JupyterLite
                        </a>
                    </p>
                </div>
            </div>
        </div>
    </div>
    """  # noqa: E501

    self.body.append(html)


def depart_pyvista_js_node_html(self: Any, node: PyVistaJSNode) -> None:  # noqa: ANN401
    """Close the HTML for pyvista-js visualization."""


def setup(app: Sphinx) -> dict[str, Any]:
    """Set up the Sphinx extension."""
    app.add_node(
        PyVistaJSNode,
        html=(visit_pyvista_js_node_html, depart_pyvista_js_node_html),
    )
    app.add_directive("pyvista-js", PyVistaJSDirective)

    return {
        "version": "0.1",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
