"""Validate the production image through Streamable HTTP."""

import anyio

from mcp.client import Client


async def main() -> None:
    async with Client("http://127.0.0.1:3001/mcp") as client:
        tools = await client.list_tools()
        tool_names = sorted(tool.name for tool in tools.tools)
        assert tool_names == [
            "app_run",
            "app_status",
            "app_test",
            "app_ui_verify",
        ]

        result = await client.call_tool("app_status")
        assert not result.is_error

    print("Tools:", tool_names)
    print("app_status validated")


if __name__ == "__main__":
    anyio.run(main)
