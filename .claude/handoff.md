# Handoff: PR #366 — refactor: enable JavaScript formatting with djlint using data-* attributes

**Branch:** `add-djlintrc-format-js`
**PR:** https://github.com/tkoyama010/pyvista-js/pull/366
**Date:** 2026-03-24

---

## What This PR Does

Enables JavaScript formatting inside `<script>` tags via djlint's `--format-js` flag by separating Jinja2 `{{ }}` expressions from inline JavaScript using HTML `data-*` attributes. This prevents djlint from choking on Jinja2 syntax inside JS.

---

## Status

### ✅ Fixed

1. **`test_download_damaged_helmet_js_output`** (in `tests/test_readers.py`)
   - Root cause: `_GLTFMesh.generate_vtk_js_source()` used `str.replace("{{INDEX}}", ...)` but templates use `{{ INDEX }}` (with spaces).
   - Fix: Replaced with Jinja2 `_render(_GLTF_URL_SOURCE_TEMPLATE, INDEX=idx, GLTF_URL=self._gltf_url)`.
   - Commit: `fix: use _render() with Jinja2 for GLTF source templates`

2. **`test_generate_render_js`** (in `tests/test_rendering.py`)
   - Root cause: `_generate_render_js()` was producing HTML with `<div data-*>` elements, but `display(Javascript(...))` requires pure JavaScript (no HTML markup).
   - Fix: Added `_html_to_pure_js()` helper that converts `<div data-* style="display:none">` elements to `document.createElement` JS calls, and strips all `<script>` / `</script>` tags.
   - Commit: `fix: convert HTML data-config divs to JS DOM creation in _generate_render_js`

3. **`Javascript Error: Unexpected token '<'` in replite (JupyterLite)**
   - Root cause: `_generate_render_js()` was passing HTML to `display(Javascript(...))`.
   - Fix: Same as above (`_html_to_pure_js()`).

---

### ❌ Still Broken — **Must Fix Next**

**`rendering.html` template** — JavaScript code renders as visible text in browser output.

#### Root Cause

Commit `1a47adbc` ("fix: move Jinja2 code blocks outside script tags in rendering templates") moved `{{ LIGHTS_CODE }}`, `{{ ACTORS_CODE }}`, `{{ SCALAR_BAR_CODE }}`, `{{ TEXT_ACTORS_CODE }}`, `{{ ENVIRONMENT_CODE }}`, `{{ AXES_CODE }}`, and `{{ CAMERA_CODE }}` **outside** of any `<script>` block in `rendering.html`.

Because `_generate_lights_code()`, `_generate_camera_code()` etc. return **raw JavaScript strings** (not HTML-wrapped), placing them outside `<script>` tags causes the JS to render as visible plain text in the browser.

#### What You'll See

- Blank white canvas (no 3D scene rendered)
- JavaScript code printed as text below the canvas, e.g.:
  ```
  // Default directional light
  const light0 = vtk.Rendering.Core.vtkLight.newInstance();
  ...
  ```

#### Current `rendering.html` Structure (Broken)

```html
<script>
  (function() {
    function tryRender() { ... window.renderer = renderer; ... }
    tryRender();
  })();
</script>

{{ LIGHTS_CODE }}      ← raw JS → appears as TEXT!

{{ ACTORS_CODE }}      ← has own <div> + <script> → works OK

{{ SCALAR_BAR_CODE }}  ← raw JS → appears as TEXT!
{{ TEXT_ACTORS_CODE }} ← raw JS → appears as TEXT!
{{ ENVIRONMENT_CODE }} ← raw JS → appears as TEXT!
{{ AXES_CODE }}        ← raw JS → appears as TEXT!

<script>
  (function() {
    const renderer = window.renderer;
    renderer.resetCamera();
  })();
</script>
{{ CAMERA_CODE }}      ← raw JS → appears as TEXT!
<script>
  (function() {
    renderWindow.render();
  })();
</script>
```

#### What the Code Generators Return

| Variable | Generator | Returns |
|---|---|---|
| `LIGHTS_CODE` | `_generate_lights_code()` | Raw JS (references `renderer`) |
| `ACTORS_CODE` | `_generate_actor_code()` → `_render(_ACTOR_TEMPLATE)` | HTML with `<div data-*>` + `<script>` blocks |
| `SCALAR_BAR_CODE` | `_generate_scalar_bar_code()` → `_render(_SCALAR_BAR_TEMPLATE)` | **Already wrapped in `<script>` tags** (via `scalar_bar.html`) |
| `TEXT_ACTORS_CODE` | `_generate_text_actors_code()` | Raw JS |
| `ENVIRONMENT_CODE` | `_generate_environment_code()` | Raw JS (references `renderer`, `renderWindow`) |
| `AXES_CODE` | `_generate_axes_code()` | Raw JS (references `interactor`) |
| `CAMERA_CODE` | `_generate_camera_code()` | Raw JS (references `renderer`) |

