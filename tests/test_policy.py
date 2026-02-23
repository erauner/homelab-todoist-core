from datetime import datetime, date
from zoneinfo import ZoneInfo

from todoist_core.models import PolicyConfig, PolicyInput, TaskContext
from todoist_core.policy import evaluate_focus_policy


def test_reminder_requires_focus_label_when_enabled():
    now = datetime(2026, 2, 23, 10, 0, tzinfo=ZoneInfo("America/Chicago"))
    task = TaskContext(id="1", content="Task", labels=("next_action",))
    inp = PolicyInput(
        source="reminder",
        now_local=now,
        focus_tasks=(),
        next_action_tasks=(),
        reminder_task=task,
        config=PolicyConfig(require_focus_for_reminder=True),
    )
    decision = evaluate_focus_policy(inp)
    assert decision.should_notify is False
    assert decision.reason == "reminder_task_not_focused"


def test_no_focus_tether_slot_allows_notify():
    now = datetime(2026, 2, 23, 9, 15, tzinfo=ZoneInfo("America/Chicago"))
    candidate = TaskContext(id="na1", content="Do thing", labels=("next_action",), due_date=date(2026, 2, 23))
    inp = PolicyInput(
        source="cron",
        now_local=now,
        focus_tasks=(),
        next_action_tasks=(candidate,),
        config=PolicyConfig(no_focus_tether_times=("09:15",)),
    )
    decision = evaluate_focus_policy(inp)
    assert decision.should_notify is True
    assert decision.mode == "NO_FOCUS_TETHER"
    assert decision.candidate_task_ids == ("na1",)


def test_focus_exec_hour_interval_gate():
    focus = TaskContext(id="f1", content="Focus", labels=("focus",), due_date=date(2026, 2, 23))
    cfg = PolicyConfig(exec_active_minutes=(0,), exec_active_hour_interval=3, allowed_hour_start=9)

    blocked = PolicyInput(
        source="cron",
        now_local=datetime(2026, 2, 23, 10, 0, tzinfo=ZoneInfo("America/Chicago")),
        focus_tasks=(focus,),
        next_action_tasks=(),
        config=cfg,
    )
    decision_blocked = evaluate_focus_policy(blocked)
    assert decision_blocked.should_notify is False
    assert decision_blocked.reason == "exec_cadence_gate"

    allowed = PolicyInput(
        source="cron",
        now_local=datetime(2026, 2, 23, 12, 0, tzinfo=ZoneInfo("America/Chicago")),
        focus_tasks=(focus,),
        next_action_tasks=(),
        config=cfg,
    )
    decision_allowed = evaluate_focus_policy(allowed)
    assert decision_allowed.should_notify is True
    assert decision_allowed.mode == "ACTIVE_FOCUS_EXEC"
