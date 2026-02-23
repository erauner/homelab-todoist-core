"""Parsing helpers for due date and time window gating."""

from __future__ import annotations

from datetime import date, datetime
from zoneinfo import ZoneInfo


def parse_due_date(value: object) -> date | None:
    """Parse date-like value into date."""
    if value is None:
        return None
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        try:
            return date.fromisoformat(value[:10])
        except ValueError:
            return None
    return None


def parse_due_datetime_local(value: object, tz_name: str) -> datetime | None:
    """Parse ISO datetime and convert to local timezone."""
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=ZoneInfo(tz_name))
        return parsed.astimezone(ZoneInfo(tz_name))
    except Exception:
        return None


def parse_hhmm(value: str) -> tuple[int, int]:
    """Parse HH:MM string."""
    raw = value.strip()
    if ":" not in raw:
        msg = f"Invalid HH:MM value: {value}"
        raise ValueError(msg)
    hh, mm = raw.split(":", 1)
    hour = int(hh)
    minute = int(mm)
    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        msg = f"Invalid HH:MM range: {value}"
        raise ValueError(msg)
    return hour, minute


def hour_interval_match(current_hour: int, start_hour: int, interval: int) -> bool:
    """Return True when hour matches interval gate from start hour."""
    if interval <= 1:
        return True
    return ((current_hour - start_hour) % interval) == 0
