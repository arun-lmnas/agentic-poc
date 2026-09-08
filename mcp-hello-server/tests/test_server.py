"""Integration tests for the hello MCP tool."""

import pytest
from mcp import Client

from hello_mcp.server import mcp


@pytest.mark.anyio
async def test_hello_tool() -> None:
    """The server should expose hello through the MCP protocol."""
    async with Client(mcp) as client:
        result = await client.call_tool("hello", {"name": "MCP"})

    assert result.structured_content == {"result": "Hello, MCP!"}
