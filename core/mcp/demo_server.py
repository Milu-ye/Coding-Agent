"""Demo MCP server — provides a greeting tool for testing MCP discovery."""

import asyncio
import datetime

from mcp.server import Server, InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import ServerCapabilities, ToolsCapability, Tool


server = Server("demo")


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="greet",
            description="Greet someone by name",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "The name to greet"},
                },
                "required": ["name"],
            },
        ),
        Tool(
            name="get_time",
            description="Get the current server time",
            inputSchema={"type": "object", "properties": {}},
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list:
    if name == "greet":
        return [{"type": "text", "text": f"Hello, {arguments['name']}!"}]
    elif name == "get_time":
        return [{"type": "text", "text": f"Server time: {datetime.datetime.now()}"}]
    return [{"type": "text", "text": f"Unknown tool: {name}"}]


async def main():
    async with stdio_server() as (read, write):
        init_opts = InitializationOptions(
            server_name="demo",
            server_version="1.0.0",
            capabilities=ServerCapabilities(tools=ToolsCapability()),
        )
        await server.run(read, write, init_opts)


if __name__ == "__main__":
    asyncio.run(main())
