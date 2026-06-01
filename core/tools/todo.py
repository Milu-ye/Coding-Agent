from enum import StrEnum
from typing import TypedDict

from jinja2 import Template

from core.tools.base import Tool


class TodoStatus(StrEnum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

ICON_MAP = {
    TodoStatus.PENDING: "✽",
    TodoStatus.IN_PROGRESS: "▸",
    TodoStatus.COMPLETED: "✓",
}

REMIND_PROMPT = """
<reminder>
Following are todos:
{% for t in todos -%}
  [{{ t.status }}] {{ t.content }}
{% endfor -%}
Please update your todos.
</reminder>
"""

class Item(TypedDict):
    status: TodoStatus
    content: str

class WriteTodo(Tool):

    def __init__(self,remind_threshold: int = 3,todos:list[Item] = []):
        self.__todos = todos
        self.__rounds_since_todo = 0
        self.__remind_threshold = remind_threshold

    @property
    def todos(self):
        return self.__todos

    @property
    def schema(self) -> dict:
        return {"name": "todo_write", "description": "Create and manage a task list ",
                 "input_schema": {
                     "type": "object",
                     "properties": {
                         "todos": {
                             "type": "array",
                             "items": {
                                 "type": "object",
                                 "properties": {
                                     "content": {"type": "string"},
                                     "status": {"type": "string", "enum": ["pending", "in_progress", "completed"]},
                                 },
                             },
                         },
                     },
                 },
                }

    def clean_todos(self):
        self.__todos = []
        self.__rounds_since_todo = 0

    @property
    def rounds_since_todo(self):
        return self.__rounds_since_todo

    def need_remind(self):
        if self.__rounds_since_todo >= self.__remind_threshold:
            return True
        return False

    def remind_prompt(self):
        template = Template(REMIND_PROMPT)
        return template.render(todos=self.__todos)



    def invoke(self, todos: list[Item]) -> str:
        self.__todos = todos
        self.__rounds_since_todo = 0
        lines = ["\n## Current Tasks"]
        for t in self.__todos:
            icon = ICON_MAP[t["status"]]
            lines.append(f"  [{icon}] {t['content']}")
        print("\n".join(lines))
        return f"Updating todos succeed"



