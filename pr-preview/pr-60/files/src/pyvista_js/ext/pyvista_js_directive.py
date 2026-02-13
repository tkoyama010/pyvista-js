"""Sphinx extension for rendering pyvista-js visualizations."""

import hashlib
from typing import Any, ClassVar

from docutils import nodes  # type: ignore[import-untyped]
from docutils.parsers.rst import Directive, directives  # type: ignore[import-untyped]
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import PythonLexer
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

    # Highlight code with Pygments
    lexer = PythonLexer()
    formatter = HtmlFormatter(style="default", noclasses=False, cssclass="highlight")
    highlighted_code = highlight(code, lexer, formatter)

    # Create HTML with Thebe integration for interactive execution
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
    .pyvista-js-code {{
        margin-bottom: 1em;
    }}
    .pyvista-js-code .thebe-button {{
        margin-top: 0.5em;
        padding: 0.5em 1em;
        background: #28a745;
        color: white;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        font-size: 0.9em;
    }}
    .pyvista-js-code .thebe-button:hover {{
        background: #218838;
    }}
    .pyvista-js-output {{
        background: #fafafa;
        border: 1px solid #ddd;
        border-radius: 4px;
        min-height: {height}px;
        padding: 1em;
    }}
    .pyvista-js-output iframe {{
        width: 100%;
        height: 100%;
        border: none;
    }}
    </style>
    <div class="pyvista-js-container" id="container-{viz_id}">
        {f'<p class="caption">{caption}</p>' if caption else ""}
        <div class="pyvista-js-code">
            <pre data-executable="true" data-language="python">{code}</pre>
            {highlighted_code}
        </div>
        <div class="pyvista-js-output" id="output-{viz_id}">
            <div style="padding: 2em; text-align: center; color: #666;">
                <p>Click "Run Code" to execute and visualize</p>
                <p style="margin-top: 1em;">
                    <a href="https://tkoyama010.github.io/pyvista-js/" target="_blank"
                       style="display: inline-block; padding: 10px 20px; background: #007bff; color: white; text-decoration: none; border-radius: 4px;">
                        Open in JupyterLite
                    </a>
                </p>
            </div>
        </div>
    </div>
    """  # noqa: E501

    self.body.append(html)


def depart_pyvista_js_node_html(self: Any, node: PyVistaJSNode) -> None:  # noqa: ANN401
    """Close the HTML for pyvista-js visualization."""


def add_thebe_config(
    app: Sphinx,  # noqa: ARG001
    pagename: str,  # noqa: ARG001
    templatename: str,  # noqa: ARG001
    context: dict[str, Any],
    doctree: Any,  # noqa: ANN401
) -> None:
    """Add Thebe configuration to the page."""
    if doctree is None:
        return

    # Check if page contains pyvista-js nodes
    has_pyvista_js = any(isinstance(node, PyVistaJSNode) for node in doctree.traverse())
    if not has_pyvista_js:
        return

    # Add Thebe scripts and configuration
    thebe_config = """
    <script type="text/x-thebe-config">
    {
        requestKernel: true,
        binderOptions: {
            repo: "tkoyama010/pyvista-js",
            ref: "main"
        },
        kernelOptions: {
            name: "python3"
        }
    }
    </script>
    <script src="https://unpkg.com/thebe@latest/lib/index.js"></script>
    <script>
        document.addEventListener("DOMContentLoaded", function() {
            thebelab.bootstrap();
        });
    </script>
    """
    context.setdefault("body", "")
    context["body"] += thebe_config


def setup(app: Sphinx) -> dict[str, Any]:
    """Set up the Sphinx extension."""
    app.add_node(
        PyVistaJSNode,
        html=(visit_pyvista_js_node_html, depart_pyvista_js_node_html),
    )
    app.add_directive("pyvista-js", PyVistaJSDirective)
    app.connect("html-page-context", add_thebe_config)

    return {
        "version": "0.1",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
