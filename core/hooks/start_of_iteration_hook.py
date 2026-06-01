import pathlib

from anthropic import Anthropic

from core.background_task import collect_background_results
from core.context import estimate_context, compact_history_by_llm
from core.tools import WriteTodo


def remind_todos(tool: WriteTodo):
    def func(messages: list):
        if tool.need_remind():
            messages.append(tool.remind_prompt())
    return func

def snip_compact(threshold:int,keep_tail:int,keep_head:int):
    def func(messages: list):
        if len(messages) <= threshold:
            return
        snipped = len(messages) - keep_head - keep_tail
        placeholder = {"role": "user",
                       "content": f"[snipped {snipped} messages from conversation middle]"}
        messages[:] = messages[:keep_head] + [placeholder] + messages[-keep_tail:]
    return func

def miro_compact(keep_tool:int , threshold:int ,tool_len_threshold:int):
    def collect_tool_results(messages):
        blocks = []
        for mi, msg in enumerate(messages):
            if msg.get("role") != "user" or not isinstance(msg.get("content"), list): continue
            for bi, block in enumerate(msg["content"]):
                if isinstance(block, dict) and block.get("type") == "tool_result":
                    blocks.append((mi, bi, block))
        return blocks

    def func(messages: list):
        blocks = collect_tool_results(messages)
        if len(blocks)  <= threshold:
            return
        for _ , _ , block in blocks[:-keep_tool]:
            if block.get("content","") > tool_len_threshold:
                block["content"] = "[Earlier tool result compacted. Re-run if needed.]"
    return func

def compact_history(client:Anthropic,threshold:int,transcript_dir:str | pathlib.Path):
    def func(messages:list):
        if estimate_context(messages) <= threshold:
            return
        summary = compact_history_by_llm(client,messages,transcript_dir)
        messages[:] = [{"role": "user", "content": f"[Compacted]\n\n{summary}"}]
    return func

def collect_bg_task(bg_ids:set[str]):
    def func(messages:list):
        notification = collect_background_results(bg_ids)
        content = []
        if notification:
            for t in notification:
                content.append({"type": "text", "text": t})
            print(f"  \033[32m[inject] {len(notification)} background "
                  f"notification(s)\033[0m")
            messages.append({"role": "user", "content": content})
    return func