> **Note:** `SCALAR_BAR_CODE` goes through `_render(scalar_bar.html)` which already has `<script>` and `</script>` tags. So it is HTML, not raw JS. It was incorrectly placed outside the `<script>` structure too, but its inner `<script>` block will execute.

#### How to Fix `rendering.html`

Wrap each raw JS code block in a `<script>` block with the necessary variable declarations (since they reference `renderer` etc. as locals but now `renderer` lives on `window`).

```html
{% if LIGHTS_CODE %}
<script>
  (function() {
    var renderer = window.renderer;
    if (!renderer) return;
    {{ LIGHTS_CODE }}
  })();
</script>
{% endif %}

{{ ACTORS_CODE }}

{% if SCALAR_BAR_CODE %}
{{ SCALAR_BAR_CODE }}
{% endif %}

{% if TEXT_ACTORS_CODE %}
<script>
  (function() {
    var renderer = window.renderer;
    if (!renderer) return;
    {{ TEXT_ACTORS_CODE }}
  })();
</script>
{% endif %}

{% if ENVIRONMENT_CODE %}
<script>
  (function() {
    var renderer = window.renderer;
    var renderWindow = window.renderWindow;
    if (!renderer) return;
    {{ ENVIRONMENT_CODE }}
  })();
</script>
{% endif %}

{% if AXES_CODE %}
<script>
  (function() {
    var interactor = window.interactor;
    if (!interactor) return;
    {{ AXES_CODE }}
  })();
</script>
{% endif %}

<script>
  (function() {
    var renderer = window.renderer;
    if (renderer) { renderer.resetCamera(); }
  })();
</script>

{% if CAMERA_CODE %}
<script>
  (function() {
    var renderer = window.renderer;
    if (!renderer) return;
    {{ CAMERA_CODE }}
  })();
</script>
{% endif %}

<script>
  (function() {
    var renderWindow = window.renderWindow;
    if (renderWindow) { renderWindow.render(); }
  })();
</script>
```

> `ACTORS_CODE` already contains full HTML with `<div data-*>` and `<script>` blocks from `actor.html`. It accesses `renderer` via the global scope (`window.renderer` = `renderer` at global scope). This is fine as-is.

---

## Key Design Decisions Already Made

### Why NOT `display(HTML(...))`

User asked: *"Can we convert templates with Jinja2 and display with `from IPython.display import HTML`?"*

**Answer: No** — JupyterLite uses DOMPurify which strips all `<script>` tags from HTML passed to `display(HTML(...))`. Also `<iframe>` elements are stripped. Only `display(Javascript(...))` can execute JavaScript in JupyterLite/replite.

### Why `display(Javascript(...))` requires pure JS

`display(Javascript(...))` expects a JavaScript string with **no HTML markup**. That's why `_html_to_pure_js()` converts `<div data-*>` elements to `document.createElement` calls and strips all `<script>` tags.

### `_html_to_pure_js()` — Key Function

Located in `src/pyvista_js/rendering.py`. Converts the rendered `rendering_js.html` output to pure JavaScript:
1. Replaces `<div data-* style="display:none"></div>` with `document.createElement('div')` + `dataset` assignments
2. Strips all `<script>` and `</script>` tags (keeps content)

---

## Files Changed in This PR

| File | Change |
|---|---|
| `src/pyvista_js/rendering.py` | Added `_html_to_pure_js()`, `_generate_standalone_html()`, restored `_generate_render_js()` using `_html_to_pure_js()` |
| `src/pyvista_js/readers.py` | Fixed `generate_vtk_js_source()` to use `_render()` instead of `str.replace()` |
| `src/pyvista_js/templates/rendering.html` | **BROKEN** — needs fix described above |
| `src/pyvista_js/templates/rendering_js.html` | Template for `display(Javascript(...))` path |
| `tests/test_rendering.py` | Updated assertions for `test_generate_render_js`, added `test_generate_standalone_html` |
| `.djlintrc` | djlint config enabling `--format-js` |

---

## How to Use `uv`

User explicitly requested using `uv` for all Python operations:
- Run tests: `uv run pytest tests/test_rendering.py -v`
- Run single test: `uv run pytest tests/test_rendering.py::test_generate_render_js -v`
- Install: `uv sync`

---

## Next Steps

1. **Fix `rendering.html`** using the template snippet above
2. Run tests locally: `uv run pytest tests/ -v`
3. Check browser output: `uv run python -c "from pyvista_js import Sphere; p = Sphere().plot(); ..."`
4. Push and check CI on PR #366
