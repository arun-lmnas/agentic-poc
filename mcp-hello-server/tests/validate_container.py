"""Validate the production image through its stdio MCP transport."""

import anyio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main() -> None:
    server = StdioServerParameters(
        command="docker",
        args=["run", "--rm", "-i", "hello-mcp-server:local-test"],
    )

    async with stdio_client(server) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            tools = await session.list_tools()
            assert [tool.name for tool in tools.tools] == ["hello"]

            result = await session.call_tool("hello", {"name": "Docker MCP"})
            assert not result.is_error
            assert result.structured_content == {"result": "Hello, Docker MCP!"}

    print("Tools:", [tool.name for tool in tools.tools])
    print("hello result:", result.structured_content["result"])


if __name__ == "__main__":
    anyio.run(main)
