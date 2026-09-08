---
tracker:
  kind: linear
  provider:
    api_key: $LINEAR_API_KEY
    project_slug: $LINEAR_PROJECT_SLUG
workspace:
  root: $SYMPHONY_WORKSPACE_ROOT
hooks:
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
---

You are working on a Linear issue `{{ issue.identifier }}`.

Issue title: {{ issue.title }}

Issue status: {{ issue.state }}

Issue URL: {{ issue.url }}

Issue description:
{% if issue.description %}
{{ issue.description }}
{% else %}
No description provided.
{% endif %}

Instructions:

1. Work only inside the provided workspace.
2. Make the smallest correct change that satisfies the issue.
3. Validate the result before stopping.
4. Leave a clear handoff note in the tracker if the workflow supports it.

