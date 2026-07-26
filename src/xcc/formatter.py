from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path, PurePath, PureWindowsPath

from . import __version__
from .budget import join_sections, minimal_budget_notice, validate_char_budget
from .config import MAX_OUTPUT_CHARS
from .models import (
    CollectionResult,
    CollectionStats,
    FileContent,
    GitChange,
    GitContext,
    SafetyWarning,
)
from .optimizer import compact_generated_text
from .safety import format_warning_lines
from .tree import build_directory_tree, build_project_tree

_MAX_LISTED_OMITTED_PATHS = 20
_MAX_LISTED_SAFETY_WARNINGS = 20


@dataclass(slots=True)
class _BudgetDetails:
    included_files: int
    omitted_paths: list[str]
    summarized_files: int
    git_diff_status: str
    project_tree_status: str
    errors_status: str
    safety_status: str


def format_collection(
    files: list[FileContent],
    errors: list[str] | None = None,
    *,
    project_root: str | Path | None = None,
    compact: bool = True,
    mode_name: str = "Compact",
    max_output_chars: int | None = MAX_OUTPUT_CHARS,
    git_context: GitContext | None = None,
    git_diff: str | None = None,
    warnings: list[SafetyWarning] | None = None,
    include_project_tree: bool = True,
) -> CollectionResult:
    errors = errors or []
    warnings = warnings or []
    validate_char_budget(max_output_chars)

    stats = CollectionStats(
        files=len(files),
        lines=sum(file.line_count for file in files),
        chars=sum(file.char_count for file in files),
        budget_limit=max_output_chars,
        warning_count=len(warnings),
    )

    header = _format_generated_lines(
        [
            "# XCC Context",
            "",
            f"XCC Version: {__version__}",
            f"Mode: {mode_name}",
            (
                "Max Output Characters: "
                f"{max_output_chars if max_output_chars is not None else 'Unlimited'}"
            ),
            "",
            f"Files: {stats.files}",
            f"Lines: {stats.lines}",
            f"Characters: {stats.chars}",
        ],
        compact=compact,
    )

    display_paths = make_display_paths(
        [file.path for file in files],
        project_root=project_root,
    )

    if git_context is not None:
        git_section = _format_git_context(git_context, compact=compact)
    else:
        # Backward-compatible support for callers that still pass one raw diff.
        git_section = (
            _format_preserved_block("# Git Diff", git_diff)
            if git_diff
            else ""
        )

    safety_section = _format_safety_warnings(warnings, compact=compact)

    tree = (
        build_project_tree([file.path for file in files], project_root)
        if include_project_tree
        else ""
    )
    tree_section = _format_generated_text(tree, compact=compact) if tree else ""

    file_sections = [
        format_file(file, display_path=display_path)
        for file, display_path in zip(files, display_paths, strict=True)
    ]

    errors_section = (
        _format_generated_lines(
            [
                "# XCC Errors",
                "",
                *[f"- {error}" for error in errors],
            ],
            compact=compact,
        )
        if errors
        else ""
    )

    full_sections = [header]
    if safety_section:
        full_sections.append(safety_section)
    if git_section:
        full_sections.append(git_section)
    if tree_section:
        full_sections.append(tree_section)
    if file_sections:
        full_sections.append("# Files")
        full_sections.extend(file_sections)
    if errors_section:
        full_sections.append(errors_section)

    full_text = join_sections(full_sections)

    if max_output_chars is None or len(full_text) <= max_output_chars:
        stats.included_files = len(files)
        stats.omitted_files = 0
        stats.partial_files = 0
        stats.summarized_files = sum(file.is_summary for file in files)
        stats.output_chars = len(full_text)

        return CollectionResult(
            text=full_text,
            stats=stats,
            errors=errors,
            was_truncated=False,
            omitted_paths=[],
            warnings=list(warnings),
        )

    return _format_budgeted_collection(
        files=files,
        errors=errors,
        display_paths=display_paths,
        header=header,
        safety_section=safety_section,
        git_section=git_section,
        tree_section=tree_section,
        file_sections=file_sections,
        errors_section=errors_section,
        max_output_chars=max_output_chars,
        stats=stats,
        warnings=warnings,
    )


