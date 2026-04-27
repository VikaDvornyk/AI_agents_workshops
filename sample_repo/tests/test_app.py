"""Tests for the Task Manager application."""

import sys
sys.path.insert(0, "..")

from models import Task, Priority, Status
from app import TaskManager


def test_add_task():
    manager = TaskManager()
    task = manager.add_task("Test task", priority="high")
    assert task.id == 1
    assert task.title == "Test task"
    assert task.priority == Priority.HIGH
    assert task.status == Status.TODO


def test_complete_task():
    manager = TaskManager()
    manager.add_task("Task 1")
    result = manager.complete_task(1)
    assert result is not None
    assert result.status == Status.DONE
    assert result.completed_at is not None


def test_complete_nonexistent_task():
    manager = TaskManager()
    result = manager.complete_task(999)
    assert result is None


def test_delete_task():
    manager = TaskManager()
    manager.add_task("To delete")
    assert manager.delete_task(1) is True
    assert manager.get_task(1) is None


def test_list_tasks_with_filter():
    manager = TaskManager()
    manager.add_task("Low task", priority="low")
    manager.add_task("High task", priority="high")
    high = manager.list_tasks(priority="high")
    assert len(high) == 1
    assert high[0].title == "High task"


def test_search():
    manager = TaskManager()
    manager.add_task("Fix login bug", "Authentication issue")
    manager.add_task("Add feature", "New dashboard")
    results = manager.search("login")
    assert len(results) == 1
    assert results[0].title == "Fix login bug"


# NOTE: test for get_statistics is missing — completion_rate may be broken
