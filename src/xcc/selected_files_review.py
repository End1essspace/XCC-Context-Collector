from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path

from .formatter import make_display_paths
from .selected_files_importer import infer_project_root


@dataclass(frozen=True, slots=True)
class SelectedFileReviewItem:
    path: Path
    display_path: str
    is_external: bool = False


def build_selected_file_review(
    paths: Sequence[str | Path],
    *,
    project_root: str | Path | None = None,
) -> tuple[SelectedFileReviewItem, ...]:
    normalized = tuple(Path(path) for path in paths)
    if not normalized:
        return ()

    root = _usable_root(normalized, project_root)
    display_paths = make_display_paths(
        normalized,
        project_root=root,
    )

    return tuple(
        SelectedFileReviewItem(
            path=path,
            display_path=display_path,
            is_external=(root is not None and not _is_inside(path, root)),
        )
        for path, display_path in zip(normalized, display_paths, strict=True)
    )


def remove_selected_file_indices(
    paths: Sequence[str | Path],
    indices: Iterable[int],
) -> tuple[Path, ...]:
    normalized = tuple(Path(path) for path in paths)
    removed = {
        index
        for index in indices
        if isinstance(index, int) and 0 <= index < len(normalized)
    }
    return tuple(
        path
        for index, path in enumerate(normalized)
        if index not in removed
    )


def review_project_root(
    paths: Sequence[str | Path],
    *,
    preferred_root: str | Path | None = None,
) -> Path | None:
    normalized = tuple(Path(path) for path in paths)
    if not normalized:
        return None

    root = _usable_root(normalized, preferred_root)
    if root is not None:
        return root

    return infer_project_root(normalized)


def _usable_root(
    paths: Sequence[Path],
    project_root: str | Path | None,
) -> Path | None:
    if project_root is None:
        return None

    root = Path(project_root)
    try:
        resolved_root = root.resolve(strict=False)
    except (OSError, RuntimeError):
        return None

    if all(_is_inside(path, resolved_root) for path in paths):
        return resolved_root

    return None


def _is_inside(path: Path, root: Path) -> bool:
    try:
        path.resolve(strict=False).relative_to(root.resolve(strict=False))
        return True
    except (OSError, RuntimeError, ValueError):
        return False
