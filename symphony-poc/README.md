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

## Dev Container

Open `symphony-poc` in VS Code and choose **Dev Containers: Reopen in Container**. The folder is
mounted at `/workspace/symphony-poc`.

Inside the container, run the official Symphony setup:

```bash
cd /workspace/symphony-poc/.symphony/elixir
mise install
mise exec -- mix setup
mise exec -- mix build
```

Verify the agent CLI with:

```bash
codex --version
codex app-server --help
```

### Codex workspace-write sandbox

Codex's Linux `workspace-write` sandbox uses Bubblewrap to create nested user, mount, and (when
required) network namespaces. Docker Desktop's default Docker seccomp profile blocks those namespace
creation calls for this unprivileged Dev Container, so the image installs Debian's `bubblewrap` package
and the Dev Container applies `.devcontainer/codex-bwrap-seccomp.json` automatically via
`--security-opt seccomp=${localWorkspaceFolder}/.devcontainer/codex-bwrap-seccomp.json`.

That profile is Docker/Moby v28.5.2's pinned default profile (upstream SHA-256
`01536f1d1df938ae611eba20d6349e0de7a99b6ecdee1549427a0b01b8301e28`) with only these additional
non-`CAP_SYS_ADMIN` permissions: `clone` for `CLONE_NEWUSER | CLONE_NEWNS`, `clone` for
`CLONE_NEWUSER | CLONE_NEWNS | CLONE_NEWPID | CLONE_NEWIPC | CLONE_NEWNET`, and `unshare` for
`CLONE_NEWUSER`. It does not enable
privileged mode, Docker socket access, extra capabilities, or `seccomp=unconfined`.

After **Dev Containers: Rebuild Container**, verify the runtime configuration with:

```bash
command -v bwrap
bwrap --version
unshare -Ur true; echo $?
bwrap --unshare-user --ro-bind / / true; echo $?
codex --version
codex app-server generate-json-schema --out /tmp/codex-schema.json
```

## Required inputs

You will need to provide values for:

- `LINEAR_API_KEY`
- `LINEAR_PROJECT_SLUG`
- `SOURCE_REPO_URL`
- `SYMPHONY_WORKSPACE_ROOT`
- `.env.local` is loaded automatically by the Dev Container at runtime

## Official execution model

The supported Symphony development path is:

1. The Symphony runtime runs inside this Dev Container.
2. Symphony polls Linear for issues in the configured project.
3. Symphony creates or reuses an isolated workspace per issue.
4. Symphony launches `codex app-server` inside that workspace.
5. Codex works the issue until the workflow-defined handoff state or completion.

## Local start shape

Once the environment is filled in, the intended command is:

```bash
cd /workspace/symphony-poc/.symphony/elixir
mise exec -- ./bin/symphony /workspace/symphony-poc/WORKFLOW.md
```

The Linear environment file is intentionally not loaded by the Dev Container automatically.
