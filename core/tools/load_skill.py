from typing import Any

from core.skill import Skill
from core.tools.base import Tool


class LoadSkill( Tool):
    """Load a skill from the skills directory."""
    def __init__(self,skills:dict[str,Skill]):
        self.__skills = skills

    @property
    def schema(self) -> dict[str, Any]:
        return {
            "name": "load_skill",
            "description": "Load the full content of a skill by name.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "The name of the skill to load.",
                    },
                },
                "required": ["name"],
            },
        }

    def invoke(self,name:str) -> str:
        skill = self.__skills.get(name,None)
        if skill is None:
            return f"Skill {name} not found"
        return skill["content"]
