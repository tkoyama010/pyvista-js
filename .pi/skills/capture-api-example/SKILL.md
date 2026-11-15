______________________________________________________________________

## name: capture-api-example description: Captures an API documentation page after running its embedded "Try it with JupyterLite" example and opens a bug-report issue when problems are found. Use when checking whether a pyvista-js docs page example works, when asked to capture or screenshot a docs example, or when docs example regressions need to be reported as issues.

# Capture API Documentation Examples

Run the embedded JupyterLite example on a pyvista-js API documentation page
and verify it renders.

## Capture a page

```bash
uv run pyvista-js capture-api-example <DOC_URL> --output capture-artifacts
```

- Writes `capture-artifacts/capture.png` (full-page screenshot after the
  example cells ran) and `capture-artifacts/problems.json` (machine-readable
  problem report).
- Exit code 1 means problems were found. Possible problems: missing
  "Try it with JupyterLite!" button, `File Load Error` dialogs (missing
  generated notebooks), console/page errors, HTTP failures, a canvas that
  never appears, and blank render canvases.

## Open a bug-report issue for problems

```bash
uv run pyvista-js capture-api-example <DOC_URL> --open-issue
```

Requires the `gh` CLI and `GH_TOKEN` (or a logged-in `gh`). The issue
follows the repository's bug report template sections.

## Prerequisites

- `uv run playwright install chromium` (browsers)
- The `test` extra: `uv pip install -e '.[test]'` (playwright, pillow, numpy)

## Reading results

- Empty `problems` array in `problems.json`: the example ran and rendered.
- Non-empty: each entry describes one problem; attach `capture.png` when
  reporting. The CI workflow `.github/workflows/capture-try-example.yml`
  does this automatically and uploads the screenshot as the `capture`
  artifact.

## Notes

- Chromium runs in `--headless=new` mode because Read the Docs' Cloudflare
  challenge blocks the classic headless mode.
- Requires Python 3.12+.
