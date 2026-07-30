from __future__ import annotations

from .models import CollectionOutcome


def format_metric_integer(value: int) -> str:
    """Format integer metrics with one stable thousands separator policy."""

    return f"{value:,}"


def outcome_metric_state(outcome: CollectionOutcome) -> str:
    return {
        CollectionOutcome.SUCCESS: "success",
        CollectionOutcome.SUCCESS_WITH_WARNINGS: "warning",
        CollectionOutcome.CANCELLED: "neutral",
        CollectionOutcome.FAILED: "error",
    }[outcome]


def truncation_metric_state(truncated: bool) -> str:
    return "warning" if truncated else "neutral"


def coverage_metric_state(
    *,
    omitted: int,
    summarized: int,
    partial: int,
) -> str:
    return "warning" if omitted or summarized or partial else "neutral"


def issues_metric_state(*, warnings: int, errors: int) -> str:
    if errors:
        return "error"
    if warnings:
        return "warning"
    return "success"
