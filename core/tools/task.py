import os

from pyexpat.errors import messages

from core.react_agent import Agent
from core.tools.base import Tool
from core.utils.extract_util import extract_text

WORKDIR = os.getcwd()




class Task(Tool):
    """任务工具类"""
    def __init__(self,agent:Agent):
        self.__agent = agent

    @property
    def schema(self) -> dict:
        return {
            "name": "task",
            "description": "Launch a subagent to handle a complex subtask. Returns only the final conclusion.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "task": {
                        "type": "string",
                        "description": "The task to execute.",
                    },
                    "max_iterations": {
                        "type": "integer",
                        "description": "The maximum number of iterations to allow the subagent to run.",
                    },
                },
                "required": ["task"],
            },
        }



    def invoke(self,task: str,max_iterations: int = 10):
        messages = [{"role": "user", "content": task}]
        self.__agent.invoke(messages, max_iterations)
        return extract_text(messages[-1]["content"])


