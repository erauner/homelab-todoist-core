"""Task selection and ranking helpers."""

from __future__ import annotations

from datetime import date

from .models import TaskContext


def has_label(task: TaskContext, label: str) -> bool:
    """Return True if task contains label (case-insensitive)."""
    wanted = label.strip().lower()
    return wanted in {item.lower() for item in task.labels}


def select_focus_task(tasks: tuple[TaskContext, ...]) -> TaskContext | None:
    """Pick deterministic focus task from candidates."""
    if not tasks:
        return None
    return sorted(tasks, key=lambda t: (t.updated_at or date.min, t.id), reverse=True)[0]


def rank_next_action_candidates(tasks: tuple[TaskContext, ...], today: date) -> tuple[TaskContext, ...]:
    """Rank next-action candidates by urgency and priority."""

    def key(task: TaskContext) -> tuple:
        if task.due_date is None:
            bucket = 3
            due_sort = "9999-12-31"
        elif task.due_date < today:
            bucket = 0
            due_sort = task.due_date.isoformat()
        elif task.due_date == today:
            bucket = 1
            due_sort = task.due_date.isoformat()
        else:
            bucket = 2
            due_sort = task.due_date.isoformat()
        return (
            bucket,
            due_sort,
            -int(task.priority or 1),
            task.content.lower(),
        )

    return tuple(sorted(tasks, key=key))
