"""OpenClaw payload builders."""

from __future__ import annotations

from .models import PolicyDecision, PolicyInput


def build_openclaw_message(decision: PolicyDecision, inp: PolicyInput) -> str:
    """Build mode-specific instruction prompt used by CLI and events flows."""
    header = (
        "Run the unified focus orchestrator check-in using tools first, no guessing. "
        f"Source={inp.source} mode={decision.mode} reason={decision.reason}. "
        "Do not manually add/remove next_action labels; treat next_action as Autodoist-managed read-only. "
        "Ask at most one question unless user requests more. "
    )

    if decision.mode == "NO_FOCUS_TETHER":
        candidate_ids = ", ".join(decision.candidate_task_ids) if decision.candidate_task_ids else "(none)"
        return header + (
            "Mode=NO_FOCUS. "
            "Execute in order: 1) td autodoist focus --apply 2) td autodoist tasks --label focus "
            '3) td next --table 4) td query "(today | overdue)". '
            f"Current ranked candidate ids from policy: {candidate_ids}. "
            "Provide one cohesive message with: Status, top 1-2 focus candidates (id + title + link + one-line why now), "
            "recommended candidate, and one concise confirm question to set focus."
        )

    if decision.mode == "ACTIVE_FOCUS_PREP_WINDOW":
        focus_id = decision.focus_task_id or "(missing)"
        return header + (
            "Mode=PREP_MODE (focused task due later today and prep window is open). "
            f"Focused task id: {focus_id}. "
            "Execute in order: 1) td autodoist focus --apply 2) td autodoist tasks --label focus "
            "3) td show <focus_task_id> 4) td next --table. "
            "Concentrate on preparation before start time: extract missing prerequisites, propose a short start checklist, "
            "identify one immediate prep action, and ask one question only if a critical detail is missing. "
            "Output format: Mode, Status, Prep action now, Start checklist (3 bullets max), Why this reduces startup friction, Definition of done."
        )

    if decision.mode in {"ACTIVE_FOCUS_EXEC", "REMINDER_FOCUS"}:
        focus_id = decision.focus_task_id or "(missing)"
        return header + (
            "Mode=EXEC_MODE (focused task due now/overdue/no due or reminder-fired focused task). "
            f"Focused task id: {focus_id}. "
            "Execute in order: 1) td autodoist focus --apply 2) td autodoist tasks --label focus "
            "3) td show <focus_task_id> 4) td next --table. "
            'Concentrate on progress/notes and starting momentum: ask for concrete progress update, capture progress with '
            'td progress <focus_task_id> "..." --type progress when user provides details, and nudge one concrete next step. '
            "If no progress yet, suggest the smallest actionable start step from existing context. "
            "If no due time/date is present, include one soft question: \"Do you want to set a target time today?\" while keeping execute behavior. "
            "Output format: Mode, Status, Best next step, Progress checkpoint question, Definition of done."
        )

    return header + "No action."


def build_openclaw_hook_payload(
    message: str,
    to: str,
    channel: str = "discord",
    name: str = "Focus Follow-up",
) -> dict:
    """Build standard OpenClaw /hooks/agent payload."""
    return {
        "message": message,
        "name": name,
        "deliver": True,
        "channel": channel,
        "to": to,
    }
