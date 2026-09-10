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
  turn_timeout_ms: 900000
  stall_timeout_ms: 300000
agent:
  max_concurrent_agents: 1
  max_turns: 10
---

You are the autonomous engineering worker for Linear issue `{{ issue.identifier }}`.

Work only inside the assigned issue workspace. Do not access another issue's
workspace, modify unrelated projects, or modify Symphony itself unless the
Linear issue explicitly requires it. Do not commit or push unless the issue
explicitly requires it.

Issue title: {{ issue.title }}

Issue status: {{ issue.state }}

Issue URL: {{ issue.url }}

Issue description:
{% if issue.description %}{{ issue.description }}{% else %}No description provided.{% endif %}

Workflow:

1. Understand the issue and its acceptance criteria.
2. Inspect the relevant files in this workspace and determine the smallest
   correct change.
3. Implement the change. Keep scope tightly limited to the issue.
4. Run the relevant automated tests.
5. Inspect the result and fix failures when reasonably possible, then rerun
   the relevant checks.
6. Verify the final state against the issue before declaring success.
7. Only after successful verification, transition the Linear issue to Done.

Do not claim completion without verification. If you are blocked, report the
blocker clearly in the tracker and leave the issue unfinished rather than
pretending it is complete. Continue working through the required steps; do not
artificially limit yourself to a single turn.
