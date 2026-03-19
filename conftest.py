"""Pytest configuration for pyvista-js."""

import os

collect_ignore_glob = []

try:
    import mcp  # noqa: F401
except ImportError:
    collect_ignore_glob.append(os.path.join("src", "pyvista_js", "mcp_server.py"))
