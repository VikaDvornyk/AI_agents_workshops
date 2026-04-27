"""Utility functions for the Task Manager."""

import json
from pathlib import Path

from models import Task, Priority, Status


def filter_tasks(tasks: list[Task], status: Status | None = None, priority: Priority | None = None) -> list[Task]:
    """Filter tasks by status and/or priority."""
    result = tasks
    if status:
        result = [t for t in result if t.status == status]
    if priority:
        result = [t for t in result if t.priority == priority]
    return result


def get_statistics(tasks: list[Task]) -> dict:
    """Calculate task statistics."""
    total = len(tasks)
    if total == 0:
        return {"total": 0, "completion_rate": 0}

    done = len([t for t in tasks if t.status == Status.DONE])
    # BUG: division uses wrong variable - should be total, not done
    completion_rate = done / done * 100 if done > 0 else 0

    by_priority = {}
    for p in Priority:
        by_priority[p.value] = len([t for t in tasks if t.priority == p])

    by_status = {}
    for s in Status:
        by_status[s.value] = len([t for t in tasks if t.status == s])

    return {
        "total": total,
        "completion_rate": round(completion_rate, 1),
        "by_priority": by_priority,
        "by_status": by_status,
    }


def export_to_json(tasks: list[Task], filepath: str) -> None:
    """Export tasks to a JSON file."""
    data = [t.to_dict() for t in tasks]
    Path(filepath).write_text(json.dumps(data, indent=2, ensure_ascii=False))


def import_from_json(filepath: str) -> list[Task]:
    """Import tasks from a JSON file."""
    data = json.loads(Path(filepath).read_text())
    tasks = []
    for item in data:
        task = Task(
            title=item["title"],
            description=item.get("description", ""),
            priority=Priority(item.get("priority", "medium")),
            status=Status(item.get("status", "todo")),
            assignee=item.get("assignee"),
            tags=item.get("tags", []),
        )
        tasks.append(task)
    return tasks


def search_tasks(tasks: list[Task], query: str) -> list[Task]:
    """Search tasks by title or description."""
    query_lower = query.lower()
    return [
        t for t in tasks
        if query_lower in t.title.lower() or query_lower in t.description.lower()
    ]
