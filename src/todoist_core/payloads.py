"""OpenClaw payload builders."""

from __future__ import annotations

from .models import PolicyDecision, PolicyInput


def build_openclaw_message(decision: PolicyDecision, inp: PolicyInput) -> str:
    """Build short mode-specific instruction prompt."""
    header = (
        "Run unified Todoist check-in using CLI tools only. "
        f"Source={inp.source} mode={decision.mode} reason={decision.reason}. "
    )
    if decision.mode == "NO_FOCUS_TETHER":
        return header + "No focus set. Propose top next_action candidates and ask one confirm question."
    if decision.mode == "ACTIVE_FOCUS_PREP_WINDOW":
        return header + "Focus exists in prep window. Provide prep checklist and one immediate prep step."
    if decision.mode in {"ACTIVE_FOCUS_EXEC", "REMINDER_FOCUS"}:
        return header + "Focus execution check-in. Ask for progress and suggest one concrete next step."
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
