"""MCP tool wrapper — adapts MCP tools to the project's Tool interface."""

from __future__ import annotations

from typing import Any

from mcp.types import Tool as MCPTool

from core.mcp.manager import MCPManager
from core.tools.base import Tool
from core.tools.decision import Decision


class MCPToolWrapper(Tool):
    """Wraps an MCP tool so the agent can discover and use it."""

    def __init__(self, mcp_tool: MCPTool, manager: MCPManager) -> None:
        self._mcp_tool = mcp_tool
        self._manager = manager

    @property
    def schema(self) -> dict[str, Any]:
        return {
            "name": f"mcp__{self._mcp_tool.name}",
            "description": f"[MCP] {self._mcp_tool.description or self._mcp_tool.name}",
            "input_schema": self._mcp_tool.inputSchema,
        }

    def invoke(self, **kwargs: Any) -> str:
        return self._manager.call_tool(self._mcp_tool.name, kwargs)

    def check_permission(self, **kwargs: Any) -> tuple[Decision, str]:
        return Decision.ALLOW, ""
