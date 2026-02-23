"""Normalization helpers for ids and labels."""

from __future__ import annotations


def normalize_id(value: object) -> str:
    """Return canonical string id for mixed int/str values."""
    if value is None:
        return ""
    return str(value).strip()


def normalize_labels(labels: object) -> tuple[str, ...]:
    """Normalize labels into a lowercase tuple."""
    if labels is None:
        return ()
    if isinstance(labels, str):
        items = [labels]
    else:
        try:
            items = list(labels)
        except TypeError:
            return ()
    normalized = [str(item).strip().lower() for item in items if str(item).strip()]
    return tuple(normalized)
