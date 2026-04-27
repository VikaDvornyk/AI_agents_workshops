"""Task Manager CLI Application.

A simple task management tool with priority levels,
status tracking, and basic reporting.
"""

from models import Task, Priority, Status
from utils import filter_tasks, get_statistics, search_tasks, export_to_json


class TaskManager:
    """Main task manager that handles all operations."""

    def __init__(self):
        self._tasks: list[Task] = []
        self._next_id: int = 1

    def add_task(self, title: str, description: str = "", priority: str = "medium", assignee: str | None = None, tags: list[str] | None = None) -> Task:
        """Add a new task."""
        task = Task(
            title=title,
            description=description,
            priority=Priority(priority),
            assignee=assignee,
            tags=tags or [],
            id=self._next_id,
        )
        self._tasks.append(task)
        self._next_id += 1
        return task

    def complete_task(self, task_id: int) -> Task | None:
        """Mark a task as complete."""
        task = self.get_task(task_id)
        if task:
            task.complete()
            return task
        return None

    def get_task(self, task_id: int) -> Task | None:
        """Get a task by ID."""
        for task in self._tasks:
            if task.id == task_id:
                return task
        return None

    def delete_task(self, task_id: int) -> bool:
        """Delete a task by ID."""
        task = self.get_task(task_id)
        if task:
            self._tasks.remove(task)
            return True
        return False

    def list_tasks(self, status: str | None = None, priority: str | None = None) -> list[Task]:
        """List tasks with optional filters."""
        s = Status(status) if status else None
        p = Priority(priority) if priority else None
        return filter_tasks(self._tasks, status=s, priority=p)

    def search(self, query: str) -> list[Task]:
        """Search tasks."""
        return search_tasks(self._tasks, query)

    def stats(self) -> dict:
        """Get task statistics."""
        return get_statistics(self._tasks)

    def export(self, filepath: str) -> None:
        """Export all tasks to JSON."""
        export_to_json(self._tasks, filepath)


def main():
    """Demo usage of TaskManager."""
    manager = TaskManager()

    # Add sample tasks
    manager.add_task("Set up CI/CD pipeline", "Configure GitHub Actions for automated testing", priority="high", assignee="alice", tags=["devops", "automation"])
    manager.add_task("Write unit tests", "Cover models and utils with tests", priority="high", assignee="bob", tags=["testing"])
    manager.add_task("Update README", "Add installation and usage instructions", priority="low", tags=["docs"])
    manager.add_task("Fix login bug", "Users can't log in with special characters in password", priority="critical", assignee="alice", tags=["bug", "auth"])
    manager.add_task("Refactor database layer", "Move from raw SQL to ORM", priority="medium", assignee="charlie", tags=["refactoring", "database"])

    # Complete some tasks
    manager.complete_task(1)
    manager.complete_task(4)

    # Show stats
    stats = manager.stats()
    print(f"Task Statistics:")
    print(f"  Total: {stats['total']}")
    print(f"  Completion Rate: {stats['completion_rate']}%")
    print(f"  By Status: {stats['by_status']}")
    print(f"  By Priority: {stats['by_priority']}")

    # Search
    results = manager.search("test")
    print(f"\nSearch 'test': {[t.title for t in results]}")

    # Filter
    high_priority = manager.list_tasks(priority="high")
    print(f"High priority: {[t.title for t in high_priority]}")


if __name__ == "__main__":
    main()
