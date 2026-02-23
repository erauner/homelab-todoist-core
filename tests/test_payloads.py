from datetime import datetime
from zoneinfo import ZoneInfo

from todoist_core.models import PolicyConfig, PolicyDecision, PolicyInput
from todoist_core.payloads import build_openclaw_hook_payload, build_openclaw_message


def test_build_openclaw_payload_shape():
    payload = build_openclaw_hook_payload("hello", to="user:1")
    assert payload["message"] == "hello"
    assert payload["to"] == "user:1"
    assert payload["channel"] == "discord"


def test_build_message_contains_mode_reason():
    decision = PolicyDecision(True, "ACTIVE_FOCUS_EXEC", "focus_exec_window", focus_task_id="f1")
    inp = PolicyInput(
        source="cron",
        now_local=datetime(2026, 2, 23, 9, 0, tzinfo=ZoneInfo("America/Chicago")),
        focus_tasks=(),
        next_action_tasks=(),
        config=PolicyConfig(),
    )
    message = build_openclaw_message(decision, inp)
    assert "mode=ACTIVE_FOCUS_EXEC" in message
    assert "reason=focus_exec_window" in message
