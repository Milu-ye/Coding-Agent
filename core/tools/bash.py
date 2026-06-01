import os
import pathlib
import subprocess

from core.background_task import start_background_task
from core.tools.base import Tool
from core.tools.utils import ask_user, Decision


class Bash(Tool):

    def __init__(self,workdir:str = os.getcwd()):
        self.workdir = pathlib.Path(workdir)
        self.bg_ids = set()

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
                    "run_in_background": {
                        "type": "boolean",
                        "description": "Set to true to run this command in the background. Use when the command is long-running and you don't need the result immediately.",
                    },
                    "path": {
                        "type": "string",
                        "description": "Optional working directory for the command. Defaults to the workspace root.",
                    },
                },
                "required": ["command"],
            },
        }

    def check_permission(self,command:str,path:str = None,**kwargs ) -> tuple[Decision,str]:
        if "rm -rf /" in command:
            return Decision.FORBIDDEN , "'rm -rf /' is a dangerous command."
        if path:
            path = (self.workdir / path).resolve()
            if not path.is_relative_to(self.workdir):
                return ask_user("Execute outside the workdir."), ""
        return Decision.ALLOW, ""





    def invoke(self,command:str,run_in_background:bool = False, path:str = None):
        try:
            if run_in_background:
                def _bg_run(cmd, cwd_path):
                    r = subprocess.run(cmd, shell=True, capture_output=True, cwd=cwd_path, text=True, timeout=600)
                    out = (r.stdout + r.stderr).strip()
                    return out if out else ""
                bg_id = start_background_task(_bg_run, cmd=command, cwd_path=path if path else self.workdir)
                self.bg_ids.add(bg_id)
                return f"[Background task {bg_id} started]" \
                       f"Command: {command}" \
                       f"Result will be available when complete." \

            r = subprocess.run(command, shell=True, capture_output=True, cwd=path if path else self.workdir, text=True, timeout=120)
            out = (r.stdout + r.stderr).strip()
            return out[:50000] if out else ""
        except subprocess.TimeoutExpired:
            return "Error: Command timed out"
        except Exception as e:
            return f"Error: {e}"