def format_project_tree(
    project_root: str | Path,
    *,
    compact: bool = True,
    mode_name: str = "Project Tree",
    max_output_chars: int | None = MAX_OUTPUT_CHARS,
    warnings: list[SafetyWarning] | None = None,
    tree_progress_callback: Callable[[int, int], None] | None = None,
    cancel_check: Callable[[], bool] | None = None,
) -> CollectionResult:
    warnings = warnings or []
    validate_char_budget(max_output_chars)

    tree, file_count, directory_count = build_directory_tree(
        project_root,
        progress_callback=tree_progress_callback,
        cancel_check=cancel_check,
    )

    stats = CollectionStats(
        files=file_count,
        lines=tree.count("\n") + 1 if tree else 0,
        chars=len(tree),
        budget_limit=max_output_chars,
        warning_count=len(warnings),
    )

    header = _format_generated_lines(
        [
            "# XCC Context",
            "",
            f"XCC Version: {__version__}",
            f"Mode: {mode_name}",
            (
                "Max Output Characters: "
                f"{max_output_chars if max_output_chars is not None else 'Unlimited'}"
            ),
            "",
            f"Files: {stats.files}",
            f"Directories: {directory_count}",
            f"Lines: {stats.lines}",
            f"Characters: {stats.chars}",
        ],
        compact=compact,
    )

    safety_section = _format_safety_warnings(warnings, compact=compact)
    tree_section = _format_generated_text(tree, compact=compact) if tree else ""
    full_sections = [header]
    if safety_section:
        full_sections.append(safety_section)
    if tree_section:
        full_sections.append(tree_section)
    full_text = join_sections(full_sections)

    if max_output_chars is None or len(full_text) <= max_output_chars:
        stats.included_files = file_count
        stats.omitted_files = 0
        stats.output_chars = len(full_text)

        return CollectionResult(
            text=full_text,
            stats=stats,
            errors=[],
            was_truncated=False,
            warnings=list(warnings),
        )

    details = _BudgetDetails(
        included_files=0,
        omitted_paths=[],
        summarized_files=0,
        git_diff_status="not requested",
        project_tree_status="omitted",
        errors_status="none",
        safety_status="included" if safety_section else "none",
    )

    base_sections = [header]
    if safety_section:
        base_sections.append(safety_section)
    rendered = _render_budgeted_output(base_sections, details, max_output_chars)

    if rendered is None:
        text = minimal_budget_notice(max_output_chars)
        stats.included_files = 0
        stats.omitted_files = file_count
        stats.output_chars = len(text)
        return CollectionResult(
            text=text,
            stats=stats,
            errors=[],
            was_truncated=True,
            warnings=list(warnings),
        )

    if tree_section:
        lines = tree_section.splitlines(keepends=True)
        low = 0
        high = len(lines)
        best_text = rendered
        best_count = 0

        while low <= high:
            middle = (low + high) // 2
            prefix = "".join(lines[:middle])

            candidate_details = _copy_budget_details(details)
            candidate_details.project_tree_status = (
                "included" if middle == len(lines) else "partial"
            )
            candidate_sections = list(base_sections)
            if prefix:
                candidate_sections.append(prefix)

            candidate_text = _render_budgeted_output(
                candidate_sections,
                candidate_details,
                max_output_chars,
            )

            if candidate_text is not None:
                best_text = candidate_text
                best_count = middle
                low = middle + 1
            else:
                high = middle - 1

        if best_count == 0:
            details.project_tree_status = "omitted"
            rendered = _render_budgeted_output(
                base_sections,
                details,
                max_output_chars,
            )
            if rendered is not None:
                best_text = rendered

        rendered = best_text
        included_tree_lines = lines[:best_count]
        included_file_count = sum(
            1
            for line in included_tree_lines
            if line.strip()
            and line.strip() != "# Project Tree"
            and not line.rstrip("\n").endswith("/")
        )
        stats.included_files = included_file_count
        stats.omitted_files = max(0, file_count - included_file_count)
    else:
        stats.included_files = 0
        stats.omitted_files = file_count

    stats.output_chars = len(rendered)

    return CollectionResult(
        text=rendered,
        stats=stats,
        errors=[],
        was_truncated=True,
        warnings=list(warnings),
    )


def format_file(
    file: FileContent,
    *,
    project_root: str | Path | None = None,
    display_path: str | None = None,
) -> str:
    if display_path is None:
        display_path = make_display_path(file.path, project_root)

    # The file payload is appended verbatim. Do not strip, compact, normalize,
    # or otherwise rewrite source content here.
    return f"===== file: {display_path} =====\n\n{file.content}"


