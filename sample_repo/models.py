"""Data models for the Task Manager application."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class Priority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Status(Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    CANCELLED = "cancelled"


@dataclass
class Task:
    title: str
    description: str = ""
    priority: Priority = Priority.MEDIUM
    status: Status = Status.TODO
    assignee: str | None = None
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: datetime | None = None
    tags: list[str] = field(default_factory=list)
    id: int | None = None

    def complete(self):
        """Mark task as done."""
        self.status = Status.DONE
        self.completed_at = datetime.now()

    def is_overdue(self, deadline: datetime) -> bool:
        """Check if the task is overdue."""
        if self.status == Status.DONE:
            return False
        return datetime.now() > deadline

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority.value,
            "status": self.status.value,
            "assignee": self.assignee,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "tags": self.tags,
        }
