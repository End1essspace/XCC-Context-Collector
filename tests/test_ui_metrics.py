from __future__ import annotations

from xcc.models import CollectionOutcome
from xcc.ui_metrics import (
    coverage_metric_state,
    format_metric_integer,
    issues_metric_state,
    outcome_metric_state,
    truncation_metric_state,
)


def test_metric_integer_formatting_is_consistent() -> None:
    assert format_metric_integer(0) == "0"
    assert format_metric_integer(51) == "51"
    assert format_metric_integer(10_691) == "10,691"
    assert format_metric_integer(349_675) == "349,675"
    assert format_metric_integer(356_647) == "356,647"
    assert format_metric_integer(89_161) == "89,161"


def test_outcome_states_match_product_semantics() -> None:
    assert outcome_metric_state(CollectionOutcome.SUCCESS) == "success"
    assert outcome_metric_state(CollectionOutcome.SUCCESS_WITH_WARNINGS) == "warning"
    assert outcome_metric_state(CollectionOutcome.CANCELLED) == "neutral"
    assert outcome_metric_state(CollectionOutcome.FAILED) == "error"


def test_metric_health_states_are_explicit() -> None:
    assert truncation_metric_state(False) == "neutral"
    assert truncation_metric_state(True) == "warning"

    assert coverage_metric_state(omitted=0, summarized=0, partial=0) == "neutral"
    assert coverage_metric_state(omitted=1, summarized=0, partial=0) == "warning"
    assert coverage_metric_state(omitted=0, summarized=1, partial=0) == "warning"

    assert issues_metric_state(warnings=0, errors=0) == "success"
    assert issues_metric_state(warnings=1, errors=0) == "warning"
    assert issues_metric_state(warnings=0, errors=1) == "error"
