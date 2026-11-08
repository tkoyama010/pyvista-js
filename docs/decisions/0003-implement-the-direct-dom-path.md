---
status: proposed
date: 2026-11-04
decision-makers: [tkoyama010]
consulted: [larsoner]
informed: []
---

# Implement the Direct-DOM Path

## Context and Problem Statement

`VTKJSRenderer` has two render modes selected by `use_ipython`. The IPython path generates vtk.js JavaScript and displays it through `display(Javascript(...))`. The direct-DOM path (reached in Pyodide without IPython) exists but is incomplete: `create_container()` builds a `<div>` without creating any vtk.js objects for it, and `render()` calls `self.renderer.resetCamera()` and `self.render_window.render()` on attributes that pyvista-js never sets — the code even carries `# type: ignore[attr-defined]` comments on both lines (`src/pyvista_js/rendering.py`, lines 1264–1265). Calling `render()` in that mode therefore raises `AttributeError`. The bug was found while improving test coverage in [pyvista-js#776](https://github.com/tkoyama010/pyvista-js/pull/776) and reported in [pyvista-js#778](https://github.com/tkoyama010/pyvista-js/issues/778): should the direct-DOM path be implemented properly, or removed?

## Decision Drivers

* **Correctness over dead code**: A code path that always raises `AttributeError` when reached is a defect, and the `type: ignore` annotations hide it from both mypy and readers.
* **Pyodide is a supported target**: pyvista-js explicitly supports Pyodide environments ({file}`jupyterlite/`, {file}`stlite/` demos), and Pyodide without IPython is a real configuration, so crashing there breaks a supported use case.
* **Testability**: Coverage tooling flags the branch, and the maintainers want the suite to cover it either way — a tested implementation is also the natural target of the existing Playwright tests.
* **Maintenance cost**: Implementing direct-DOM rendering means creating and wiring the full vtk.js object graph (`render_window`, `renderer`, context) from Python in `src/pyvista_js/rendering.py`, duplicating logic that today lives in the vtk.js wiring of `ts/renderer.ts` and is embedded into the generated JavaScript of the IPython path.

## Considered Options

* Implement the direct-DOM path: make `create_container()` create the vtk.js object graph and `render()` drive it.
* Remove the direct-DOM path: make the non-IPython branch raise an explicit, informative error.
* Keep the path but document it as experimental and guard `render()` so it degrades gracefully instead of crashing.

## Decision Outcome

Chosen option: "Implement the direct-DOM path", because Pyodide without IPython is a supported target, and a correctly implemented path is the only option that both removes the guaranteed crash and gives that environment real rendering. The implementation must create the vtk.js renderer and render window inside the container `create_container()` builds, so `render()` drives actual objects instead of attributes that do not exist, and the `# type: ignore[attr-defined]` comments are removed or justified by generated attributes.

### Consequences

* Good, because it removes the guaranteed `AttributeError` defect, and the `type: ignore[attr-defined]` markers that mask it can be deleted.
* Good, because Pyodide without IPython stays a supported use case with real rendering instead of a crash.
* Good, because the direct-DOM branch becomes reachable and testable by tests that exercise the real lifecycle rather than injected stand-ins.
* Neutral, because a second vtk.js object wiring path now exists alongside the generated-JavaScript IPython path, and the two must be kept in sync.

### Confirmation

Confirmed by tests that exercise the actual direct-DOM lifecycle without injected attributes: a unit test that calls `create_container()` and `render()` in Pyodide without IPython and without preset `renderer`/`render_window` attributes (note that `tests/test_rendering.py::test_render_loads_vtkjs_in_pyodide` cannot serve as this check because it injects stand-ins for both attributes, so it passes with the defect still present), plus a browser test that renders a mesh in Pyodide without IPython, analogous to the existing Playwright tests. The ADR status moves from `proposed` to `accepted` or `rejected` after discussion in the PR that carries this record.

## Pros and Cons of the Options

## Pros and Cons of the Options

### Implement the direct-DOM path (proposed)

At `create_container()` time, construct the vtk.js object graph for the container; `render()` then calls `resetCamera()` and `render_window.render()` on real objects.

* Good, because it removes the guaranteed `AttributeError` defect, and the `type: ignore[attr-defined]` markers that mask it can be deleted.
* Good, because Pyodide without IPython stays a supported use case with real rendering instead of a crash.
* Good, because the direct-DOM branch becomes reachable and testable by tests that exercise the real lifecycle rather than injected stand-ins.
* Neutral, because a second vtk.js object wiring path now exists alongside the generated-JavaScript IPython path, and the two must be kept in sync.

### Remove the direct-DOM path

Raise an explicit `RuntimeError` with guidance (for example, "install or initialize IPython, or use `generate_standalone_html()`") when not in IPython.

* Good, because it replaces the `AttributeError` with a loud, intentional error and removes the masked dead path and its `type: ignore` comments.
* Bad, because Pyodide-without-IPython becomes a permanently unsupported configuration, with `VTKJSRenderer` degrading to IPython-only despite accepting that environment.
* Neutral, because the exposed failure is deterministic and easy to test, and the Playwright surface neither shrinks nor grows.
* Good, because it is the smallest change, with no duplicated vtk.js wiring to maintain.

### Keep the path but document it as experimental

Keep the path untouched but catch `AttributeError` and warn.

* Bad, because the masked defect and the `type: ignore[attr-defined]` comments stay, and a caught `AttributeError` turns the crash into a silent no-op, which is worse than a clear error.
* Bad, because in Pyodide without IPython the scene still does not render, so the supported use case gets no visualization.
* Good, because the guarded branch becomes deterministic and testable, and a no-IPython test needs no stand-ins for `renderer` or `render_window`.
* Good, because the implementation work is near zero: no vtk.js wiring is created.

## More Information

* Issue: [tkoyama010/pyvista-js#778](https://github.com/tkoyama010/pyvista-js/issues/778)
* Coverage PR that surfaced it: [tkoyama010/pyvista-js#776](https://github.com/tkoyama010/pyvista-js/pull/776)
* Affected code: `src/pyvista_js/rendering.py`, `VTKJSRenderer.create_container` and `VTKJSRenderer.render`
* ADR-0001 for the related rendering-backend decision, ADR-0000 for the record format used here.
