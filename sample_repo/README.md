# Task Manager

A simple CLI task manager with priority levels, status tracking, and reporting.

## Features

- Create, complete, and delete tasks
- Filter by status and priority
- Search by title/description
- Export to JSON
- Task statistics

## Usage

```python
from app import TaskManager

manager = TaskManager()
manager.add_task("My task", priority="high", assignee="alice")
manager.complete_task(1)
print(manager.stats())
```

## Running

```bash
python app.py
```
