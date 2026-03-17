"""Script to capture a GIF of the pyvista-js JupyterLite demo.

This script automates capturing a preview GIF showing pyvista-js rendering in JupyterLite.
It can be run locally by maintainers or in CI with appropriate network access.

Requirements:
    pip install playwright imageio[ffmpeg] pillow
    playwright install chromium

Usage:
    python scripts/capture_preview.py
"""

import time
from pathlib import Path

from playwright.sync_api import sync_playwright


def capture_demo(output_dir: Path, demo_url: str = "https://tkoyama010.github.io/pyvista-js/"):
    """Capture the JupyterLite demo and save screenshots.

    Args:
        output_dir: Directory to save screenshots
        demo_url: URL of the JupyterLite demo

    Returns:
        Path to the screenshots directory
    """
    screenshots_dir = output_dir / "screenshots"
    screenshots_dir.mkdir(parents=True, exist_ok=True)

    print(f"Capturing demo from: {demo_url}")

    with sync_playwright() as p:
        # Launch browser with specific viewport size
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1200, "height": 800},
        )
        page = context.new_page()

        try:
            print("Navigating to JupyterLite demo...")
            page.goto(demo_url, wait_until="domcontentloaded", timeout=60000)

            # Wait for JupyterLite to load - this can take a while
            print("Waiting for JupyterLite to load...")
            page.wait_for_timeout(15000)  # Wait 15 seconds for initial load

            # Try to find and click on the demo notebook
            print("Looking for simple_demo.ipynb...")

            # Wait for file browser elements to appear
            page.wait_for_selector(".jp-DirListing-content", timeout=20000)

            # Look for the notebook file
            try:
                # Try multiple selectors for the notebook
                notebook_selectors = [
                    "text=simple_demo.ipynb",
                    "[title*='simple_demo']",
                    ".jp-DirListing-itemText:has-text('simple_demo')",
                ]

                notebook_found = False
                for selector in notebook_selectors:
                    try:
                        page.wait_for_selector(selector, timeout=5000)
                        page.click(selector)
                        notebook_found = True
                        print(f"Clicked on notebook using selector: {selector}")
                        break
                    except Exception:
                        continue

                if not notebook_found:
                    print("Could not find notebook, taking screenshots of main page")
                    page.screenshot(path=str(screenshots_dir / "screenshot_01.png"))
                    return screenshots_dir

                # Wait for notebook to open
                print("Waiting for notebook to open...")
                page.wait_for_timeout(5000)

                # Take screenshot of initial state
                print("Taking screenshot of notebook...")
                page.screenshot(path=str(screenshots_dir / "screenshot_01.png"))

                # Look for and run the notebook cells
                print("Attempting to run notebook cells...")

                # Wait for cells to be loaded
                page.wait_for_selector(".jp-Cell", timeout=10000)

                # Click on the first code cell to focus
                page.click(".jp-Cell")
                page.wait_for_timeout(1000)

                # Try to run all cells using the Run menu
                try:
                    # Try clicking the Run menu
                    page.click("text=Run", timeout=5000)
                    page.wait_for_timeout(500)
                    page.click("text=Run All Cells", timeout=5000)
                    print("Clicked 'Run All Cells' from menu")
                except Exception as e:
                    print(f"Could not use menu, trying keyboard shortcuts: {e}")
                    # Fallback: use keyboard shortcuts to run cells
                    # Ctrl+Shift+Enter runs all cells in some Jupyter implementations
                    page.keyboard.press("Control+Shift+Enter")
                    page.wait_for_timeout(1000)
                    # Or try running cells one by one with Shift+Enter
                    page.keyboard.press("Shift+Enter")
                    page.wait_for_timeout(1000)
                    page.keyboard.press("Shift+Enter")

                # Wait for the execution to complete and rendering to appear
                print("Waiting for 3D rendering to appear (this may take up to 15 seconds)...")
                page.wait_for_timeout(15000)

                # Take multiple screenshots to capture the rendering process
                print("Capturing rendering screenshots...")
                for i in range(2, 15):
                    page.screenshot(path=str(screenshots_dir / f"screenshot_{i:02d}.png"))
                    page.wait_for_timeout(500)  # 500ms between frames

                print(f"Captured {14} screenshots successfully")

            except Exception as e:
                print(f"Error during notebook interaction: {e}")
                # Still take some screenshots of what we have
                for i in range(2, 5):
                    page.screenshot(path=str(screenshots_dir / f"screenshot_{i:02d}.png"))
                    page.wait_for_timeout(1000)

        except Exception as e:
            print(f"Error navigating to demo: {e}")
            # Take a screenshot to see what we got
            try:
                page.screenshot(path=str(screenshots_dir / "error_screenshot.png"))
            except Exception:
                pass
        finally:
            context.close()
            browser.close()

    return screenshots_dir


def create_gif_from_screenshots(screenshots_dir: Path, output_path: Path, fps: int = 2):
    """Create a GIF from screenshots using imageio.

    Args:
        screenshots_dir: Directory containing screenshot PNG files
        output_path: Path where the GIF should be saved
        fps: Frames per second for the GIF (default: 2)

    Returns:
        True if successful, False otherwise
    """
    import imageio.v3 as iio

    screenshot_files = sorted(screenshots_dir.glob("screenshot_*.png"))

    if not screenshot_files:
        print("Error: No screenshots found!")
        return False

    print(f"Found {len(screenshot_files)} screenshots")

    # Load all images
    images = []
    for i, filepath in enumerate(screenshot_files):
        print(f"  Loading {filepath.name}...")
        images.append(iio.imread(filepath))

    # Calculate duration per frame in milliseconds
    duration_ms = int(1000 / fps)

    # Create GIF
    print(f"Creating GIF at {output_path} ({fps} fps)...")
    iio.imwrite(
        output_path,
        images,
        duration=duration_ms,
        loop=0,  # Infinite loop
    )

    print(f"✓ GIF created successfully: {output_path}")
    print(f"  Size: {output_path.stat().st_size / 1024:.1f} KB")
    print(f"  Frames: {len(images)}")
    print(f"  Duration: ~{len(images) / fps:.1f} seconds")

    return True


def main():
    """Main function to capture demo and create GIF."""
    print("=" * 60)
    print("PyVista-js JupyterLite Demo Capture")
    print("=" * 60)

    # Setup paths
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent

    # Use /tmp for temporary files
    temp_dir = Path("/tmp/demo_capture")
    temp_dir.mkdir(exist_ok=True)

    # Assets directory in the repository
    assets_dir = repo_root / "assets"
    assets_dir.mkdir(exist_ok=True)

    try:
        # Capture screenshots
        print("\nStep 1: Capturing screenshots from JupyterLite demo...")
        screenshots_dir = capture_demo(temp_dir)

        # Verify we got some screenshots
        screenshot_files = list(screenshots_dir.glob("screenshot_*.png"))
        if not screenshot_files:
            print("\n✗ Failed: No screenshots were captured")
            print("  This might be due to network restrictions or the demo not loading properly")
            return 1

        # Create GIF
        print("\nStep 2: Creating GIF from screenshots...")
        output_gif = assets_dir / "preview.gif"
        success = create_gif_from_screenshots(screenshots_dir, output_gif, fps=2)

        if success:
            print("\n" + "=" * 60)
            print("✓ SUCCESS!")
            print("=" * 60)
            print(f"Preview GIF saved to: {output_gif}")
            print(f"You can now commit this file and update the README.md")
            return 0
        else:
            print("\n✗ Failed to create GIF")
            return 1

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
