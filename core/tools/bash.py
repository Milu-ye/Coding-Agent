import os
import pathlib
import subprocess
from core.tools.base import Tool
from core.tools.utils import ask_user, Decision


class Bash(Tool):

    def __init__(self,workdir:str = os.getcwd()):
        self.workdir = pathlib.Path(workdir)

    @property
    def schema(self) -> dict:
        return {
            "name": "bash",
            "description": "Run a shell command in the workspace. Output is truncated at 50000 chars. Commands time out after 120s. Dangerous commands (rm -rf /, sudo, shutdown, reboot, kill) are blocked.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The shell command to execute (bash syntax).",
                    },
                    "path": {
                        "type": "string",
                        "description": "Optional working directory for the command. Defaults to the workspace root.",
                    },
                },
                "required": ["command"],
            },
        }

    def check_permission(self,command:str,path:str = None ) -> tuple[Decision,str]:
        if "rm -rf /" in command:
            return Decision.FORBIDDEN , "'rm -rf /' is a dangerous command."
        if path:
            path = (self.workdir / path).resolve()
            if not path.is_relative_to(self.workdir):
                return ask_user("Execute outside the workdir."), ""
        return Decision.ALLOW, ""





    def invoke(self,command:str, path:str = None):
        try:
            r = subprocess.run(command, shell=True, capture_output=True, cwd=path if path else self.workdir, text=True, timeout=120)
            out = (r.stdout + r.stderr).strip()
            return out[:50000] if out else ""
        except subprocess.TimeoutExpired:
            return "Error: Command timed out"
        except Exception as e:
            return f"Error: {e}"