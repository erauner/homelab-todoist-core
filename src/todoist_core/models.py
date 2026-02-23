"""Shared Todoist policy domain models."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Literal

Source = Literal["manual", "cron", "reminder"]
Mode = Literal[
    "NO_FOCUS_TETHER",
    "ACTIVE_FOCUS_PREP_WINDOW",
    "ACTIVE_FOCUS_EXEC",
    "REMINDER_FOCUS",
    "SKIP",
]


@dataclass(frozen=True)
class TaskContext:
    id: str
    content: str
    labels: tuple[str, ...]
    project_id: str | None = None
    due_date: date | None = None
    due_datetime_local: datetime | None = None
    duration_minutes: int | None = None
    priority: int = 1
    updated_at: datetime | None = None
    url: str | None = None


@dataclass(frozen=True)
class PolicyConfig:
    timezone: str = "America/Chicago"
    allowed_hour_start: int = 9
    allowed_hour_end: int = 18
    prep_window_minutes: int = 180
    require_focus_for_reminder: bool = True
    no_focus_tether_times: tuple[str, ...] = ("09:15", "13:30", "16:45")
    exec_active_minutes: tuple[int, ...] = (0,)
    prep_active_minutes: tuple[int, ...] = (0,)
    exec_active_hour_interval: int = 3
    prep_active_hour_interval: int = 1


@dataclass(frozen=True)
class PolicyInput:
    source: Source
    now_local: datetime
    focus_tasks: tuple[TaskContext, ...]
    next_action_tasks: tuple[TaskContext, ...]
    reminder_task: TaskContext | None = None
    config: PolicyConfig = PolicyConfig()


@dataclass(frozen=True)
class PolicyDecision:
    should_notify: bool
    mode: Mode
    reason: str
    focus_task_id: str | None = None
    candidate_task_ids: tuple[str, ...] = ()
