---
status: accepted
date: 2026-03-20
decision-makers: [tkoyama010]
consulted: []
informed: []
---

# Adopt SPEC 6 — Keys to the Castle

## Context and Problem Statement

The project engages with restricted resources: PyPI package publishing, translation
management, documentation hosting, and repository administration. [Scientific Python
SPEC 6 — Keys to the Castle](https://scientific-python.org/specs/spec-0006/) requires
projects to document these restricted resources, grant the lowest privileges needed,
keep at least two maintainers able to access project assets, and use a secrets
distribution system with defined properties. Should pyvista-js adopt SPEC 6?

## Decision Drivers

* **Release integrity**: PyPI publishing credentials are the highest-value asset; a
  takeover would allow distributing malicious packages to users.
* **Bus factor**: With a single maintainer, losing access to one account could lock
  the project out of its own assets.
* **Existing good practice**: The project already uses OIDC trusted publishing,
  build provenance attestations, and SHA-pinned GitHub Actions (SPEC 8), so few
  shared long-lived secrets exist.
* **Ecosystem alignment**: Endorsed SPECs signal trustworthiness to users and
  downstream packagers.

## Considered Options

* Adopt SPEC 6 and document resources and access control.
* Do not adopt; keep access undocumented.

## Decision Outcome

Chosen option: "Adopt SPEC 6 and document resources and access control", because the
project already satisfies most of the SPEC's principles through secret-free
workflows, and the remaining work is documentation that reduces operational risk.

### Restricted Resources Inventory

| Resource | Purpose | Who has access | How to gain access |
| --- | --- | --- | --- |
| GitHub repository (`tkoyama010/pyvista-js`) | Source code, CI/CD, releases | Owner: `tkoyama010` | Contact the owner; collaborators are added with the lowest workable role |
| PyPI package (`pyvista-js`) | Package publishing | PyPI project owner; publishing is via GitHub OIDC trusted publishing (environment `pypi`), so no PyPI token is stored | Trusted publishers are managed by the owner in the PyPI project settings |
| Transifex project (`tkoyama010/pyvista-js`) | Translations | Owner; CI uses the `transifex` environment secrets | Request via a GitHub issue; reviewers/proofreaders are invited with translator-level permissions |
| Read the Docs project (`pyvista-js`) | Documentation hosting | Owner | Contact the owner |

### Secrets Handling

* The project avoids shared secrets wherever possible: PyPI publishing uses OIDC
  trusted publishing (no PyPI token), and CI authenticates through GitHub
  environment-scoped secrets with minimal permissions (`permissions: {}` by default
  in workflows).
* Remaining secrets (Transifex API token, codecov token) live in encrypted GitHub
  Actions environment secrets: centrally stored, grantable per environment, and
  revocable by removing the secret. This satisfies the SPEC's properties without a
  separate password manager.
* If a secret must ever be shared between maintainers, prefer granting service-level
  permission over sharing a credential; if sharing is unavoidable, use a hosted
  password manager (for example Bitwarden, which offers a non-profit discount) with
  encrypted, revocable sharing.

### Other Security Recommendations

* **2FA**: The maintainer uses two-factor authentication on GitHub, PyPI, Transifex,
  and Read the Docs. All collaborators must do the same.
* **Least privilege**: Permissions are reviewed periodically (at least yearly) and
  scoped to the minimum needed.
* **Continuity**: The PyPI project, GitHub repository, and Transifex organization
  should be accessible by at least two maintainers as the team grows.

### Consequences

* Good, because documented access paths prevent lock-outs and speed up incident
  response.
* Good, because the secret-free publishing path (OIDC) already minimizes stored
  credentials.
* Bad, because the inventory must be kept up to date as services change; it is
  reviewed in the yearly permission review.

### Confirmation

Compliance is confirmed by reviewing this document against the repository settings,
PyPI trusted-publisher configuration, and CI workflow permissions during the yearly
permission review.

## Pros and Cons of the Options

### Adopt SPEC 6

Document resources and access control as above.

* Good, because it reduces operational and security risk with no runtime cost.
* Bad, because documentation requires maintenance.

### Do not adopt

Keep access undocumented.

* Good, because nothing needs writing.
* Bad, because a single-account compromise or a lost password could lock the project
  out of its own release infrastructure.

## More Information

* [SPEC 6 — Keys to the Castle](https://scientific-python.org/specs/spec-0006/)
* [PyPI trusted publishers](https://docs.pypi.org/trusted-publishers/using-a-publisher/)
* Release hardening (SPEC 8) is described in `pyproject.toml` and
  `.github/workflows/release-please.yml`.
