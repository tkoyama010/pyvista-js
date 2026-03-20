# Playwright Browser Testing for PyVista-JS

This directory contains browser-based tests using Playwright to verify that PyVista plots render correctly in actual browser environments.

## Overview

The Playwright integration allows PyVista-JS to:

1. **Run tests in headless browsers** - No visible browser windows during test execution
2. **Verify actual rendering** - Test that plots actually render in real browsers with vtk.js
3. **Capture screenshots** - Take screenshots of rendered visualizations for visual regression testing
4. **Simulate user interactions** - Test mouse/keyboard interactions with 3D visualizations
5. **Run in CI without display servers** - Fully automated testing in GitHub Actions and other CI systems

## Test Structure

### Files

- `conftest.py` - Pytest fixtures for Playwright browser management
  - `playwright_browser` - Browser instance fixture
  - `browser_context` - Browser context fixture
  - `page` - Page fixture for browser automation
  - `check_cdn_access` - Checks if external CDNs are accessible

- `test_browser_rendering.py` - Browser-based rendering tests
  - Tests for single and multiple mesh rendering
  - Screenshot capture tests
  - Canvas interaction tests
  - Headless mode verification tests

## Running the Tests

### Prerequisites

1. Install test dependencies:
   ```bash
   pip install -e .[test]
   ```

2. Install Playwright browsers:
   ```bash
   playwright install chromium
   ```

### Running Tests

Run all Playwright tests:
```bash
pytest tests/test_browser_rendering.py -v
```

Run a specific test:
```bash
pytest tests/test_browser_rendering.py::test_plotter_renders_in_browser -v
```

Skip Playwright tests (run all other tests):
```bash
pytest -m "not playwright"
```

Run only Playwright tests:
```bash
pytest -m playwright
```

## Configuration

### Headless Mode

By default, tests run in headless mode (no visible browser). This is configured in `conftest.py`:

```python
@pytest.fixture(scope="session")
def browser_type_launch_args() -> dict[str, bool]:
    return {
        "headless": True,  # Always headless for CI
    }
```

### Viewport Size

The default viewport size is 1200x800, configured in `conftest.py`:

```python
@pytest.fixture(scope="session")
def browser_context_args() -> dict[str, dict[str, int]]:
    return {
        "viewport": {"width": 1200, "height": 800},
    }
```

## How It Works

### The Challenge

When running tests, PyVista-JS normally opens plots in the default web browser using `webbrowser.open()`. This creates several problems:

1. **Disruptive** - Browser windows pop up during test execution
2. **Not CI-friendly** - Requires a display server or X11 forwarding
3. **Hard to verify** - Can't programmatically check if rendering succeeded
4. **No automation** - Can't capture screenshots or test interactions

### The Solution

Playwright provides a programmatic way to control browser instances:

```python
# Instead of this (opens real browser):
plotter.show()

# We do this (controlled by Playwright):
plotter._renderer.create_container(plotter._container_id)
html = plotter._renderer._generate_standalone_html()

# Write HTML to file and load in Playwright browser
with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False) as f:
    f.write(html)
    temp_path = f.name

page.goto(Path(temp_path).as_uri())
page.wait_for_load_state("networkidle")

# Now we can verify rendering:
canvas = page.query_selector("canvas")
assert canvas is not None
```

### Test Pattern

All browser rendering tests follow this pattern:

1. Create a `Plotter` and add meshes
2. Generate standalone HTML (simulating what `show()` does)
3. Load HTML in Playwright-controlled browser
4. Wait for vtk.js to load and render
5. Verify rendering by checking for canvas element
6. Optionally capture screenshots or test interactions

## CI Integration

### GitHub Actions

The tests are automatically run in CI via `.github/workflows/test.yml`. The `tox.ini` configuration ensures Playwright browsers are installed before running tests:

