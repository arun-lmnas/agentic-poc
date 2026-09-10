# Symphony POC Architecture

POC-1b turns the proven Linear-to-Symphony loop into a reusable engineering
workflow. It does not implement cross-issue dependency orchestration.

```text
Host VS Code Codex (engineering/setup agent)
  -> Git repository
  -> Symphony devcontainer (outer isolation boundary)
  -> Symphony (orchestration/control plane)
  -> per-issue workspace (isolated working copy)
  -> Codex app-server (autonomous engineering worker)
  -> implementation, tests, verification, and Linear Done
```

## Boundaries and Responsibilities

- Host Codex configures and validates the repository. It does not run
  Symphony or perform the assigned Linear engineering task.
- Symphony polls Linear, creates and cleans up one workspace per issue, and
  invokes the worker.
- The Symphony devcontainer is the outer isolation boundary for automated
  workers. It has no Docker socket, privileged mode, or added capabilities.
- The disposable devcontainer mounts the local `symphony-poc-codex-auth` named
  volume at `/home/node/.codex`. It persists CLI authentication across image
  rebuilds and container recreation without placing credentials in the image,
  repository, or environment files.
- A per-issue workspace is the only working copy the worker may use. Issue
  workspaces are never shared.
- Codex app-server receives the issue and executes the reusable engineering
  workflow: inspect, implement, test, repair, verify, then mark the issue Done.
- MCP is a future controlled-capability layer; it is not a shared workspace or
  an artifact promotion mechanism in POC-1b.

Codex uses `thread_sandbox: danger-full-access` together with the explicit
`externalSandbox` turn policy. That policy delegates containment to the
devcontainer, so no nested Bubblewrap sandbox or custom Docker seccomp profile
is required. Network access is enabled for the worker's normal engineering
dependencies; the container boundary remains responsible for host isolation.

The workflow permits up to ten bounded turns, a 15-minute turn timeout, and a
five-minute stall timeout. A worker must validate the requested change before
moving the Linear issue to Done; otherwise it reports the blocker and leaves
the issue active.

The Codex adapter contains low-noise debug tracing for JSON-RPC lifecycle
metadata only: methods, request IDs, workspace/policy metadata, item types,
and token/terminal events. It does not log prompts, tool arguments, or
credentials.

## POC-2 Extension Seam

The future model should extend the issue model without merging workspaces:

```text
Feature
  -> Issue
       -> workspace
       -> tracker state
       -> dependencies
       -> outputs

Artifact
  -> producer issue
  -> artifact type
  -> immutable version/reference/digest
  -> validation status
  -> approval metadata
```

Recommended ownership:

- Linear remains the source of work, business relationships, and human-visible
  dependency intent.
- Symphony evaluates dependency readiness before dispatching an issue and
  records orchestration state for a run.
- The producer issue publishes a versioned, immutable artifact reference only
  after validation succeeds.
- A downstream issue consumes that explicit artifact reference, never `latest`.
- Git and the artifact registry are the handoff mechanisms; workspaces remain
  isolated and are never shared between MCP and product issues.

The future dependency gate belongs at Symphony dispatch eligibility, backed by
Linear relationships and an explicit artifact/approval record. It should be
implemented only after the artifact contract and source of truth are selected.

## Not Implemented

- Dependency scheduling or blocking
- Feature graphs
- MCP artifact publishing or promotion
- Automatic downstream issue activation
- Cross-issue workspace access
- Product/MCP integration orchestration

These are POC-2 design points, not POC-1 behavior.