def _format_budgeted_collection(
    *,
    files: list[FileContent],
    errors: list[str],
    display_paths: list[str],
    header: str,
    safety_section: str,
    git_section: str,
    tree_section: str,
    file_sections: list[str],
    errors_section: str,
    max_output_chars: int,
    stats: CollectionStats,
    warnings: list[SafetyWarning],
) -> CollectionResult:
    details = _BudgetDetails(
        included_files=0,
        omitted_paths=list(display_paths),
        summarized_files=0,
        git_diff_status="omitted" if git_section else "not requested",
        project_tree_status="omitted" if tree_section else "not requested",
        errors_status="omitted" if errors_section else "none",
        safety_status="omitted" if safety_section else "none",
    )
    sections = [header]

    base_rendered = _render_budgeted_output(sections, details, max_output_chars)
    if base_rendered is None:
        text = minimal_budget_notice(max_output_chars)
        stats.omitted_files = len(files)
        stats.output_chars = len(text)

        return CollectionResult(
            text=text,
            stats=stats,
            errors=errors,
            was_truncated=True,
            omitted_paths=list(display_paths),
            warnings=list(warnings),
        )

    if safety_section:
        candidate_details = _copy_budget_details(details)
        candidate_details.safety_status = "included"
        candidate_sections = [*sections, safety_section]

        if _render_budgeted_output(
            candidate_sections,
            candidate_details,
            max_output_chars,
        ) is not None:
            sections = candidate_sections
            details = candidate_details

    if git_section:
        candidate_details = _copy_budget_details(details)
        candidate_details.git_diff_status = "included"
        candidate_sections = [*sections, git_section]

        if _render_budgeted_output(
            candidate_sections,
            candidate_details,
            max_output_chars,
        ) is not None:
            sections = candidate_sections
            details = candidate_details

    if tree_section:
        candidate_details = _copy_budget_details(details)
        candidate_details.project_tree_status = "included"
        candidate_sections = [*sections, tree_section]

        if _render_budgeted_output(
            candidate_sections,
            candidate_details,
            max_output_chars,
        ) is not None:
            sections = candidate_sections
            details = candidate_details

    if file_sections:
        heading_sections = [*sections, "# Files"]
        if _render_budgeted_output(
            heading_sections,
            details,
            max_output_chars,
        ) is not None:
            sections = heading_sections

            for index, (file, file_section) in enumerate(
                zip(files, file_sections, strict=True)
            ):
                candidate_details = _copy_budget_details(details)
                candidate_details.included_files = index + 1
                candidate_details.omitted_paths = display_paths[index + 1 :]
                candidate_details.summarized_files = sum(
                    item.is_summary for item in files[: index + 1]
                )
                candidate_sections = [*sections, file_section]

                if _render_budgeted_output(
                    candidate_sections,
                    candidate_details,
                    max_output_chars,
                ) is None:
                    break

                sections = candidate_sections
                details = candidate_details

    if errors_section:
        candidate_details = _copy_budget_details(details)
        candidate_details.errors_status = "included"
        candidate_sections = [*sections, errors_section]

        if _render_budgeted_output(
            candidate_sections,
            candidate_details,
            max_output_chars,
        ) is not None:
            sections = candidate_sections
            details = candidate_details

    rendered = _render_budgeted_output(sections, details, max_output_chars)

    if rendered is None:
        rendered = minimal_budget_notice(max_output_chars)
        details.included_files = 0
        details.omitted_paths = list(display_paths)
        details.summarized_files = 0

    stats.included_files = details.included_files
    stats.omitted_files = len(details.omitted_paths)
    stats.partial_files = 0
    stats.summarized_files = details.summarized_files
    stats.output_chars = len(rendered)

    return CollectionResult(
        text=rendered,
        stats=stats,
        errors=errors,
        was_truncated=True,
        omitted_paths=list(details.omitted_paths),
        warnings=list(warnings),
    )


def _render_budgeted_output(
    sections: list[str],
    details: _BudgetDetails,
    max_output_chars: int,
) -> str | None:
    max_listed = min(
        len(details.omitted_paths),
        _MAX_LISTED_OMITTED_PATHS,
    )

    for listed_count in range(max_listed, -1, -1):
        used = 0
        text = ""

        for _ in range(12):
            summary = _build_budget_summary(
                max_output_chars=max_output_chars,
                used_chars=used,
                details=details,
                listed_count=listed_count,
            )
            text = join_sections([*sections, summary])
            new_used = len(text)

            if new_used == used:
                break

            used = new_used

        if len(text) <= max_output_chars:
            return text

    return None


