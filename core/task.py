from dataclasses import dataclass


@dataclass
class Task:
    id: str
    subject:str
    description: str
    status: str
    owner: str
    blocked_by: list[str]


