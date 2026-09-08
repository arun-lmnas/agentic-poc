"""Integration tests for the engineering MCP tools."""

import pytest
from mcp import Client

from engineering_mcp.server import mcp


@pytest.mark.anyio
async def test_engineering_tools_exposed() -> None:
    async with Client(mcp) as client:
        tools = await client.list_tools()
        tool_names = sorted(tool.name for tool in tools.tools)

    assert tool_names == [
        "app_run",
        "app_status",
        "app_test",
        "app_ui_verify",
    ]
