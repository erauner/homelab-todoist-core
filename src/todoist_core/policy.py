"""Deterministic policy evaluation for reminder/cron/manual flows."""

from __future__ import annotations

from datetime import timedelta

from .models import PolicyDecision, PolicyInput
from .parsing import hour_interval_match, parse_hhmm
from .selectors import has_label, rank_next_action_candidates, select_focus_task


def evaluate_focus_policy(inp: PolicyInput) -> PolicyDecision:
    """Evaluate policy and return deterministic decision."""
    cfg = inp.config
    now = inp.now_local

    if inp.source != "manual":
        if now.hour < cfg.allowed_hour_start or now.hour >= cfg.allowed_hour_end:
            return PolicyDecision(False, "SKIP", "outside_allowed_window")

    if inp.source == "reminder":
        if inp.reminder_task is None:
            return PolicyDecision(False, "SKIP", "missing_reminder_task")
        if cfg.require_focus_for_reminder and not has_label(inp.reminder_task, "focus"):
            return PolicyDecision(False, "SKIP", "reminder_task_not_focused")
        return PolicyDecision(True, "REMINDER_FOCUS", "focused_reminder_task", focus_task_id=inp.reminder_task.id)

    focus = select_focus_task(inp.focus_tasks)
    if focus is None:
        slots = {parse_hhmm(t) for t in cfg.no_focus_tether_times}
        if inp.source == "manual" or (now.hour, now.minute) in slots:
            candidates = rank_next_action_candidates(inp.next_action_tasks, now.date())
            return PolicyDecision(
                True,
                "NO_FOCUS_TETHER",
                "no_focus_candidates",
                candidate_task_ids=tuple(item.id for item in candidates[:3]),
            )
        return PolicyDecision(False, "SKIP", "no_focus_not_tether_slot")

    if inp.source == "manual":
        return PolicyDecision(True, "ACTIVE_FOCUS_EXEC", "manual_focus_checkin", focus_task_id=focus.id)

    if focus.due_datetime_local is not None:
        due_dt = focus.due_datetime_local
        if due_dt.date() > now.date():
            return PolicyDecision(False, "SKIP", "focus_due_future_day")
        if due_dt > now:
            prep_start = due_dt - timedelta(minutes=cfg.prep_window_minutes)
            if now < prep_start:
                return PolicyDecision(False, "SKIP", "before_prep_window")
            if now.minute not in set(cfg.prep_active_minutes) or not hour_interval_match(
                now.hour,
                cfg.allowed_hour_start,
                cfg.prep_active_hour_interval,
            ):
                return PolicyDecision(False, "SKIP", "prep_cadence_gate")
            return PolicyDecision(True, "ACTIVE_FOCUS_PREP_WINDOW", "prep_window_open", focus_task_id=focus.id)

    if focus.due_date is not None and focus.due_date > now.date():
        return PolicyDecision(False, "SKIP", "focus_due_future_day")

    if now.minute not in set(cfg.exec_active_minutes) or not hour_interval_match(
        now.hour,
        cfg.allowed_hour_start,
        cfg.exec_active_hour_interval,
    ):
        return PolicyDecision(False, "SKIP", "exec_cadence_gate")

    return PolicyDecision(True, "ACTIVE_FOCUS_EXEC", "focus_exec_window", focus_task_id=focus.id)
