---
tracker:
  kind: linear
  provider:
    api_key: $LINEAR_API_KEY
    # project_slug: $LINEAR_PROJECT_SLUG
    project_slug: "e751aaf12fc6"
  active_states:
    - Todo
    - In Progress
  terminal_states:
    - Closed
    - Cancelled
    - Canceled
    - Duplicate
    - Done
polling:
  interval_ms: 5000
workspace:
  root: $SYMPHONY_WORKSPACE_ROOT
hooks:
  timeout_ms: 300000
  after_create: |
    set -euo pipefail
    if [ -z "${SOURCE_REPO_URL:-}" ]; then
      echo "SOURCE_REPO_URL is required"
      exit 1
    fi
    git clone --depth 1 "$SOURCE_REPO_URL" .
    git config --global --add safe.directory "$PWD"
codex:
  command: "$CODEX_BIN --config shell_environment_policy.inherit=all app-server"
  approval_policy: never
  thread_sandbox: danger-full-access
  turn_sandbox_policy:
    type: externalSandbox
    networkAccess: enabled
  turn_timeout_ms: 180000
  stall_timeout_ms: 300000
agent:
  max_concurrent_agents: 1
  max_turns: 1
---

You are executing one deterministic Symphony smoke test for Linear issue `{{ issue.identifier }}`.

Work only in the supplied workspace. Follow the issue description exactly.
Create the requested file or change, verify it with a shell command, and stop.
Do not inspect unrelated files, make architectural changes, commit, push, or modify any other file.

Issue title: {{ issue.title }}

Issue description:
{% if issue.description %}{{ issue.description }}{% else %}No description provided.{% endif %}
