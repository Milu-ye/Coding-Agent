import os
import pathlib
from typing import Any

from core.tools.base import Tool
from core.tools.decision import Decision


class Glob(Tool):

    def __init__(self, workdir: str = os.getcwd()):
        self.workdir = pathlib.Path(workdir)

    @property
    def schema(self) -> dict[str, Any]:
        return {
            "name": "glob",
            "description": "Find files matching a glob pattern. Returns newline-separated relative paths.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "Glob pattern to match (e.g. '**/*.py', 'src/**/*.ts'). Supports *, ?, [], ** wildcards.",
                    },
                },
                "required": ["pattern"],
            },
        }


    def invoke(self,pattern:str):
        import glob as g
        return "\n".join(g.glob(pattern, root_dir=self.workdir,recursive=True))