# Notes

## Confirmed from the official Symphony repo

- Symphony is a long-running orchestrator that polls a tracker, creates an isolated workspace, and launches a coding agent session there.
- The current reference implementation is the Elixir app under `openai/symphony/elixir`.
- `WORKFLOW.md` is the repository-owned contract for tracker config, workspace root, hooks, agent settings, and the Codex command.
- Linear auth is supplied on the Symphony host through `LINEAR_API_KEY`.
- Codex is launched as `codex app-server` inside the issue workspace.
- The workspace root is configured in `WORKFLOW.md` and each issue gets its own directory under that root.

## Current local observation

- The machine already has a `codex` CLI exposed from the OpenAI VS Code extension bundle.
- The current workspace root is not yet a git repository.

## Open inputs needed to finish the live POC

- Linear personal API key
- Linear project slug for the test project
- Source repo URL to clone into each issue workspace
- Whether the POC should target the whole monorepo or a specific subproject path

