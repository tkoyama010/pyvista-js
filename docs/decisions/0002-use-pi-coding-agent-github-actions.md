---
status: proposed
date: 2026-11-03
decision-makers: [tkoyama010]
consulted: []
informed: []
---

# Use Pi Coding Agent GitHub Actions for Repository Automation

## Context and Problem Statement

Repository maintenance tasks — triaging issues, reviewing pull requests, and drafting fixes — currently happen only when a maintainer is available. The repository already carries its AI-facing guidance in [`AGENTS.md`](../../AGENTS.md), which every coding agent reads, but GitHub automation has no way to invoke that agent on demand. Should the repository run the [pi coding agent](https://github.com/badlogic/pi-mono) directly from GitHub Actions, triggered by comments on issues and pull requests?

## Decision Drivers

* **Reuse of AGENTS.md**: The agent harness reads `AGENTS.md`, skills, and extensions, so workflow contributions must follow the same conventions as human-written ones.
* **Security**: A comment-triggered agent can post content and write to branches; it must not run for arbitrary accounts or leak the LLM API key.
* **Runner cost**: Agent runs use hosted runners plus a paid LLM API key; unbounded triggers would be expensive.
* **Action pinning policy**: Project policy (SPEC 8) requires third-party GitHub Actions to be pinned to a commit SHA, which applies to any action added here.
* **Maintainer bandwidth**: Automation should reduce manual triage and review turn-around without requiring a new service or self-hosted infrastructure.

## Considered Options

* Do nothing; handle issues and reviews manually only.
* Use `shaftoe/pi-coding-agent-action` (pi-native GitHub Action) triggered by comments.
* Use a generic AI review bot (for example, an LLM-based reviewer app that does not load `AGENTS.md`).
* Self-host a dedicated agent service outside GitHub Actions.

## Decision Outcome

Chosen option: "Use `shaftoe/pi-coding-agent-action` (pi-native GitHub Action) triggered by comments" (proposed, not yet accepted), because it is the pi ecosystem's own action: it runs the pi CLI inside the workflow, so it loads `AGENTS.md`, skills, and extensions exactly like a local run, keeping repository guidance consistent between local and CI. It is comment-triggered (`/pi`), restricted to repository owners and organization members by default, needs no new infrastructure, and keeps the agent's token budget and cost visible in the workflow run log.

### Consequences

* Good, because issue and PR triage can start from a maintainer comment instead of the maintainer's keyboard.
* Good, because the same `AGENTS.md` and skill set govern local sessions and CI runs, so there is one source of agent guidance.
* Good, because the allowlist default (owners and organization members) plus the project's pinned-SHA policy keeps the attack surface small.
* Bad, because each triggered run consumes a hosted runner and a paid LLM API call; cost must be watched.
* Bad, because an agent posting on behalf of the repository can generate incorrect technical claims; posted output still needs human review before being trusted.
* Bad, because third-party action dependency adds supply-chain surface; version updates must be reviewed.

### Confirmation

Compliance is confirmed by review of any workflow file added under `.github/workflows/`: it must trigger only on comments (not on every push), restrict triggering actors to owners and organization members, pin the action to a commit SHA, and read the API token from a repository secret (never an inline value). The ADR status moves from `proposed` to `accepted` or `rejected` after discussion in the PR that carries this record.

## Pros and Cons of the Options

### Do nothing; handle issues and reviews manually only

No automation is added.

* Good, because there is no new dependency, cost, or security surface.
* Bad, because triage and review latency stays proportional to maintainer availability.

### Use `shaftoe/pi-coding-agent-action` (proposed)

Invoke the pi CLI through the pi-native GitHub Action via `/pi` comments on issues and pull requests.

* Good, because it loads `AGENTS.md`, skills, and extensions, matching local pi sessions exactly.
* Good, because it is comment-triggered and allowlisted by default to owners and organization members.
* Good, because it needs no infrastructure beyond hosted runners and one API-key secret.
* Neutral, because the action is maintained by a third party, not by pi core; its releases must be tracked.
* Bad, because it sits outside pi-mono, so it can drift from pi CLI changes between releases.

### Use a generic AI review bot

Install an LLM-based reviewer application from the GitHub Marketplace.

* Good, because setup is often a one-click app install.
* Bad, because such bots do not read `AGENTS.md` or the repository's skills, so their guidance diverges from what local agents follow.
* Bad, because behavior is opaque and not customizable to this repository's conventions.

### Self-host a dedicated agent service

Run a long-lived agent outside GitHub Actions and connect it via webhook.

* Good, because it could support richer triggers and persistence.
* Bad, because it requires running and monitoring a service, which is disproportionate to the current maintainer count.

## More Information

* [pi-mono](https://github.com/badlogic/pi-mono) (the pi coding agent) and the [pi ecosystem `awesome-pi-coding-agent` list](https://github.com/shaftoe/awesome-pi-coding-agent)
* [`shaftoe/pi-coding-agent-action`](https://github.com/shaftoe/pi-coding-agent-action)
* ADR-0000 for the record format used here.
