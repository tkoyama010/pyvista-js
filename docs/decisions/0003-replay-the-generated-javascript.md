---
status: accepted
date: 2026-11-04
decision-makers: [tkoyama010]
consulted: [larsoner]
informed: []
---

# Replay the Generated JavaScript in Non-IPython Pages

## Context and Problem Statement

`VTKJSRenderer` has two render modes selected by `use_ipython`. The IPython path generates vtk.js JavaScript and displays it through `display(Javascript(...))`. The direct-DOM path (reached in Pyodide without IPython) exists but is incomplete: `create_container()` builds a `<div>` without creating any vtk.js objects for it, and `render()` calls `self.renderer.resetCamera()` and `self.render_window.render()` on attributes that pyvista-js never sets — the code even carries `# type: ignore[attr-defined]` comments on both lines (`src/pyvista_js/rendering.py`, lines 1264–1265). Calling `render()` in that mode therefore raises `AttributeError`. The bug was found while improving test coverage in [pyvista-js#776](https://github.com/tkoyama010/pyvista-js/pull/776) and reported in [pyvista-js#778](https://github.com/tkoyama010/pyvista-js/issues/778): should the direct-DOM path be implemented properly, or removed?

Review of this record noted that no current demo reaches the direct-DOM path. JupyterLite's Pyodide kernel includes IPython, so it takes the IPython path; the Streamlit demo renders with `generate_standalone_html()` and never calls `VTKJSRenderer.render()`; and the `stlite/` directory named in the contributing instructions is stale and absent from `main`. A concrete non-IPython use case (for example, a PyScript page embedding Pyodide without IPython) therefore remains hypothetical.

## Decision Drivers

* **Correctness over dead code**: A code path that always raises `AttributeError` when reached is a defect, and the `type: ignore` annotations hide it from both mypy and readers.
* **Reachability of a plausible target**: no current demo reaches the direct-DOM path, but Pyodide without IPython (for example, a PyScript page) is a plausible future embedding, and a path that always crashes there gives no clear error for that configuration.
* **Testability**: Coverage tooling flags the branch, and the maintainers want the suite to cover it either way — a tested implementation is also the natural target of the existing Playwright tests.
* **Maintenance cost**: Implementing direct-DOM rendering means creating and wiring the full vtk.js object graph (`render_window`, `renderer`, context) from Python in `src/pyvista_js/rendering.py`, duplicating logic that today lives in the vtk.js wiring of `ts/renderer.ts` and is embedded into the generated JavaScript of the IPython path.
* **Time to a safe release**: the crash defect should disappear from released pyvista-js soon; options that require substantial new implementation and testing delay that release.
* **Loud and helpful failure**: a configuration that cannot render should fail with an explicit, informative message suggesting a working alternative, instead of crashing or silently doing nothing.

## Considered Options

* Implement the direct-DOM path: make `create_container()` create the vtk.js object graph and `render()` drive it.
* Remove the direct-DOM path: make the non-IPython branch raise an explicit, informative error.
* Keep the path but document it as experimental and guard `render()` so it degrades gracefully instead of crashing.
* Replay the generated JavaScript in non-IPython pages: run the existing `_generate_render_js()` output of the IPython path inside the page instead of rebuilding the vtk.js object graph from Python.
* Share a single TypeScript render entry point: refactor `ts/renderer.ts` so both the IPython path and the direct-DOM path drive rendering through one entry function, with Python passing the rendering data and the container element.

## Decision Outcome

Chosen option: "Replay the generated JavaScript in non-IPython pages", because it removes the guaranteed crash, gives a non-IPython embedding real rendering, and needs no TypeScript changes: the non-IPython branch emits the JavaScript the IPython path already generates through `_generate_render_js()` inside the container `create_container()` builds, and the `# type: ignore[attr-defined]` comments go away with the dead branch. Review of this record raised this option and showed an inclination toward "Remove the direct-DOM path"; the record chose replay over removal because removal trades away the only Good under "Reachability of a plausible target" for neutrality elsewhere, while replay keeps every Good of removal except "Loud and helpful failure", where a Python-side precondition check with an informative message covers the gap. The decision therefore remains `proposed` pending that discussion in the PR that carries this record.

### Consequences

* Good, because it removes the guaranteed `AttributeError` defect with a deliberate behavior, and the `type: ignore[attr-defined]` markers that mask it can be deleted.
* Good, because a possible non-IPython embedding gets real rendering drawn by the same code as the IPython path.
* Neutral, because standalone execution of the replayed output must first be proven by a browser test.
* Good, because nothing new must stay in sync with `ts/renderer.ts`, at the bounded cost of `create_container()` still placing a suitable host element.
* Good, because only Python-side changes are needed, with no TypeScript rebuild in the loop.
* Neutral, because if the replayed output fails in the browser, the failure carries no informative message until a precondition check fills that gap.

### Confirmation

Confirmed by tests that exercise the actual direct-DOM lifecycle without injected attributes: a unit test that calls `create_container()` and `render()` in Pyodide without IPython and without preset `renderer`/`render_window` attributes (note that `tests/test_rendering.py::test_render_loads_vtkjs_in_pyodide` cannot serve as this check because it injects stand-ins for both attributes, so it passes with the defect still present), plus a browser test that renders a mesh in Pyodide without IPython and thereby proves the replayed `_generate_render_js()` output runs standalone. Accepted after discussion in [tkoyama010/pyvista-js#797](https://github.com/tkoyama010/pyvista-js/pull/797).

## Pros and Cons of the Options

### Implement the direct-DOM path

At `create_container()` time, construct the vtk.js object graph for the container; `render()` then calls `resetCamera()` and `render_window.render()` on real objects.

* Good, because it removes the guaranteed `AttributeError` defect, and the `type: ignore[attr-defined]` markers that mask it can be deleted.
* Good, because a possible Pyodide-without-IPython embedding gets real rendering instead of a crash.
* Good, because the direct-DOM branch becomes reachable and testable by tests that exercise the real lifecycle rather than injected stand-ins.
* Neutral, because a second vtk.js object wiring path now exists alongside the generated-JavaScript IPython path, and the two must be kept in sync.
* Bad, because the fix waits on new vtk.js wiring plus new unit and browser tests before it can ship.
* Neutral, because a completed implementation leaves no unsupported configuration to fail, but until it lands the crash stays.

### Remove the direct-DOM path

Raise an explicit `RuntimeError` with guidance (for example, "install or initialize IPython, or use `generate_standalone_html()`") when not in IPython.

* Good, because it replaces the `AttributeError` with a loud, intentional error and removes the masked dead path and its `type: ignore` comments.
* Bad, because Pyodide-without-IPython becomes a permanently unsupported configuration, with `VTKJSRenderer` degrading to IPython-only despite accepting that environment.
* Neutral, because the exposed failure is deterministic and easy to test, and the Playwright surface neither shrinks nor grows.
* Good, because it is the smallest change, with no duplicated vtk.js wiring to maintain.
* Good, because a small Python-side change can ship the fix quickly.
* Good, because the exposed error carries guidance, such as installing IPython or using `generate_standalone_html()`.

### Keep the path but document it as experimental

Keep the path untouched but catch `AttributeError` and warn.

* Bad, because the masked defect and the `type: ignore[attr-defined]` comments stay, and a caught `AttributeError` turns the crash into a silent no-op, which is worse than a clear error.
* Bad, because in Pyodide without IPython the scene still does not render, so the supported use case gets no visualization.
* Good, because the guarded branch becomes deterministic and testable, and a no-IPython test needs no stand-ins for `renderer` or `render_window`.
* Good, because the implementation work is near zero: no vtk.js wiring is created.
* Neutral, because the catch-and-warn guard is a small change, but it leaves the rendering question unresolved.
* Bad, because the guarded branch still renders nothing and only prints a warning instead of informative guidance.

### Replay the generated JavaScript in non-IPython pages (proposed)

Make the non-IPython branch emit the same JavaScript the IPython path generates through `_generate_render_js()` and inject it into the container built by `create_container()`, reusing the single vtk.js object wiring that lives in `ts/renderer.ts`.

* Good, because it removes the guaranteed `AttributeError` defect with a deliberate behavior instead of a crash.
* Good, because a possible non-IPython embedding gets real rendering drawn by the same code as the IPython path.
* Neutral, because the generated JavaScript is written for the IPython display context, so standalone execution must first be proven by a browser test.
* Good, because nothing new must stay in sync with `ts/renderer.ts`, at the bounded cost of `create_container()` still placing a suitable host element.
* Good, because only Python-side changes are needed, with no TypeScript rebuild in the loop.
* Neutral, because if the replayed output fails in the browser, the failure carries no informative message.

### Share a single TypeScript render entry point

Refactor `ts/renderer.ts` so the IPython path and the direct-DOM path drive rendering through the same entry function; Python passes the rendering data and the container element, and the bundle creates the vtk.js object graph.

* Good, because it removes the guaranteed `AttributeError` defect with a deliberate behavior instead of a crash.
* Good, because a possible Pyodide-without-IPython embedding gets real rendering.
* Good, because both modes exercise the same tested code, so one browser test covers the shared entry point.
* Good, because a single vtk.js wiring remains: there is no second object graph to keep in sync, at only the one-time cost of refactoring the entry function out of `ts/renderer.ts` and rebuilding the bundle.
* Bad, because the fix waits on the TypeScript refactor, rebuild, and new tests.
* Neutral, because a completed shared entry point leaves no unsupported configuration to fail, but until it lands the crash stays.

## More Information

* Issue: [tkoyama010/pyvista-js#778](https://github.com/tkoyama010/pyvista-js/issues/778)
* Coverage PR that surfaced it: [tkoyama010/pyvista-js#776](https://github.com/tkoyama010/pyvista-js/pull/776)
* Review discussion of this record: [tkoyama010/pyvista-js#797](https://github.com/tkoyama010/pyvista-js/pull/797)
* Affected code: `src/pyvista_js/rendering.py`, `VTKJSRenderer.create_container` and `VTKJSRenderer.render`
* ADR-0001 for the related rendering-backend decision, ADR-0000 for the record format used here.
