import os
import pathlib

from core.tools.base import Tool
from core.tools.decision import Decision
from core.tools.utils import safe_path, ask_user


class Read(Tool):
    """
    A tool for reading a file.
    """
    def __init__(self,workdir:str = os.getcwd()):
        self.workdir = pathlib.Path(workdir)

    @property
    def schema(self) -> dict:
        return {
            "name": "read",
            "description": "Read the contents of a file. Returns line-numbered text. Paths outside the workspace are blocked.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Relative or absolute path to the file within the workspace.",
                    },
                    "offset": {
                        "type": "integer",
                        "description": "Line number to start reading from (1-indexed).",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of lines to return.",
                    },
                },
                "required": ["path"],
            },
        }

    def check_permission(self,path:str , **kwargs):
        if path:
            path = (self.workdir / path).resolve()
            if not path.is_relative_to(self.workdir):
                return ask_user("Read file outside the workdir."), ""
        return Decision.ALLOW, ""


    def invoke(self, path: str, offset: int = 0, limit: int = None):
        from itertools import islice

        file_path = (self.workdir / path).resolve()
        try:
            with file_path.open(encoding="utf-8") as f:
                start = max(offset - 1, 0) if offset else 0
                stop = start + limit if limit is not None else None
                lines = list(islice(f, start, stop))
            return "".join(lines).rstrip("\n")
        except Exception as e:
            return f"Error: {e}"
