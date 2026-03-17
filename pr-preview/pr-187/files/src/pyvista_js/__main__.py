"""pyvista-js command-line interface entry point."""

from __future__ import annotations

import logging

from pyvista_js._cli import main

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    main()
