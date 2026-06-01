import os
import pathlib
from typing import Any

from core.tools.base import Tool
from core.tools.decision import Decision
from core.tools.utils import safe_path, ask_user


# 后期可以增强
class Edit(Tool):

    def __init__(self, workdir: str = os.getcwd()):
        self.workdir = pathlib.Path(workdir)

    @property
    def schema(self) -> dict[str, Any]:
        return {
            "name": "edit",
            "description": "Edit a file by finding an exact match of old_text and replacing its first occurrence with new_text. Paths outside the workspace are blocked.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Relative or absolute path to the target file within the workspace.",
                    },
                    "old_text": {
                        "type": "string",
                        "description": "Exact text substring to search for and replace. Must match exactly including whitespace and indentation. Only the first match is replaced.",
                    },
                    "new_text": {
                        "type": "string",
                        "description": "The replacement text. Use an empty string to delete old_text.",
                    },
                },
                "required": ["path", "old_text", "new_text"],
            },
        }

    def check_permission(self,path:str = None,**kwargs):
        if path:
            file_path = (self.workdir / path).resolve()
            if not file_path.is_relative_to(self.workdir):
                return ask_user("Execute outside the workdir."), ""
        return Decision.ALLOW, ""

    def invoke(self, path: str, old_text: str, new_text: str) -> str:
        try:
            file_path = safe_path(self.workdir, path)
            content = file_path.read_text(encoding="utf-8")
            if old_text not in content:
                return f"Error: old_text not found in {path}"
            new_content = content.replace(old_text, new_text, 1)
            file_path.write_text(new_content, encoding="utf-8")
            return f"Successfully edited {path}"
        except Exception as e:
            return f"Error: {e}"
