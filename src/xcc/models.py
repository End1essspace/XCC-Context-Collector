from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class CollectionOutcome(str, Enum):
    SUCCESS = "SUCCESS"
    SUCCESS_WITH_WARNINGS = "SUCCESS_WITH_WARNINGS"
    CANCELLED = "CANCELLED"
    FAILED = "FAILED"

    @property
    def health_label(self) -> str:
        return {
            CollectionOutcome.SUCCESS: "Completed",
            CollectionOutcome.SUCCESS_WITH_WARNINGS: "Completed with warnings",
            CollectionOutcome.CANCELLED: "Cancelled",
            CollectionOutcome.FAILED: "Failed",
        }[self]

    @property
    def metric_label(self) -> str:
        return {
            CollectionOutcome.SUCCESS: "Success",
            CollectionOutcome.SUCCESS_WITH_WARNINGS: "With warnings",
            CollectionOutcome.CANCELLED: "Cancelled",
            CollectionOutcome.FAILED: "Failed",
        }[self]

    @property
    def is_success(self) -> bool:
        return self in {
            CollectionOutcome.SUCCESS,
            CollectionOutcome.SUCCESS_WITH_WARNINGS,
        }


@dataclass(slots=True)
class FileContent:
    path: Path
    content: str
    line_count: int
    char_count: int
    is_summary: bool = False


@dataclass(frozen=True, slots=True)
class GitChange:
    """One porcelain-v1 Git change with separate index/worktree states."""

    index_status: str
    worktree_status: str
    path: str
    original_path: str | None = None

    @property
    def status_code(self) -> str:
        return f"{self.index_status}{self.worktree_status}"

    @property
    def has_staged_change(self) -> bool:
        return self.index_status not in {" ", "?", "!"}

    @property
    def has_unstaged_change(self) -> bool:
        return self.worktree_status not in {" ", "?", "!"}

    @property
    def is_untracked(self) -> bool:
        return self.status_code == "??"

    @property
    def is_deleted(self) -> bool:
        return "D" in self.status_code

    @property
    def is_rename_or_copy(self) -> bool:
        return (
            self.index_status in {"R", "C"}
            or self.worktree_status in {"R", "C"}
        )

    @property
    def display_path(self) -> str:
        if self.original_path is not None and self.is_rename_or_copy:
            return f"{self.original_path} -> {self.path}"

        return self.path


@dataclass(slots=True)
class GitContext:
    changes: list[GitChange] = field(default_factory=list)
    staged_diff: str = ""
    unstaged_diff: str = ""

    @property
    def has_changes(self) -> bool:
        return bool(self.changes)

    @property
    def has_diff(self) -> bool:
        return bool(self.staged_diff or self.unstaged_diff)


@dataclass(slots=True)
class SafetyWarning:
    path: str
    category: str
    line_number: int | None = None

    @property
    def location(self) -> str:
        if self.line_number is None:
            return self.path

        return f"{self.path}:{self.line_number}"


@dataclass(slots=True)
class CollectionStats:
    files: int
    lines: int
    chars: int
    included_files: int = 0
    omitted_files: int = 0
    partial_files: int = 0
    summarized_files: int = 0
    budget_limit: int | None = None
    output_chars: int = 0
    warning_count: int = 0
    error_count: int = 0
    duration_seconds: float = 0.0


@dataclass(slots=True)
class CollectionResult:
    text: str
    stats: CollectionStats
    errors: list[str]
    was_truncated: bool = False
    omitted_paths: list[str] = field(default_factory=list)
    warnings: list[SafetyWarning] = field(default_factory=list)
    outcome: CollectionOutcome = field(init=False)

    def __post_init__(self) -> None:
        self.stats.warning_count = len(self.warnings)
        self.stats.error_count = len(self.errors)
        self.outcome = (
            CollectionOutcome.SUCCESS_WITH_WARNINGS
            if self.warnings or self.errors
            else CollectionOutcome.SUCCESS
        )


@dataclass(frozen=True, slots=True)
class CollectionRunRecord:
    timestamp: str
    mode_name: str
    source: str
    outcome: CollectionOutcome
    duration_seconds: float = 0.0
    files: int = 0
    lines: int = 0
    source_chars: int = 0
    output_chars: int = 0
    output_tokens: int = 0
    included_files: int = 0
    omitted_files: int = 0
    summarized_files: int = 0
    partial_files: int = 0
    truncated: bool = False
    warning_count: int = 0
    error_count: int = 0

    @classmethod
    def from_result(
        cls,
        *,
        timestamp: str,
        mode_name: str,
        source: str,
        result: CollectionResult,
        outcome: CollectionOutcome | None = None,
        output_copied: bool = True,
    ) -> "CollectionRunRecord":
        output_chars = result.stats.output_chars or len(result.text)
        if not output_copied:
            output_chars = 0

        return cls(
            timestamp=timestamp,
            mode_name=mode_name,
            source=source,
            outcome=outcome or result.outcome,
            duration_seconds=max(0.0, result.stats.duration_seconds),
            files=result.stats.files,
            lines=result.stats.lines,
            source_chars=result.stats.chars,
            output_chars=output_chars,
            output_tokens=output_chars // 4,
            included_files=result.stats.included_files,
            omitted_files=result.stats.omitted_files,
            summarized_files=result.stats.summarized_files,
            partial_files=result.stats.partial_files,
            truncated=result.was_truncated,
            warning_count=result.stats.warning_count,
            error_count=result.stats.error_count,
        )

    @classmethod
    def terminal(
        cls,
        *,
        timestamp: str,
        mode_name: str,
        source: str,
        outcome: CollectionOutcome,
        duration_seconds: float,
    ) -> "CollectionRunRecord":
        if outcome.is_success:
            raise ValueError("terminal records require CANCELLED or FAILED outcome")

        return cls(
            timestamp=timestamp,
            mode_name=mode_name,
            source=source,
            outcome=outcome,
            duration_seconds=max(0.0, duration_seconds),
        )

    @property
    def health_label(self) -> str:
        return self.outcome.health_label

    @property
    def duration_label(self) -> str:
        if self.duration_seconds < 0.01:
            return "<0.01 s"

        return f"{self.duration_seconds:.2f} s"
