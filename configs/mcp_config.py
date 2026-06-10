"""MCP server discovery configuration.

Reads MCP server definitions from .mcp.json (project-local) or
~/.claude/mcp.json (global). Merges both with project taking precedence.
"""

from __future__ import annotations

import json
import os
import pathlib
from typing import Any


def _load_json(path: pathlib.Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def discover_mcp_servers() -> dict[str, dict[str, Any]]:
    """Discover MCP servers from configuration files.

    Merges global (~/.claude/mcp.json) and project-local (.mcp.json) configs.
    Project-local servers override global ones by name.
    """
    global_config = _load_json(pathlib.Path.home() / ".claude" / "mcp.json")
    project_config = _load_json(pathlib.Path(os.getcwd()) / ".mcp.json")

    global_servers: dict = global_config.get("mcpServers", {})
    project_servers: dict = project_config.get("mcpServers", {})

    merged = {**global_servers, **project_servers}
    return merged
