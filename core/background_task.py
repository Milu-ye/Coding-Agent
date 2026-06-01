import threading
import uuid
from typing import Callable

_bg_counter = 0
background_tasks: dict[str, dict] = {}   # bg_id → {tool_use_id, command, status}
background_results: dict[str, str] = {}   # bg_id → output
background_lock = threading.Lock()

def start_background_task(func: Callable, *args, **kwargs) -> str:
    """Run tool in a daemon thread. Returns background task ID."""
    global _bg_counter
    _bg_counter += 1
    bg_id = f"bg_{_bg_counter:04d}"
    def worker():
        result = func(*args, **kwargs)
        with background_lock:
            background_tasks[bg_id]["status"] = "completed"
            background_results[bg_id] = result

    with background_lock:
        background_tasks[bg_id] = {
            "param": kwargs,
            "status": "running",
        }
    thread = threading.Thread(target=worker, daemon=True)
    thread.start()
    return bg_id

# def is_slow_operation(tool_name: str, tool_input: dict) -> bool:
#     """Fallback heuristic: commands likely to take > 30s."""
#     if tool_name != "bash":
#         return False
#     cmd = tool_input.get("command", "").lower()
#     slow_keywords = ["install", "build", "test", "deploy", "compile",
#                      "docker build", "pip install", "npm install",
#                      "cargo build", "pytest", "make"]
#     return any(kw in cmd for kw in slow_keywords)
#
# def should_run_background(tool_name: str, tool_input: dict) -> bool:
#     """Model explicit request takes priority; fallback to heuristic."""
#     if tool_input.get("run_in_background"):
#         return True
#     return is_slow_operation(tool_name, tool_input)

def collect_background_results(bg_ids: set[str]) -> list[str]:
    """Collect completed results as task_notification messages."""
    with background_lock:
        ready_ids = [bid for bid, task in background_tasks.items()
                     if bid in bg_ids and task["status"] == "completed"]
    notifications = []
    for bg_id in ready_ids:
        bg_ids.remove(bg_id)
        with background_lock:
            task = background_tasks.pop(bg_id)
            output = background_results.pop(bg_id, "")
        notifications.append(
            f"<task_notification>\n"
            f"  <task_id>{bg_id}</task_id>\n"
            f"  <status>completed</status>\n"
            f"  <summary>{output[:500]}</summary>\n"
            f"</task_notification>")
    return notifications