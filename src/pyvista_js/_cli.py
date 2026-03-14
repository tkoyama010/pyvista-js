"""Command-line interface for pyvista-js.

Provides a ``pyvista-js`` command with subcommands modelled after the
PyVista CLI so that common tasks (plotting mesh files, printing package
information) can be done without writing any Python code.
"""

from __future__ import annotations

import argparse
import logging
import platform
import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence

logger = logging.getLogger(__name__)

# Supported file extensions and the reader class name they map to.
_READER_MAP: dict[str, str] = {
    ".vtk": "PolyDataReader",
    ".ply": "PLYReader",
    ".obj": "OBJReader",
}


def _build_parser() -> argparse.ArgumentParser:
    """Build and return the top-level argument parser."""
    parser = argparse.ArgumentParser(
        prog="pyvista-js",
        description="PyVista-like CLI for browser-based 3-D visualization with vtk.js.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {_get_version()}",
    )

    subparsers = parser.add_subparsers(dest="command", metavar="COMMAND")
    subparsers.required = True

    _add_plot_subcommand(subparsers)
    _add_info_subcommand(subparsers)

    return parser


def _get_version() -> str:
    """Return the pyvista_js version string."""
    from pyvista_js import __version__  # noqa: PLC0415

    return __version__


def _add_plot_subcommand(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Register the ``plot`` subcommand."""
    plot_parser = subparsers.add_parser(
        "plot",
        help="Plot one or more mesh files in the browser.",
        description=(
            "Open one or more mesh files (.vtk, .ply, .obj) and render them "
            "in the default web browser using vtk.js."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    plot_parser.add_argument(
        "files",
        nargs="+",
        metavar="FILE",
        help="Mesh file(s) to plot. Supported formats: .vtk (ASCII), .ply (ASCII), .obj.",
    )
    plot_parser.add_argument(
        "--color",
        default=None,
        metavar="COLOR",
        help="Mesh colour applied to all files (e.g. ``red``, ``#ff0000``).",
    )
    plot_parser.add_argument(
        "--background",
        default=None,
        metavar="COLOR",
        help="Background colour (e.g. ``white``, ``black``). Default: renderer default.",
    )
    plot_parser.add_argument(
        "--opacity",
        type=float,
        default=1.0,
        metavar="FLOAT",
        help="Mesh opacity in the range [0, 1]. Default: 1.0.",
    )
    plot_parser.set_defaults(func=_cmd_plot)


def _add_info_subcommand(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Register the ``info`` subcommand."""
    info_parser = subparsers.add_parser(
        "info",
        help="Show pyvista-js version and environment information.",
        description="Print the pyvista-js version and basic Python environment details.",
    )
    info_parser.set_defaults(func=_cmd_info)


# ---------------------------------------------------------------------------
# Subcommand implementations
# ---------------------------------------------------------------------------


def _read_mesh(path: Path):  # type: ignore[return]  # noqa: ANN202
    """Read a mesh file and return a PolyData object.

    Parameters
    ----------
    path : Path
        Path to the mesh file. Must have a supported extension
        (``.vtk``, ``.ply``, or ``.obj``).

    Returns
    -------
    pyvista_js.mesh.PolyData
        The loaded mesh.

    Raises
    ------
    SystemExit
        When the file does not exist or its extension is not supported.

    """
    import pyvista_js as pv  # noqa: PLC0415

    if not path.exists():
        logger.error("file not found: %s", path)
        sys.exit(1)

    suffix = path.suffix.lower()
    reader_name = _READER_MAP.get(suffix)
    if reader_name is None:
        supported = ", ".join(_READER_MAP)
        logger.error("unsupported file format '%s'. Supported: %s", suffix, supported)
        sys.exit(1)

    reader_cls = getattr(pv, reader_name)
    return reader_cls(path).read()


def _cmd_plot(args: argparse.Namespace) -> None:
    """Implement the ``plot`` subcommand.

    Parameters
    ----------
    args : argparse.Namespace
        Parsed command-line arguments.

    """
    import pyvista_js as pv  # noqa: PLC0415

    plotter = pv.Plotter()

    if args.background is not None:
        plotter.background_color = args.background

    for file_str in args.files:
        path = Path(file_str)
        mesh = _read_mesh(path)
        kwargs: dict[str, object] = {"opacity": args.opacity}
        if args.color is not None:
            kwargs["color"] = args.color
        plotter.add_mesh(mesh, **kwargs)

    plotter.show()


def _cmd_info(args: argparse.Namespace) -> None:  # noqa: ARG001
    """Implement the ``info`` subcommand.

    Parameters
    ----------
    args : argparse.Namespace
        Parsed command-line arguments (unused).

    """
    import pyvista_js as pv  # noqa: PLC0415

    logger.info("pyvista-js : %s", pv.__version__)
    logger.info("Python     : %s", sys.version)
    logger.info("Platform   : %s", platform.platform())


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------


def main(argv: Sequence[str] | None = None) -> None:
    """Entry point for the ``pyvista-js`` command-line interface.

    Parameters
    ----------
    argv : sequence of str, optional
        Argument list to parse. Defaults to ``sys.argv[1:]``.

    """
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    parser = _build_parser()
    args = parser.parse_args(argv)
    args.func(args)
