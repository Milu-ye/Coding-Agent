import os
import pathlib

from .base import Tool
from .decision import Decision
from .utils import safe_path, ask_user


class Write( Tool):

    def __init__(self,workdir:str = os.getcwd()):
        self.workdir = pathlib.Path(workdir)

    @property
    def schema(self) -> dict:
        return {
            "name": "write",
            "description": "Write or overwrite a file with new content. Creates parent directories automatically. Paths outside the workspace are blocked.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Relative or absolute path to the target file within the workspace.",
                    },
                    "content": {
                        "type": "string",
                        "description": "The exact text content to write to the file.",
                    },
                },
                "required": ["path", "content"],
            },
        }

    def check_permission(self,path: str,**kwargs):
        if path:
            path = (self.workdir / path).resolve()
            if not path.is_relative_to(self.workdir):
                return ask_user("Write file outside the workdir."), ""
        return Decision.ALLOW, ""

    def invoke(self,path: str,content: str):
        try:
            file_path = (self.workdir / path).resolve()
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content)
            return f"Wrote {len(content)} bytes to {path}"
        except Exception as e:
            return f"Error: {e}"
