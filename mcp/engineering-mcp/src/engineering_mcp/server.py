"""Controlled application lifecycle and verification tools for the POC."""

import argparse
import os
import subprocess
import urllib.error
import urllib.request
from datetime import UTC, datetime
from typing import Literal

from mcp.server import MCPServer

mcp = MCPServer("engineering-mcp")
COMPOSE_FILE = os.environ.get(
    "ENGINEERING_POC_COMPOSE_FILE", "/workspace/engineering-poc/docker-compose.yml"
)
COMPOSE = ("docker", "compose", "-p", "engineering-poc", "-f", COMPOSE_FILE)
last_results: dict[str, dict] = {}


def _run(*args: str, timeout: int = 120) -> tuple[int, str]:
    result = subprocess.run(
        (*COMPOSE, *args), capture_output=True, text=True, timeout=timeout
    )
    output = (result.stdout + result.stderr).strip()
    return result.returncode, output[-4000:]


def _record(name: str, code: int, output: str, command: list[str]) -> dict:
    result = {
        "command": command,
        "exit_code": code,
        "passed": code == 0,
        "output": output,
        "completed_at": datetime.now(UTC).isoformat(),
    }
    last_results[name] = result
    return result


@mcp.tool()
def app_status() -> dict:
    """Return service health and the latest controlled operation results."""
    services = {}
    for name, url in (("backend", "http://backend:8000/health"), ("frontend", "http://frontend/")):
        try:
            with urllib.request.urlopen(url, timeout=2) as response:
                services[name] = {"reachable": True, "status_code": response.status}
        except (urllib.error.URLError, TimeoutError, OSError) as error:
            services[name] = {"reachable": False, "error": str(error)}
    code, output = _run("ps", "--format", "json", "backend", "frontend")
    return {"services": services, "compose_exit_code": code, "compose_output": output, "last_results": last_results}


@mcp.tool()
def app_run(mode: Literal["start", "restart"] = "start") -> dict:
    """Start or restart only the named backend and frontend application services."""
    args = ("up", "-d", "--build", "backend", "frontend")
    if mode == "restart":
        stop_code, stop_output = _run("stop", "backend", "frontend")
        if stop_code:
            return _record("app_run", stop_code, stop_output, [*COMPOSE, "stop", "backend", "frontend"])
    code, output = _run(*args, timeout=300)
    return _record("app_run", code, output, [*COMPOSE, *args])


@mcp.tool()
def app_test() -> dict:
    """Run the canonical backend unit-test suite in its fixed test service."""
    args = ("run", "--rm", "backend-tests")
    code, output = _run(*args, timeout=300)
    return _record("app_test", code, output, [*COMPOSE, *args])


@mcp.tool()
def app_ui_verify() -> dict:
    """Run the canonical Playwright browser verification in its fixed test service."""
    reset_code, reset_output = _run(
        "up", "-d", "--force-recreate", "backend", "frontend", timeout=300
    )
    if reset_code:
        return _record(
            "app_ui_verify",
            reset_code,
            reset_output,
            [*COMPOSE, "up", "-d", "--force-recreate", "backend", "frontend"],
        )
    args = ("run", "--rm", "ui-tests")
    code, output = _run(*args, timeout=300)
    return _record(
        "app_ui_verify", code, f"reset:\n{reset_output}\n\n{output}", [*COMPOSE, *args]
    )


def main() -> None:
    """Run the shared server definition over the selected MCP transport."""
    parser = argparse.ArgumentParser(description="Run the engineering MCP server")
    parser.add_argument(
        "--transport",
        choices=("stdio", "streamable-http"),
        default="stdio",
        help="MCP transport to serve (default: stdio)",
    )
    parser.add_argument("--host", default="0.0.0.0", help="HTTP bind host")
    parser.add_argument("--port", type=int, default=3001, help="HTTP bind port")
    args = parser.parse_args()

    if args.transport == "stdio":
        mcp.run()
        return

    mcp.run(transport="streamable-http", host=args.host, port=args.port)


if __name__ == "__main__":
    main()
