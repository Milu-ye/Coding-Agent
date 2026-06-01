import os
import pathlib

from anthropic import Anthropic

from configs import app_config
from core.hooks.before_llm_hook import remind_todos, snip_compact, miro_compact, compact_history
from core.react_agent import Agent, Event
from core.skill import list_skills, SKILL_REGISTRY
from core.tools import Bash, Edit, Read, Glob, Write, WriteTodo
from core.tools.load_skill import LoadSkill
from core.tools.task import Task

WORKDIR = pathlib.Path(os.getcwd())
SYSTEM = (
    f"""
    You are a coding agent at {WORKDIR.name}.
    
    you have following skills:
    {list_skills()}
    Use load_skill to get full details when needed.
    
    Before starting any multi-step task, use todo_write to plan your steps. "
    Update status as you go.
    """
)

SUB_SYSTEM = (
    f"You are a coding agent at {WORKDIR}. "
    "Complete the task you were given, then return a concise summary. "
    "Do not delegate further."
)
client = Anthropic(base_url=app_config.BASE_URL, api_key=app_config.API_KEY)



if __name__ == "__main__":
    print("s01: Agent Loop")
    print("输入问题，回车发送。输入 q 退出。\n")

    # 工具初始化
    bash = Bash()
    glob = Glob()
    read = Read()
    write = Write()
    edit = Edit()
    write_todo = WriteTodo(3)
    subagent = Agent(client=client,system_prompt=SUB_SYSTEM, tools=[bash, glob, read, write, edit],per_max_token=8000,transcript_dir=WORKDIR / "transcript",max_retry=3)
    task = Task(subagent)
    load_skill = LoadSkill(SKILL_REGISTRY)

    agent = Agent(client=client,system_prompt=SYSTEM, tools=[bash, glob, read, write, edit,write_todo,task,load_skill], per_max_token=8000,transcript_dir=WORKDIR / "transcript",max_retry=3)

    agent.register_hook(Event.START_OF_ITERATION,
                        snip_compact(100,40,5),
                        miro_compact(10,40,300),
                        compact_history(client,100,WORKDIR / "transcript"),
                        remind_todos(write_todo))

    history = []
    while True:
        try:
            query = input("\033[36ms01 >> \033[0m")
        except (EOFError, KeyboardInterrupt):
            break
        if query.strip().lower() in ("q", "exit", ""):
            break
        history.append({"role": "user", "content": query})
        agent.invoke(history)
        # Print the model's final text response
        response_content = history[-1]["content"]
        if isinstance(response_content, list):
            for block in response_content:
                if getattr(block, "type", None) == "text":
                    print(block.text)
        print()
