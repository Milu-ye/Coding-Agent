import json
import time
from pathlib import Path

from anthropic import Anthropic

from configs import app_config


def summarize_history(client: Anthropic, messages):
    conversation = json.dumps(messages, default=str)[:80000]
    prompt = ("Summarize this coding-agent conversation so work can continue.\n"
              "Preserve: 1. current goal, 2. key findings/decisions, 3. files read/changed, "
              "4. remaining work, 5. user constraints.\nBe compact but concrete.\n\n" + conversation)
    response = client.messages.create(model=app_config.MODEL, messages=[{"role": "user", "content": prompt}],
                                      max_tokens=2000)
    return "\n".join(
        getattr(block, "text", "")
        for block in response.content
        if getattr(block, "type", None) == "text").strip() or "(empty summary)"

def write_transcript(messages, transcript_dir: str | Path):
    if isinstance(transcript_dir, str):
        transcript_dir = Path(transcript_dir)
    transcript_dir.mkdir(parents=True, exist_ok=True)
    path = transcript_dir / f"transcript_{int(time.time())}.jsonl"
    with path.open("w") as f:
        for msg in messages: f.write(json.dumps(msg, default=str) + "\n")
    return path

def compact_history_by_llm(client:Anthropic,messages:list,transcript_dir: Path | str):
    transcript_path = write_transcript(messages, transcript_dir)
    print(f"[transcript saved: {transcript_path}]")
    return summarize_history(client,messages)

def estimate_context(messages:list):
    return len(str(messages))