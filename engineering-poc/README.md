# Engineering POC

This isolated POC experiments with an agentic software-engineering loop around
a small task-board application. Codex owns code inspection, edits, reasoning,
and failure interpretation. The product workspace owns only the app itself:
backend, frontend, tests, and the product dev container.

## Dev Container

Open `engineering-poc` in VS Code and choose **Dev Containers: Reopen in
Container**. The container uses Python 3.12, Node 22, and Playwright.
Project dependencies are installed by the dev-container `postCreateCommand`,
not on the host. It does not own the MCP runtime.

## Local App Checks

From inside the dev container:

```bash
docker compose build
docker compose up -d backend frontend
docker compose run --rm backend-tests
docker compose run --rm ui-tests
```

The application is available at `http://localhost:4173`.

## MCP Boundary

The MCP implementation now lives in the separate `mcp/engineering-mcp`
project. The product repo consumes only the approved MCP through Docker MCP
Gateway, not by editing the MCP source directly.

The current local-product compose stack only starts the product services:

```bash
docker compose build
docker compose up -d backend frontend
docker compose run --rm backend-tests
docker compose run --rm ui-tests
```

To develop the MCP itself, use the standalone `mcp/engineering-mcp`
workspace. That project is independently buildable, testable, and packaged.

The validated integration path is:

`Product Codex -> MCP_DOCKER -> Docker MCP Gateway -> Engineering MCP -> product application`

For this experiment, Codex is connected with:

```bash
docker mcp client connect codex --profile lmnas_engineering_lab --global
```

The product Codex must not connect directly to `http://localhost:3001/mcp`.
