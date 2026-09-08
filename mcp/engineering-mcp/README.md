# Engineering MCP

This project owns the Engineering MCP implementation for LensCloud POC work.
It is intentionally separate from the product workspace so the MCP lifecycle
can be developed, tested, packaged, and approved independently.

## Contents

- MCP source: `src/engineering_mcp`
- MCP tests: `tests`
- MCP dev container: `.devcontainer`
- Production Dockerfile: `Dockerfile`
- Validation script: `scripts/validate_streamable_http.py`

## Development Loop

Use the MCP dev container for source changes and test execution:

```bash
pytest
ruff check .
```

Build the production runtime image independently:

```bash
docker build -t engineering-mcp:local .
```

Validate the image over Streamable HTTP:

```bash
python scripts/validate_streamable_http.py --url http://127.0.0.1:3001/mcp
```

## Runtime

The production image serves the MCP server over Streamable HTTP on port 3001.
The server is designed to run as a standalone runtime container and can be
exposed to Docker MCP Gateway as an approved local MCP capability.

The gateway mechanism to validate on this host is `docker mcp gateway run`.
The temporary experiment profile is `lmnas_engineering_lab`; the protected
`lmnas_mcp_lab` profile is unchanged.

The local image reference `docker://engineering-mcp:local` is not accepted by
this Toolkit because the image is not self-describing, and image profiles are
started as stdio servers. The supported local definition for this Streamable
HTTP runtime is `docker-mcp-remote.yaml`, which registers
`http://127.0.0.1:3001/mcp` as a remote server in the temporary profile.

```bash
docker mcp profile create --id lmnas_engineering_lab \
  --name lmnas_engineering_lab \
  --server file:///absolute/path/to/docker-mcp-remote.yaml
docker mcp gateway run --profile lmnas_engineering_lab \
  --transport streaming --port 8811 --static \
  --tools app_status,app_run,app_test,app_ui_verify
docker mcp client connect codex --profile lmnas_engineering_lab --global
```

Codex connects to the Toolkit's `MCP_DOCKER` stdio server. It does not connect
directly to port 3001.
