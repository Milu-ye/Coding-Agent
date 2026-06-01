import os
import pathlib
from enum import StrEnum
from typing import Callable

from anthropic import Anthropic
from anthropic.types import MessageParam

from configs import app_config
from .context import compact_history_by_llm
from .tools.base import Tool
from .tools.decision import Decision


workdir = pathlib.Path(os.getcwd())


TOOLS = []

class Event(StrEnum):
    BEFORE_QUERY = "before_query"
    START_OF_ITERATION = "before_agent"
    BEFORE_TOOL_USE = "before_tool_use"
    AFTER_TOOL_USE = "after_tool_use"
    END_OF_ITERATION = "after_agent"
    STOP = "stop"

class Agent:

    def __init__(self, client:Anthropic, system_prompt:str, tools:list[Tool], per_max_token:int, max_retry, transcript_dir: str | pathlib.Path):
        self.client = client
        self.system_prompt = system_prompt
        self.tools_schema = [tool.schema for tool in tools]
        self.tools: dict[str, Tool] = dict()
        for tool in tools:
            self.tools[tool.schema["name"]] = tool
        self.per_max_token = per_max_token
        self.max_retry = max_retry
        self.hooks = {
            Event.BEFORE_QUERY : [],
            Event.START_OF_ITERATION : [],
            Event.BEFORE_TOOL_USE : [],
            Event.AFTER_TOOL_USE : [],
            Event.END_OF_ITERATION: [],
            Event.STOP: [],
        }
        self.transcript_dir = transcript_dir

    def register_hook(self,event:Event,*hook:Callable):
        self.hooks[event].extend(hook)


    def trigger_hook(self,event:Event,**kwargs):

        match event:
            case Event.BEFORE_QUERY:
                for func in self.hooks[Event.BEFORE_QUERY]:
                    func(kwargs["query"])
            case Event.START_OF_ITERATION:
                for func in self.hooks[Event.START_OF_ITERATION]:
                    func(kwargs["messages"])
            case Event.BEFORE_TOOL_USE:
                for func in self.hooks[Event.BEFORE_TOOL_USE]:
                    func(kwargs["block"])
            case Event.AFTER_TOOL_USE:
                for func in self.hooks[Event.AFTER_TOOL_USE]:
                    func(kwargs["block"],kwargs["output"])
            case Event.STOP:
                for func in self.hooks[Event.STOP]:
                    func(kwargs["messages"])



    def invoke(self,messages:list,max_iterator:int = 10):
        self.trigger_hook(Event.BEFORE_QUERY,query=messages[-1])
        for _ in range(max_iterator):
            self.trigger_hook(Event.START_OF_ITERATION, messages=messages)
            reactive_retries = 0
            try:
                response = self.client.messages.create(
                    model=app_config.MODEL,
                    system=self.system_prompt,
                    tools=self.tools_schema,
                    messages=messages,
                    max_tokens=8000,
                )
                messages.append({"role": "assistant", "content": response.content})

            except Exception as e:
                if reactive_retries < self.max_retry:
                    if "prompt_too_long" in str(e).lower() or "too many tokens" in str(e).lower():
                        summary = compact_history_by_llm(self.client, messages, self.transcript_dir)
                        messages[:] = [{"role": "user", "content": f"[Compacted]\n\n{summary}"}]
                    reactive_retries += 1
                    continue
                raise

            if response.stop_reason != "tool_use":
                self.trigger_hook(Event.STOP,messages=messages)
                return

            results = []
            for block in response.content:
                if block.type == "tool_use":

                    print(f"\033[33m> {block.name} : {block.input}\033[0m")
                    tool = self.tools.get(block.name,None)
                    self.trigger_hook(Event.BEFORE_TOOL_USE,block=block)

                    if tool is None:
                        print(f"\033[31mError: Tool {block.name} not found\033[0m")
                        results.append(f"Error: Tool {block.name} not found")
                        continue


                    decision , reason = tool.check_permission(**block.input)

                    match decision:
                        case Decision.ALLOW:
                            output = tool.invoke(**block.input)
                            print("\n")
                            print(output)
                        case Decision.DENY:
                            output = "User deny to invoke tool"
                            print(f"[!] {output}")
                        case Decision.FORBIDDEN:
                            output = reason
                            print(f"[X] {reason}")
                        case _:
                            output = "Error: Unknown decision"

                    self.trigger_hook(Event.AFTER_TOOL_USE,block=block,output=output)


                    results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": output,
                    })
            messages.append({"role": "user", "content": results})
            self.trigger_hook(Event.END_OF_ITERATION,messages=messages)