```ini
[testenv]
deps =
    pytest>=7.0
    pytest-cov
    playwright>=1.40
    pytest-playwright>=0.4.0
commands_pre =
    playwright install chromium
commands =
    pytest tests/ src/ --cov=pyvista_js
```

### Network Requirements

**Important**: These tests require internet access to load vtk.js from the unpkg.com CDN. The tests include a `check_cdn_access` fixture to detect if CDN access is available. In environments without CDN access, tests will be skipped.

For production use in restricted environments, consider:
- Vendoring vtk.js locally in the test directory
- Using a local HTTP server to serve vtk.js
- Mocking the vtk.js library for unit tests

## Examples

### Example 1: Basic Rendering Test

```python
@pytest.mark.playwright
def test_sphere_renders(page: Page) -> None:
    """Test that a sphere renders in the browser."""
    plotter = Plotter()
    plotter.add_mesh(Sphere(), color="red")

    # Load in browser
    _load_plotter_html(page, plotter)

    # Verify canvas exists
    canvas = page.query_selector("canvas")
    assert canvas is not None
```

### Example 2: Screenshot Capture

```python
@pytest.mark.playwright
def test_screenshot(page: Page, tmp_path) -> None:
    """Capture a screenshot of the rendered plot."""
    plotter = Plotter()
    plotter.add_mesh(Sphere(), color="blue")

    _load_plotter_html(page, plotter)

    # Capture screenshot
    screenshot_path = tmp_path / "sphere.png"
    page.screenshot(path=str(screenshot_path))

    assert screenshot_path.exists()
```

### Example 3: User Interaction

```python
@pytest.mark.playwright
def test_mouse_interaction(page: Page) -> None:
    """Test mouse interaction with the 3D visualization."""
    plotter = Plotter()
    plotter.add_mesh(Sphere(), color="green")

    _load_plotter_html(page, plotter)

    # Find canvas and get its position
    canvas = page.query_selector("canvas")
    box = canvas.bounding_box()

    # Simulate mouse drag (rotation)
    center_x = box["x"] + box["width"] / 2
    center_y = box["y"] + box["height"] / 2

    page.mouse.move(center_x - 50, center_y)
    page.mouse.down()
    page.mouse.move(center_x + 50, center_y, steps=10)
    page.mouse.up()

    # Test passes if no errors occurred
```

## Benefits

### For Development

- **Fast feedback** - Verify rendering without manually opening browsers
- **Automated testing** - Test interactions and visual output programmatically
- **Debugging** - Capture screenshots when tests fail
- **Isolation** - Tests don't interfere with your actual browser

### For CI/CD

- **Headless execution** - No display server required
- **Parallel testing** - Run multiple browser tests simultaneously
- **Cross-platform** - Works on Linux, macOS, and Windows
- **Reliable** - Consistent rendering across environments

### For Quality

- **Visual regression testing** - Compare screenshots across commits
- **Interaction testing** - Verify mouse/keyboard controls work
- **Performance testing** - Measure rendering times
- **Compatibility testing** - Test across different browser versions

## Troubleshooting

### Tests Skip with "CDN not accessible"

The tests require internet access to load vtk.js. If you're in a restricted environment:

1. Check your network connection
2. Verify firewall allows access to unpkg.com
3. Consider vendoring vtk.js locally

### Chromium Not Found

If you get "Chromium not found" errors:

```bash
playwright install chromium
```

### Slow Tests

Browser tests are inherently slower than unit tests. To speed up:

1. Use `pytest -n auto` for parallel execution (requires pytest-xdist)
2. Run Playwright tests separately: `pytest -m playwright`
3. Skip Playwright tests in development: `pytest -m "not playwright"`

## Further Reading

- [Playwright Python Documentation](https://playwright.dev/python/)
- [pytest-playwright Plugin](https://github.com/microsoft/playwright-pytest)
- [PyVista-JS Documentation](https://github.com/tkoyama010/pyvista-js)
- [vtk.js Documentation](https://kitware.github.io/vtk-js/)