def _build_budget_summary(
    *,
    max_output_chars: int,
    used_chars: int,
    details: _BudgetDetails,
    listed_count: int,
) -> str:
    omitted_count = len(details.omitted_paths)

    lines = [
        "# XCC Budget Summary",
        "",
        f"Limit: {max_output_chars}",
        f"Used: {used_chars}",
        f"Included files: {details.included_files}",
        f"Omitted files: {omitted_count}",
        "Partial files: 0",
        f"Summarized files: {details.summarized_files}",
        f"Git diff: {details.git_diff_status}",
        f"Project tree: {details.project_tree_status}",
        f"Errors: {details.errors_status}",
    ]

    if details.safety_status != "none":
        lines.append(f"Safety warnings: {details.safety_status}")

    if omitted_count:
        lines.extend(["", "Omitted:"])

        for path in details.omitted_paths[:listed_count]:
            lines.append(f"- {path}")

        remaining = omitted_count - listed_count
        if remaining:
            lines.append(f"- ... {remaining} additional file(s) not listed")

    return "\n".join(lines)


def _copy_budget_details(details: _BudgetDetails) -> _BudgetDetails:
    return _BudgetDetails(
        included_files=details.included_files,
        omitted_paths=list(details.omitted_paths),
        summarized_files=details.summarized_files,
        git_diff_status=details.git_diff_status,
        project_tree_status=details.project_tree_status,
        errors_status=details.errors_status,
        safety_status=details.safety_status,
    )


def make_display_paths(
    paths: Sequence[PurePath],
    *,
    project_root: str | Path | None = None,
) -> list[str]:
    """Return stable, distinguishable display paths for an output collection.

    Folder and Git modes keep using their explicit project root. Selected Files
    mode derives a shared source root when that root is useful. If files do not
    share a meaningful root (for example, files selected from different drives),
    XCC falls back to the shortest unique path suffixes instead of exposing full
    absolute paths.
    """
    if not paths:
        return []

    if project_root is not None:
        return [make_display_path(Path(path), project_root) for path in paths]

    normalized_paths = [_normalize_display_path(path) for path in paths]

    if len(normalized_paths) == 1:
        return [normalized_paths[0].name]

    common_root = _common_parent(normalized_paths)
    if common_root is not None and not _is_filesystem_root(common_root):
        relative_paths = [
            path.relative_to(common_root).as_posix()
            for path in normalized_paths
        ]

        if _display_paths_are_unique(relative_paths, normalized_paths):
            return relative_paths

    return _shortest_unique_suffixes(normalized_paths)


def make_display_path(path: Path, project_root: str | Path | None = None) -> str:
    if project_root is None:
        return path.name

    root = Path(project_root)

    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.name



def _normalize_display_path(path: PurePath) -> PurePath:
    if isinstance(path, Path):
        try:
            return path.resolve()
        except OSError:
            return path.absolute()

    return path


def _common_parent(paths: Sequence[PurePath]) -> PurePath | None:
    if not paths:
        return None

    first = paths[0]
    windows_flavor = isinstance(first, PureWindowsPath)

    if any(isinstance(path, PureWindowsPath) != windows_flavor for path in paths):
        return None

    parents = [path.parent for path in paths]
    first_parts = parents[0].parts
    common_length = min(len(parent.parts) for parent in parents)

    for index in range(common_length):
        reference = _comparison_value(first_parts[index], windows_flavor)

        if any(
            _comparison_value(parent.parts[index], windows_flavor) != reference
            for parent in parents[1:]
        ):
            common_length = index
            break

    if common_length == 0:
        return None

    return type(first)(*first_parts[:common_length])


def _is_filesystem_root(path: PurePath) -> bool:
    return path.parent == path


def _display_paths_are_unique(
    display_paths: Sequence[str],
    source_paths: Sequence[PurePath],
) -> bool:
    if not display_paths:
        return True

    windows_flavor = isinstance(source_paths[0], PureWindowsPath)
    keys = [
        _comparison_value(display_path, windows_flavor)
        for display_path in display_paths
    ]
    return len(keys) == len(set(keys))


