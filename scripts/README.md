# Preview Capture Script

This directory contains the script to generate a preview GIF of the pyvista-js JupyterLite demo.

## Requirements

```bash
pip install playwright imageio[ffmpeg] pillow
playwright install chromium
```

## Usage

Run the script from the repository root:

```bash
python scripts/capture_preview.py
```

This will:
1. Navigate to the JupyterLite demo at https://tkoyama010.github.io/pyvista-js/
2. Open the `simple_demo.ipynb` notebook
3. Execute the cells to render the 3D sphere
4. Capture screenshots during the rendering
5. Create an animated GIF at `assets/preview.gif`

## Manual Capture (Alternative)

If the automated script doesn't work due to network restrictions or other issues, you can manually capture the preview:

1. Open https://tkoyama010.github.io/pyvista-js/ in your browser
2. Click on `simple_demo.ipynb` to open the demo notebook
3. Run all cells (Shift + Enter on each cell, or Run -> Run All Cells)
4. Wait for the 3D rendering to appear
5. Use a screen recording tool to capture the rendering
6. Convert to GIF and save as `assets/preview.gif`

## CI Integration (Optional)

To automatically regenerate the preview when the demo changes, you can add a GitHub Actions workflow:

```yaml
name: Update Preview GIF
on:
  workflow_dispatch:

jobs:
  update-preview:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: |
          pip install playwright imageio[ffmpeg] pillow
          playwright install chromium
          python scripts/capture_preview.py
      - uses: stefanzweifel/git-auto-commit-action@v5
        with:
          commit_message: "chore: update preview GIF"
          file_pattern: assets/preview.gif
```
