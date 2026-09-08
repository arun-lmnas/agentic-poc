# Symphony POC

This directory holds the minimal local Symphony setup for the controlled POC.

## What this POC uses

- Official Symphony execution model from `openai/symphony`
- Linear as the issue tracker
- Codex as the coding agent via `codex app-server`
- Per-issue isolated workspaces under `symphony-poc/workspaces`

## Files

- `WORKFLOW.md`: Symphony workflow configuration and prompt
- `.env.example`: required host-side environment values
- `NOTES.md`: current assumptions and open inputs

## Required inputs

You will need to provide values for:

- `LINEAR_API_KEY`
- `LINEAR_PROJECT_SLUG`
- `SOURCE_REPO_URL`
- `SYMPHONY_WORKSPACE_ROOT`
- `CODEX_BIN` if you want to pin the host executable explicitly

## Official execution model

The supported Symphony path is:

1. Symphony runs on the host.
2. Symphony polls Linear for issues in the configured project.
3. Symphony creates or reuses an isolated workspace per issue.
4. Symphony launches `codex app-server` inside that workspace.
5. Codex works the issue until the workflow-defined handoff state or completion.

## Local start shape

Once the environment is filled in, the intended command is:

```bash
cd ~/aidev/lmnas-agentic-poc/symphony-poc
export $(grep -v '^#' .env | xargs)
./bin/symphony ./WORKFLOW.md
```

The actual binary location depends on which official Symphony build you choose to run.
At this stage I have only prepared the POC scaffolding, not the runtime itself.
