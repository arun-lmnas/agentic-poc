"""A minimal MCP server that exposes a single hello tool over stdio."""

from mcp.server import MCPServer

mcp = MCPServer("hello-server")


@mcp.tool()
def hello(name: str = "world") -> str:
    """Return a friendly greeting."""
    return f"Hello, {name}!"


if __name__ == "__main__":
    mcp.run()
