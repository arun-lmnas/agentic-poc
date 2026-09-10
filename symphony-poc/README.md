# Symphony POC

This directory holds the local Symphony setup for POC-1b: a reusable Linear
engineering workflow in an isolated devcontainer.

## What this POC uses

- Official Symphony execution model from `openai/symphony`
- Linear as the issue tracker
- Host VS Code Codex as the engineering/setup agent
- Symphony as the orchestration/control plane
- Codex app-server as the autonomous engineering worker
- Per-issue isolated workspaces under `symphony-poc/workspaces`
- MCP as a future controlled-capability layer (not POC-2 orchestration)

## Files

- `WORKFLOW.md`: Symphony workflow configuration and prompt
- `.env.example`: required host-side environment values
- `NOTES.md`: current assumptions and open inputs

## Dev Container

Open `symphony-poc` in VS Code and choose **Dev Containers: Reopen in Container**. The folder is
mounted at `/workspace/symphony-poc`.

The Dev Container automatically configures mise, runtime links, Git identity,
GitHub CLI Git integration, and Symphony dependencies/build.

### Outer sandbox model

The devcontainer is the worker's outer isolation boundary. `WORKFLOW.md`
configures Codex with an `externalSandbox` turn policy, so Codex does not need
to create a nested Bubblewrap sandbox. The image does not install Bubblewrap
and the devcontainer does not override Docker's default seccomp profile.

It does not use privileged mode, added capabilities, Docker-in-Docker, or a
Docker socket. The worker must not depend on the host VS Code Codex extension.

After **Dev Containers: Rebuild Container**, verify the runtime with:

```bash
codex --version
codex app-server --help
cd /workspace/symphony-poc/.symphony/elixir
mise exec -- mix build
```

## Required inputs

You will need to provide values for:

- `LINEAR_API_KEY`
- `LINEAR_PROJECT_SLUG`
- `SOURCE_REPO_URL`
- `SYMPHONY_WORKSPACE_ROOT`
- `.env.local` is loaded automatically by the Dev Container at runtime

### Persistent Codex authentication

The Dev Container mounts the local Docker named volume
`symphony-poc-codex-auth` at `/home/node/.codex`. Codex stores its cached CLI
credentials at `/home/node/.codex/auth.json`; the volume retains them across
container recreation and image rebuilds. The image creates only an empty,
node-owned directory at that path and never contains credentials.

The volume is local developer state: it is not in git, `.env.local`, or the
Docker image. It remains separate from GitHub authentication.

Docker reuses the stable image layers for the Node base image, Codex CLI, and
mise unless their Dockerfile inputs change. The local
`symphony-poc-mise-data` named volume retains the Erlang and Elixir toolchains,
avoiding a toolchain reinstall when the disposable container is recreated.
`post-create.sh` still validates the existing Symphony dependencies and builds
the executable, but it fetches dependencies only when `deps/` or `_build/` is
absent.

### GitHub CLI and Git authentication

Codex authentication is only for the Codex service; it does not authenticate
`git clone` or `git push` to GitHub. Issue workspaces are cloned from
`SOURCE_REPO_URL`, so a HTTPS clone creates `origin` in that issue workspace;
the Symphony control-plane directory is not itself that clone and need not
have an `origin` remote.

GitHub CLI is installed in the image at the pinned version declared in the
Dockerfile. The Dev Container mounts the local Docker named volume
`symphony-poc-gh-auth` at `/home/node/.config/gh`. It is separate from the
Codex volume and holds GitHub CLI authentication state only; no credential is
in the image, git, `.env.local`, or a host-wide home/SSH mount.

After rebuilding the Dev Container, the only manual setup action is GitHub
browser/device authentication. Complete organization SSO when GitHub requires
it:

```bash
gh auth login
```

The Dev Container automatically configures Git identity, safe directories, and
GitHub CLI credential integration. It runs `gh auth setup-git` automatically
when prior persisted GitHub CLI authentication exists; the image-level Git
helper makes Git usable immediately after a first `gh auth login`. You do not
need to run `git credential approve`, `git config`, `gh auth setup-git`, repair
runtime links, run mise setup, or build Symphony manually.

Then validate from a disposable issue-style clone, not from
`/workspace/symphony-poc`:

```bash
validation_dir="$(mktemp -d)"
git clone --depth 1 https://github.com/arun-lmnas/agentic-poc.git "$validation_dir"
git -C "$validation_dir" remote -v
git -C "$validation_dir" ls-remote origin
rm -rf "$validation_dir"
```

The GitHub CLI volume survives image rebuilds, container recreation, and
issue-workspace deletion. Deleting `symphony-poc-gh-auth` deliberately removes
the GitHub authentication state. Issue workspaces never receive a credential
copy; Git invokes `gh` when it needs an HTTPS credential.

## Official execution model

The supported Symphony development path is:

1. The Symphony runtime runs inside this Dev Container.
2. Symphony polls Linear for issues in the configured project.
3. Symphony creates or reuses an isolated workspace per issue.
4. Symphony launches `codex app-server` inside that workspace.
5. Codex understands the issue, implements the smallest correct change, runs
   relevant tests, verifies the final state, commits and pushes
   `symphony/<issue identifier>`, records concise evidence in Linear, and only
   then marks the issue Done.

Workspaces are deliberately ephemeral. The pushed issue branch and commit are
the durable engineering output; the Linear `Symphony Engineering Result`
comment records the branch, commit, change summary, validation, acceptance
verification, and limitations. If committing, pushing, or recording evidence
fails, the issue remains active and Symphony may clean up only after it reaches
a terminal state through some other deliberate action.

POC-2 remains a documented extension seam only. It does not yet provide a
dependency scheduler, feature graph, artifact registry or promotion, automatic
downstream activation, cross-issue workspace sharing, or MCP orchestration.

## Local start shape

Once the environment is filled in, the intended command is:

```bash
cd /workspace/symphony-poc/.symphony/elixir
mise exec -- ./bin/symphony /workspace/symphony-poc/WORKFLOW.md
```

The Linear environment file is intentionally not loaded by the Dev Container automatically.
