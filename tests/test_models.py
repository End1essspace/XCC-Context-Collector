from __future__ import annotations

from pathlib import Path

import pytest

from src.xcc.models import (
    CollectionOutcome,
    CollectionResult,
    CollectionRunRecord,
    CollectionStats,
    SafetyWarning,
)


def _result(
    *,
    errors: list[str] | None = None,
    warnings: list[SafetyWarning] | None = None,
) -> CollectionResult:
    return CollectionResult(
        text="# XCC Context\n",
        stats=CollectionStats(
            files=3,
            lines=12,
            chars=240,
            included_files=2,
            omitted_files=1,
            summarized_files=1,
            partial_files=0,
            output_chars=180,
            duration_seconds=1.25,
        ),
        errors=errors or [],
        warnings=warnings or [],
        was_truncated=True,
        omitted_paths=["src/omitted.py"],
    )


def test_collection_result_uses_success_without_findings() -> None:
    result = _result()

    assert result.outcome == CollectionOutcome.SUCCESS
    assert result.stats.warning_count == 0
    assert result.stats.error_count == 0


def test_collection_result_uses_success_with_warnings_for_safety_findings() -> None:
    result = _result(
        warnings=[
            SafetyWarning(
                path="settings.py",
                category="Credential assignment",
                line_number=4,
            )
        ]
    )

    assert result.outcome == CollectionOutcome.SUCCESS_WITH_WARNINGS
    assert result.stats.warning_count == 1
    assert result.stats.error_count == 0


def test_collection_result_keeps_recoverable_errors_separate_from_warnings() -> None:
    result = _result(errors=["Cannot decode file: broken.py"])

    assert result.outcome == CollectionOutcome.SUCCESS_WITH_WARNINGS
    assert result.stats.warning_count == 0
    assert result.stats.error_count == 1


def test_run_record_copies_only_result_metadata() -> None:
    secret_value = "supersecret-value"
    result = _result(
        errors=[f"Cannot decode file: {Path('broken.py')}"],
        warnings=[
            SafetyWarning(
                path="settings.py",
                category="Credential assignment",
                line_number=4,
            )
        ],
    )
    result.text += secret_value

    record = CollectionRunRecord.from_result(
        timestamp="12:34:56",
        mode_name="Full Folder",
        source="D:/project",
        result=result,
    )

    assert record.outcome == CollectionOutcome.SUCCESS_WITH_WARNINGS
    assert record.duration_seconds == 1.25
    assert record.included_files == 2
    assert record.omitted_files == 1
    assert record.summarized_files == 1
    assert record.partial_files == 0
    assert record.warning_count == 1
    assert record.error_count == 1
    assert secret_value not in repr(record)
    assert "Cannot decode" not in repr(record)


def test_cancelled_record_does_not_claim_copied_output() -> None:
    result = _result()

    record = CollectionRunRecord.from_result(
        timestamp="12:34:56",
        mode_name="Full Folder",
        source="D:/project",
        result=result,
        outcome=CollectionOutcome.CANCELLED,
        output_copied=False,
    )

    assert record.outcome == CollectionOutcome.CANCELLED
    assert record.output_chars == 0
    assert record.output_tokens == 0
    assert record.health_label == "Cancelled"


def test_terminal_record_rejects_success_outcome() -> None:
    with pytest.raises(ValueError, match="CANCELLED or FAILED"):
        CollectionRunRecord.terminal(
            timestamp="12:34:56",
            mode_name="Full Folder",
            source="D:/project",
            outcome=CollectionOutcome.SUCCESS,
            duration_seconds=0.5,
        )
