# Symphony POC Architecture

This POC proves the Linear -> Symphony -> isolated workspace -> Codex loop. It
does not implement cross-issue dependency orchestration.

## Current Boundary

```text
Linear issue
  -> Symphony scheduler and tracker adapter
  -> one workspace per issue under workspaces/
  -> Codex app-server in that workspace
  -> Git changes and validation
```

The Symphony Dev Container is the outer execution boundary. Codex uses the
`externalSandbox` turn policy, so it does not create a nested Bubblewrap
sandbox. The container must not contain unrelated secrets or mounts.

## POC-1 Proven Path

The disposable `LMN-6` smoke run validated this sequence in container
`f0930478fc0543d35fd9afc136206abcc1ed315daad93d764f39ae4b0f102cd7`:

```text
Linear LMN-6 (Todo)
  -> one Symphony worker
  -> /workspace/symphony-poc/workspaces/LMN-6
  -> shallow clone of the configured repository
  -> Codex 0.153.0 app-server
  -> one completed turn and shell/file tool execution
  -> symphony-smoke.txt validated
  -> LMN-6 moved to Done
```

The smoke workflow uses `max_concurrent_agents: 1`, `max_turns: 1`, a
300-second workspace-hook timeout, and bounded Codex turn/stall timeouts. The
issue must reach a configured terminal state after the turn; otherwise
Symphony correctly schedules a continuation for an active issue, even when
`max_turns` is one. Once Linear reports a terminal state, Symphony removes the
associated issue workspace during normal cleanup.

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
