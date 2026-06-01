import json
import time
from typing import Any

from anthropic import Anthropic

from core.context import write_transcript, summarize_history, compact_history_by_llm
from core.tools.base import Tool





class CompactHistory(Tool):
    def __init__(self,client:Anthropic,messages:list,transcript_dir):
        self.__client = client
        self.__messages = messages
        self.__transcript_dir = transcript_dir

    @property
    def schema(self) -> dict[str, Any]:
        return {
            "name": "compact_history",
            "description": "Compress the conversation history by summarizing it. Saves the full transcript to disk and returns a condensed summary so work can continue without losing context. Preserves current goal, key findings, files touched, remaining work, and user constraints.",
            "input_schema": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        }

    def invoke(self):
        summary = compact_history_by_llm(self.__client, self.__messages, self.__transcript_dir)
        self.__messages[:] = [{"role": "user", "content": f"[Compacted]\n\n{summary}"}]
        return "[Compacted. Conversation history has been summarized.]"