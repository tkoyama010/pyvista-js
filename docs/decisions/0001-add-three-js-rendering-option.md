---
status: proposed
date: 2026-09-26
decision-makers: [tkoyama010]
consulted: []
informed: []
---

# Add a three.js Rendering Option to Complement vtk.js

## Context and Problem Statement

pyvista-js renders in the browser through [vtk.js](https://vtk.org/), which is the JavaScript port of the VTK visualization pipeline. This choice gives pyvista-js a rendering path that is close to desktop VTK, which is what PyVista itself uses. However, vtk.js is a port of a subset of VTK, and not every VTK feature has been implemented there yet. Some VTK classes and rendering capabilities that desktop PyVista users rely on either do not exist in vtk.js or behave differently, so pyvista-js cannot offer them to users today. [three.js](https://threejs.org/) is a mature, widely deployed WebGL library with strong rendering quality, a large ecosystem, and capabilities that overlap with, but do not equal, vtk.js. Should pyvista-js add three.js as an optional rendering backend to complement the features that vtk.js has not yet implemented from VTK?

## Decision Drivers

* **VTK feature parity**: Users coming from desktop PyVista expect the VTK features they already use; vtk.js gaps directly limit pyvista-js.
* **Maintenance cost**: A second rendering backend means a second code path in `ts/renderer.ts`, double the testing surface, and tracking a second upstream project's releases.
* **Bundle size**: The browser client is loaded per session; shipping two rendering libraries increases download size unless backends are lazy-loaded.
* **Ecosystem risk**: vtk.js is the canonical JavaScript continuation of the VTK ecosystem, which keeps pyvista-js aligned with upstream VTK development.
* **User choice**: An optional backend lets users trade consistency with VTK for rendering features and quality that three.js offers.

## Considered Options

* Stay vtk.js-only and wait for upstream vtk.js to implement missing VTK features.
* Add three.js as an optional, opt-in rendering backend alongside vtk.js.
* Replace vtk.js with three.js entirely.

## Decision Outcome

Chosen option: "Add three.js as an optional, opt-in rendering backend alongside vtk.js" (proposed, not yet accepted), because it offers a path to rendering capabilities that vtk.js has not yet implemented from VTK, delivered by translating the PyVista scene into three.js, while preserving the vtk.js path that keeps pyvista-js aligned with desktop VTK semantics. Making three.js opt-in keeps the default behavior unchanged, and lazy-loading the backend keeps the extra bundle cost off users who do not need it.

### Consequences

* Good, because users get access to rendering capabilities beyond what vtk.js currently implements, delivered through per-feature scene translation work, instead of waiting on upstream.
* Good, because the default vtk.js path stays intact, so existing users and tests see no behavior change.
* Bad, because rendering-dependent code in `ts/renderer.ts` must be abstracted behind a backend interface, which is real refactoring work.
* Bad, because two backends must be tested against the same scene features, and drift between them is a permanent maintenance tax.
* Bad, because results (camera state, picking, screenshots) may differ subtly between backends unless conformance tests are written.

### Confirmation

Compliance is confirmed by review of the renderer abstraction and by a conformance test that renders the same scene features on both backends and compares outputs. The ADR status moves from `proposed` to `accepted` or `rejected` after discussion in the PR that carries this record.

## Pros and Cons of the Options

### Stay vtk.js-only

Keep the current single-backend architecture and file issues upstream for missing VTK features.

* Good, because there is no new code path, no bundle growth, and no second upstream to track.
* Good, because pyvista-js stays closest to desktop VTK semantics, which is the project's core promise.
* Bad, because pyvista-js cannot offer VTK features that vtk.js has not implemented, on a timeline pyvista-js does not control.

### Add three.js as an optional backend (proposed)

Implement a small renderer backend interface; vtk.js stays the default, three.js is opt-in and lazy-loaded.

* Good, because rendering capabilities that vtk.js currently lacks can be delivered through three.js translations, instead of users waiting on upstream vtk.js.
* Good, because opt-in plus lazy-loading keeps the default bundle and behavior unchanged.
* Neutral, because three.js does not implement the VTK pipeline, so the backend must translate PyVista scene descriptions rather than share vtk.js objects.
* Bad, because it doubles the testing surface and adds a second upstream dependency to track.

### Replace vtk.js with three.js entirely

Drop vtk.js and render everything through three.js.

* Good, because there is only one backend and three.js has a very large ecosystem and community.
* Bad, because three.js has no notion of the VTK pipeline, so VTK-specific semantics would have to be rebuilt and would drift from desktop VTK.
* Bad, because it discards working, tested vtk.js integration for no feature gain on the happy path.

## More Information

* [vtk.js](https://vtk.js.org/) and its [VTK feature coverage](https://kitware.github.io/vtk-js/docs/intro_vtk_as_js_library.html)
* [three.js](https://threejs.org/docs/)
* pyvista-js renderer implementation: `ts/renderer.ts`
* ADR-0000 for the record format used here.
