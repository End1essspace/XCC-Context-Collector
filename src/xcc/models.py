from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


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


@dataclass(slots=True)
class CollectionResult:
    text: str
    stats: CollectionStats
    errors: list[str]
    was_truncated: bool = False
    omitted_paths: list[str] = field(default_factory=list)
    warnings: list[SafetyWarning] = field(default_factory=list)
