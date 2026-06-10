"""MCP client manager — discovers servers, connects, lists tools, invokes calls."""

from __future__ import annotations

import asyncio
import threading
from typing import Any

from mcp import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.sse import sse_client
from mcp.types import Tool as MCPTool

from configs.mcp_config import discover_mcp_servers


def _run_on_loop(loop: asyncio.AbstractEventLoop, coro):
    """Schedule *coro* on *loop* from any thread, block until done, return result."""
    future = asyncio.run_coroutine_threadsafe(coro, loop)
    return future.result()


class MCPServer:
    """Represents a connected MCP server with its tools."""

    def __init__(self, name: str, config: dict[str, Any]) -> None:
        self.name = name
        self.config = config
        self.tools: list[MCPTool] = []
        self._session: ClientSession | None = None
        self._transport_ctx = None  # held open for the lifetime of the connection
        self._session_ctx = None
        self._loop: asyncio.AbstractEventLoop | None = None
        self._thread: threading.Thread | None = None

    def connect(self) -> None:
        """Connect to the MCP server in a background event loop."""
        self._loop = asyncio.new_event_loop()
        ready = threading.Event()
        self._thread = threading.Thread(target=self._run_loop, args=(ready,), daemon=True)
        self._thread.start()
        ready.wait()
        _run_on_loop(self._loop, self._connect())

    def _run_loop(self, ready: threading.Event) -> None:
        asyncio.set_event_loop(self._loop)
        self._loop.call_soon(ready.set)
        self._loop.run_forever()

    async def _connect(self) -> None:
        transport = self.config.get("transport", "stdio")
        if transport == "sse":
            url = self.config["url"]
            self._transport_ctx = sse_client(url)
        else:
            cmd = self.config["command"]
            args = self.config.get("args", [])
            env = self.config.get("env")
            params = StdioServerParameters(command=cmd, args=args, env=env)
            self._transport_ctx = stdio_client(params)

        read, write = await self._transport_ctx.__aenter__()
        self._session_ctx = ClientSession(read, write)
        self._session = await self._session_ctx.__aenter__()
        await self._session.initialize()
        result = await self._session.list_tools()
        self.tools = list(result.tools)

    def call_tool(self, tool_name: str, arguments: dict[str, Any]) -> str:
        """Invoke a tool on this MCP server and return the result text."""
        return _run_on_loop(self._loop, self._call_tool(tool_name, arguments))

    async def _call_tool(self, tool_name: str, arguments: dict[str, Any]) -> str:
        result = await self._session.call_tool(name=tool_name, arguments=arguments)
        parts: list[str] = []
        for item in result.content:
            if hasattr(item, "text"):
                parts.append(item.text)
            else:
                parts.append(str(item))
        return "\n".join(parts)

    def disconnect(self) -> None:
        """Disconnect from the MCP server."""
        if self._loop is None:
            return

        async def _disconnect() -> None:
            if self._session_ctx:
                await self._session_ctx.__aexit__(None, None, None)
            if self._transport_ctx:
                await self._transport_ctx.__aexit__(None, None, None)

        try:
            _run_on_loop(self._loop, _disconnect())
        except Exception:
            pass
        finally:
            if self._loop:
                self._loop.call_soon_threadsafe(self._loop.stop)
            if self._thread:
                self._thread.join(timeout=2)
            self._loop = None
            self._thread = None


class MCPManager:
    """Manages MCP server discovery, connection, and tool listing."""

    def __init__(self) -> None:
        self._servers: dict[str, MCPServer] = {}
        self._connected = False

    def discover_and_connect(self) -> list[MCPTool]:
        """Discover MCP servers from config, connect, and return all tools."""
        server_configs = discover_mcp_servers()
        all_tools: list[MCPTool] = []

        for name, config in server_configs.items():
            try:
                server = MCPServer(name, config)
                server.connect()
                self._servers[name] = server
                all_tools.extend(server.tools)
                print(f"[MCP] Connected to '{name}' — {len(server.tools)} tools")
            except Exception as e:
                print(f"[MCP] Failed to connect to '{name}': {e}")

        self._connected = True
        return all_tools

    def get_tool_server(self, tool_name: str) -> MCPServer | None:
        """Find which server provides the given tool."""
        for server in self._servers.values():
            for tool in server.tools:
                if tool.name == tool_name:
                    return server
        return None

    def call_tool(self, tool_name: str, arguments: dict[str, Any]) -> str:
        """Invoke a tool by name, routing to the correct server."""
        server = self.get_tool_server(tool_name)
        if server is None:
            return f"Error: MCP tool '{tool_name}' not found on any server"
        return server.call_tool(tool_name, arguments)

    def shutdown(self) -> None:
        """Disconnect all MCP servers."""
        for name, server in self._servers.items():
            try:
                server.disconnect()
            except Exception as e:
                print(f"[MCP] Error disconnecting '{name}': {e}")
        self._servers.clear()
        self._connected = False
