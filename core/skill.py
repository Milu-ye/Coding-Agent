import os
from pathlib import Path
from typing import TypedDict

from core.utils.parse_util import parse_frontmatter


class Skill(TypedDict):
    name: str
    description: str
    content: str

SKILL_REGISTRY: dict[str, Skill] = {}
SKILL_DIR = Path(__file__).parent.parent / "skills"



def scan_skills():
    if not SKILL_DIR.exists():
        return
    for d in sorted(SKILL_DIR.iterdir()):
        if not d.is_dir():
            continue
        manifest = d / "SKILL.md"
        if manifest.exists():
            raw = manifest.read_text()
            meta , body = parse_frontmatter(raw)
            name = meta.get("name", d.name)
            desc = meta.get("description", raw.split("\n")[0].lstrip("#").strip())
            SKILL_REGISTRY[name] = {"name": name, "description": desc, "content": body}

def list_skills():
    return "\n".join(f"- **{s['name']}**: {s['description']}" for s in SKILL_REGISTRY.values())

scan_skills()

# def build_system() -> str:
#     catalog = list_skills()
#     return (
#         f"You are a coding agent at {os.getcwd()}. "
#         f"Skills available:\n{catalog}\n"
#         "Use load_skill to get full details when needed."
#     )
#
# SYSTEM = build_system()