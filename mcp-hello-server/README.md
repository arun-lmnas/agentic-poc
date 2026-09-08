# Minimal Python MCP server

This project uses the MCP Python SDK 2.x `MCPServer` API and exposes one
`hello` tool over stdio.

## Development container

Open this directory in VS Code, then run **Dev Containers: Reopen in
Container**. The container uses Python 3.12 and installs the project with its
test and lint dependencies.

```bash
pytest
ruff check .
python -m hello_mcp.server
```

## Production image

Build from this directory:

```bash
docker build -t hello-mcp-server .
```

The container communicates over standard input/output, as required for a
stdio MCP server:

```bash
docker run --rm -i hello-mcp-server
```

Validate the production image as an MCP client would:

```bash
python tests/validate_container.py
```
