# Engineering POC Design

## Application

The sample application is a tiny task board. A user enters a task title and
adds it to a list. The business rule is that a task title must contain
between three and five non-whitespace characters, inclusive. The backend owns the rule and returns
HTTP 400 for invalid input; the UI displays the server validation message and
only adds successful tasks to the list.

The backend is FastAPI with an in-memory store. The frontend is a small React
application built with Vite. Playwright drives the UI against the real
backend/frontend containers.

## MCP Tools

The companion `engineering-mcp` server uses the current Python MCP SDK
`MCPServer` API and exposes exactly four tools:

| Tool | Input | Output |
| --- | --- | --- |
| `app_status` | `{}` | Structured service health, URLs, and latest result metadata |
| `app_run` | `{"mode": "start" \| "restart"}` | Structured lifecycle result and service URLs |
| `app_test` | `{}` | Structured backend test result: command, exit code, passed, output summary |
| `app_ui_verify` | `{}` | Structured Playwright result: command, exit code, passed, output summary |

These tools run fixed, repository-local operations only. MCP does not expose
file editing, arbitrary shell commands, arbitrary test selection, or generic
browser automation. Codex remains responsible for inspecting and editing code,
reasoning about changes, choosing what to change, and interpreting failures.

## Container Boundaries

- `backend`: FastAPI application, Python 3.12.
- `frontend`: Vite production preview, Node 22.
- `mcp`: Python 3.12 stdio MCP server. It has the Docker CLI and a read-only
  project mount so its fixed operations can control the Compose services.
- `ui-tests`: Playwright test runner, created ephemerally by `app_ui_verify`.

The MCP container requires the Docker socket only for this local POC so it can
start/restart the named application services and create the fixed test
container. The socket is not exposed as an MCP capability.

## Execution Flow

1. Codex reads and edits the backend or frontend using native workspace tools.
2. Codex calls `app_run({"mode": "start"})` or restart after application changes.
3. Codex calls `app_test({})`; MCP runs the canonical backend pytest suite.
4. Codex calls `app_ui_verify({})`; MCP runs the canonical Playwright suite.
5. Codex uses the structured results and output to decide whether more code
   changes are needed, then repeats verification.