def _shortest_unique_suffixes(paths: Sequence[PurePath]) -> list[str]:
    components = [_path_components(path) for path in paths]
    depths = [1 for _ in paths]
    include_anchor = [False for _ in paths]
    windows_flavor = isinstance(paths[0], PureWindowsPath)

    while True:
        candidates = [
            _suffix_candidate(
                path,
                parts,
                depth,
                include_path_anchor,
            )
            for path, parts, depth, include_path_anchor in zip(
                paths,
                components,
                depths,
                include_anchor,
                strict=True,
            )
        ]

        groups: dict[str, list[int]] = defaultdict(list)
        for index, candidate in enumerate(candidates):
            groups[_comparison_value(candidate, windows_flavor)].append(index)

        collisions = [indices for indices in groups.values() if len(indices) > 1]
        if not collisions:
            return candidates

        progressed = False

        for indices in collisions:
            for index in indices:
                if depths[index] < len(components[index]):
                    depths[index] += 1
                    progressed = True
                    continue

                anchor = _display_anchor(paths[index])
                if anchor and not include_anchor[index]:
                    include_anchor[index] = True
                    progressed = True

        if not progressed:
            return _disambiguate_identical_candidates(candidates, windows_flavor)


def _path_components(path: PurePath) -> list[str]:
    parts = list(path.parts)

    if path.anchor and parts and parts[0] == path.anchor:
        parts = parts[1:]

    if parts:
        return parts

    return [path.name or "file"]


def _suffix_candidate(
    path: PurePath,
    components: Sequence[str],
    depth: int,
    include_anchor: bool,
) -> str:
    selected = list(components[-depth:])

    if include_anchor:
        anchor = _display_anchor(path)
        if anchor:
            selected.insert(0, anchor)

    return "/".join(selected)


def _display_anchor(path: PurePath) -> str:
    drive = path.drive.replace("\\", "/").strip("/")
    if drive:
        return drive

    return "root" if path.anchor else ""


def _disambiguate_identical_candidates(
    candidates: Sequence[str],
    windows_flavor: bool,
) -> list[str]:
    counts: dict[str, int] = defaultdict(int)
    totals: dict[str, int] = defaultdict(int)

    for candidate in candidates:
        totals[_comparison_value(candidate, windows_flavor)] += 1

    result: list[str] = []
    for candidate in candidates:
        key = _comparison_value(candidate, windows_flavor)
        counts[key] += 1

        if totals[key] == 1:
            result.append(candidate)
        else:
            result.append(f"{candidate} [{counts[key]}]")

    return result


def _comparison_value(value: str, windows_flavor: bool) -> str:
    return value.casefold() if windows_flavor else value




def _format_generated_lines(lines: list[str], *, compact: bool) -> str:
    return _format_generated_text("\n".join(lines), compact=compact)


def _format_generated_text(text: str, *, compact: bool) -> str:
    if compact:
        return compact_generated_text(text).rstrip("\n")

    return text.rstrip("\n")



def _format_safety_warnings(
    warnings: Sequence[SafetyWarning],
    *,
    compact: bool,
) -> str:
    if not warnings:
        return ""

    lines = [
        "# XCC Safety Warnings",
        "",
        *format_warning_lines(
            warnings,
            max_items=_MAX_LISTED_SAFETY_WARNINGS,
        ),
        "",
        "Detection is heuristic and may produce false positives.",
        "Secret values are not displayed in this warning summary.",
    ]
    return _format_generated_lines(lines, compact=compact)


def _format_git_context(context: GitContext, *, compact: bool) -> str:
    sections: list[str] = []

    if context.changes:
        sections.append(
            _format_generated_lines(
                [
                    "# Git Changes",
                    "",
                    *[_format_git_change(change) for change in context.changes],
                ],
                compact=compact,
            )
        )

    if context.staged_diff:
        sections.append(
            _format_preserved_block(
                "# Git Diff — Staged",
                context.staged_diff,
            )
        )

    if context.unstaged_diff:
        sections.append(
            _format_preserved_block(
                "# Git Diff — Unstaged",
                context.unstaged_diff,
            )
        )

    return "\n\n".join(sections)


def _format_git_change(change: GitChange) -> str:
    return f"- [{change.status_code}] {change.display_path}"

def _format_preserved_block(title: str, content: str | None) -> str:
    if content is None:
        return ""

    # Git diff is externally produced source-like data and must not be
    # compacted. Framing is added without changing its internal contents.
    return f"{title}\n\n{content}"
