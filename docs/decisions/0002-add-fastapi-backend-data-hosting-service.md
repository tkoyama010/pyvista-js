---
status: proposed
date: 2026-09-27
decision-makers: [tkoyama010]
consulted: []
informed: []
---

# Add a FastAPI Backend Data Hosting Service

## Context and Problem Statement

pyvista-js is a client-side library: the browser (or Pyodide/stlite runtime) renders meshes directly and needs no server. Example data is downloaded at runtime from static URLs — `https://raw.githubusercontent.com/pyvista/vtk-data/master/Data` and the Khronos glTF sample repository (`src/pyvista_js/examples.py`). A proposal has been made to add a [FastAPI](https://fastapi.tiangolo.com/) backend server to pyvista-js that hosts mesh data, motivated in part by a desire to learn FastAPI and AWS. Should pyvista-js gain a FastAPI backend that serves (and possibly accepts uploads of) mesh data, or should the project remain backend-free?

## Decision Drivers

* **Project scope**: pyvista-js is a client-side visualization library with zero server-side runtime today; every backend adds deployment, uptime, and security obligations that a pip-installed library does not carry.
* **Current data path works**: Example data is served from static URLs that require no infrastructure owned by this project, and the browser fetches them directly with no CORS-visible intermediary.
* **Upstream fragility**: The `raw.githubusercontent.com` dependency is outside this project's control; the `master` branch paths can move or be rate-limited, so a failure mode exists for the current approach.
* **Static-vs-dynamic serving**: Hosting data is a static-file problem; a read-only file server is exactly what object storage plus a CDN does, so a general-purpose web framework may be the wrong tool for the serving half of the job.
* **Upload and metadata needs**: Serving *contributed* data (upload, listing, auth, quotas) is a genuinely dynamic problem that static hosting cannot cover — but no such requirement exists in the project today.
* **Learning goals**: FastAPI + AWS hands-on experience is a legitimate goal, but it is a personal driver, not an architectural need of the library.

## Considered Options

* Keep the status quo: static URLs on `raw.githubusercontent.com`, no backend.
* Move example data to static hosting this project controls (S3 + CloudFront), still no backend.
* Add a FastAPI backend service on AWS (e.g., App Runner/ECS + S3) with upload/list/download endpoints.

## Decision Outcome

Chosen option: "Keep the status quo: static URLs, no backend" (proposed, not yet accepted), because pyvista-js has no dynamic data requirement today, static file serving needs no application server, and adding a backend would couple a client-side library to server infrastructure it must then operate. The FastAPI + AWS learning goal is real and worth pursuing, but as a **separate repository** that could serve as an alternative mirror for `pyvista/vtk-data`; it does not need to live inside this library.

### Consequences

* Good, because the library keeps its zero-infrastructure deployment story: `pip install pyvista-js` still works with no server to run, pay for, or secure.
* Good, because the learning goal is still met — a separate FastAPI/AWS project can exercise the same data-hosting design without imposing operational burden on pyvista-js users or maintainers.
* Bad, because the dependency on `raw.githubusercontent.com` remains outside this project's control and can break example downloads without notice.
* Bad, because if upload/metadata features are ever wanted, this decision must be revisited (see Confirmation).

### Confirmation

The decision holds as long as `src/pyvista_js/examples.py` continues to fetch from static URLs and no upload or authenticated-data feature appears in the issue tracker. If a dynamic requirement (user uploads, dataset listings, access control) is accepted, this ADR is reopened and the FastAPI option below is re-evaluated with that requirement in hand. Status moves from `proposed` to `accepted` or `rejected` after discussion in the PR that carries this record.

## Pros and Cons of the Options

### Keep the status quo (static `raw.githubusercontent.com` URLs)

Example data stays where it is; pyvista-js ships no server-side component.

* Good, because there is no code to write, no service to deploy, and no cost to bear.
* Good, because the current path already serves the browser directly and needs no CORS configuration on this project's side.
* Bad, because availability and layout are controlled by the upstream `pyvista/vtk-data` and Khronos repositories, not by this project.

### Move example data to S3 + CloudFront (static hosting, no backend)

Copy or mirror the needed datasets into an S3 bucket fronted by CloudFront; point `_PYVISTA_DATA_BASE` at it.

* Good, because it removes the upstream fragility while keeping the architecture backend-free.
* Good, because it is the natural first AWS step (S3, CloudFront, Terraform) and needs no application code.
* Bad, because it introduces data-sync work: the mirror must be updated when upstream data changes.
* Bad, because it adds a small ongoing AWS cost and an infrastructure-as-code surface (the repository already manages GitHub settings with Terraform in `terraform/`, so the pattern exists, but AWS is new scope).

### Add a FastAPI backend service on AWS

Run FastAPI (on App Runner, ECS Fargate, or Lambda) with endpoints such as `GET /datasets/{name}` and `POST /datasets`, backed by S3 for object storage, deployed via Terraform or CDK.

* Good, because it is an excellent, well-bounded FastAPI + AWS learning project: real file streaming, S3 integration, IAM, deployments.
* Good, because it could later support uploads, dataset metadata, and access control that static hosting cannot express.
* Bad, because none of those dynamic requirements exist in pyvista-js today; the backend would serve files a CDN serves better and cheaper.
* Bad, because a service attached to an OSS library inherits its users: uptime, abuse control (rate limiting, upload quotas), and security response become maintainer obligations.
* Bad, because it conflicts with the project's client-side simplicity: Pyodide/stlite users would still fetch over HTTP, gaining nothing from the server being FastAPI rather than object storage.

## More Information

* Current data fetching: `src/pyvista_js/examples.py` (`_PYVISTA_DATA_BASE`, `_GLTF_SAMPLE_BASE`, `_download_url`)
* [pyvista/vtk-data](https://github.com/pyvista/vtk-data) — the upstream data repository
* [FastAPI](https://fastapi.tiangolo.com/), [Amazon S3](https://aws.amazon.com/s3/), [Amazon CloudFront](https://aws.amazon.com/cloudfront/)
* ADR-0001 for the record format and the "(proposed, not yet accepted)" convention used here.
