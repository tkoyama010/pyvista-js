# AGENTS.md

Instructions for AI coding agents working in this repository. Keep changes small, follow the commands below, and run the checks before you finish.

## Commands

Run everything with `uv` (Python 3.12+ required; the project supports 3.12, 3.13, and 3.14):

```bash
# Run the test suite (includes doctests in src/, excludes browser tests)
uv run pytest -m "not playwright"

# Run a single test file
uv run pytest tests/test_mesh.py

# Run the full matrix (py312, py313, py314, lint) — this is what CI runs
uv run tox

# Lint and type-check Python (same as tox -e lint)
uv run ruff check .
uv run ruff format --check .
uv run mypy src/

# Build the TypeScript renderer (required before browser/Playwright tests pass)
npm ci
npm run build

# Check TypeScript and JS style
npm run typecheck
npm run lint

# Documentation build
uv run tox -e docs

# Pre-commit hooks (ruff, mdformat, pyproject-fmt, uv-lock check, djlint, ...)
uv run pre-commit run --all-files
```

You do not need a local environment beyond `uv` and `npm`: CI, pre-commit.ci, and Read the Docs previews verify everything. If local Playwright browsers are missing, run `uv run playwright install chromium` first.

## Testing

Framework is `pytest` (config in `pyproject.toml`). Browser tests use Playwright and are marked `@pytest.mark.playwright`; deselect them with `-m "not playwright"`.

Conventions, with an example from this repository's style:

```python
def test_add_mesh() -> None:
    """Test add_mesh adds a mesh to the plotter."""
    plotter = Plotter()
    mesh = Sphere()
    plotter.add_mesh(mesh)
    assert len(plotter.actors) == 1
```

- Name tests after the function under test: `test_<function_name>`, one test per behavior.
- Tests live in `tests/test_<module>.py`, mirroring `src/pyvista_js/<module>.py`.
- New features and bug fixes need a test. Run `uv run pytest -m "not playwright"` before you finish.
- Do not weaken assertions, add `# noqa`/`# type: ignore` without a code and reason, or skip tests to make them pass.

## Project structure

- `src/pyvista_js/` — the Python package (lazy-loaded modules: `mesh.py`, `plotter.py`, `camera.py`, `light.py`, `readers.py`, `rendering.py`, `text.py`, `texture.py`, `_cli.py`, ...). Public API is re-exported via `__init__.py` with `__init__.pyi` stubs.
- `src/pyvista_js/templates/` — generated artifacts (`renderer.js` is built from TypeScript by esbuild; HTML templates are formatted by djLint).
- `ts/` — TypeScript source for the renderer, bundled into `src/pyvista_js/templates/renderer.js`.
- `tests/` — pytest suite; `tests/data/` holds test fixtures.
- `docs/` — Sphinx docs (MyST, jupytext tutorials, `docs/decisions/` for ADRs, `docs/locale/` + `docs/pot/` for translations via Transifex).
- `jupyterlite/`, `stlite/` — browser notebook and Streamlit demos.
- [`.pre-commit-config.yaml`](.pre-commit-config.yaml), `biome.jsonc`, `pyproject.toml` — tooling configuration.

## Code style

- Python: `ruff` with `lint.select = ["ALL"]` (line length 100), formatted with `ruff format`. Type hints with `mypy src/` passing.
- TypeScript/JavaScript: Biome (`npm run lint`, `npm run format`), type-checked with `npm run typecheck` (`tsc --noEmit -p ts/tsconfig.json`).
- Markdown: mdformat (except `docs/decisions/`, which keeps MADR formatting as-is).
- Follow the scientific-python SPECs declared in `pyproject.toml`: SPEC 0 (minimum versions), SPEC 1 (lazy loading — never import `pyvista_js` submodules eagerly at module top level), SPEC 6 (upper-bound dependency constraints), SPEC 7 (`numpy.random.default_rng()` for any random generation), SPEC 8 (GitHub Actions pinned to commit SHAs).
- Use the standard `logging` module with a module-level `logger = logging.getLogger(__name__)` (see `src/pyvista_js/_cli.py`); the deprecated `logging.warn` is banned by pre-commit.

## Git workflow

- Branch from `main`. Small, focused commits.
- Commit messages follow [Conventional Commits](https://conventionalcommits.org): `feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `chore:`, `ci:`, `build:`, `style:`, `perf:`, `revert:`. The PR title must match this format; release-please generates the changelog from it.
- PRs use `.github/pull_request_template.md`. Issues use the templates in `.github/ISSUE_TEMPLATE/`. Do not modify those templates in the same PR as a code change.

## Boundaries — never do these

- **Never commit secrets**: API keys, tokens, credentials, or private keys. If a secret lands in a commit, remove it from history and rotate it.
- **Never commit generated artifacts**: `src/pyvista_js/templates/renderer.js` is built by esbuild from `ts/renderer.ts`; edit the TypeScript source and rebuild, not the bundle.
- **Never edit `uv.lock` by hand** — let `uv` and the `uv-lock` pre-commit hook manage it.
- **Never edit `docs/pot/` or `docs/locale/` machine-generated translation files** directly; translations go through Transifex (see `transifex.yml`).
- **Never change CI configuration** (`.github/workflows/`, pinned action SHAs, `tox.ini` env list) or `codecov.yml`, `renovate.json`, `release-please-config.json` in a feature PR.
- **Never bump the version** in `pyproject.toml`; release-please does that from Conventional Commits.

## Further reading

- [CONTRIBUTING.md](CONTRIBUTING.md) — full development setup and workflow
- [README.md](README.md) — project overview and usage
- [docs/decisions/](docs/decisions/) — architecture decision records (ADRs)
- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) — Contributor Covenant 3.0
