"""Pytest configuration for pyvista-js."""

from pathlib import Path

collect_ignore_glob = []

try:
    import mcp  # noqa: F401
except ImportError:
    collect_ignore_glob.append(str(Path("src") / "pyvista_js" / "mcp_server.py"))
