from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from xcc.git_utils import (
    GitCommandError,
    get_changed_files,
    get_collectable_changed_files,
    get_git_changes,
    get_git_context,
    get_git_diff,
    is_git_repository,
    parse_git_status_z,
)


def _run(repo: Path, *args: str) -> None:
    subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        capture_output=True,
    )


def _init_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    _run(repo, "init")
    _run(repo, "config", "user.email", "test@example.com")
    _run(repo, "config", "user.name", "Test User")
    return repo


def _commit_file(repo: Path, relative_path: str, content: str = "v1\n") -> Path:
    file_path = repo / relative_path
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content, encoding="utf-8")
    _run(repo, "add", "--", relative_path)
    _run(repo, "commit", "-m", f"add {relative_path}")
    return file_path


def test_detects_git_repository(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)

    assert is_git_repository(repo) is True


def test_detects_non_git_repository(tmp_path: Path) -> None:
    folder = tmp_path / "folder"
    folder.mkdir()

    assert is_git_repository(folder) is False


def test_clean_repository_is_distinct_from_git_failure(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    _commit_file(repo, "main.py")

    context = get_git_context(repo)

    assert context.changes == []
    assert context.staged_diff == ""
    assert context.unstaged_diff == ""
    assert get_changed_files(repo) == []


def test_git_failure_is_exposed_instead_of_returning_empty(tmp_path: Path) -> None:
    folder = tmp_path / "not-a-repo"
    folder.mkdir()

    with pytest.raises(GitCommandError, match="not a Git repository"):
        get_git_context(folder)


def test_returns_unstaged_modified_file_and_diff(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    file_path = _commit_file(repo, "main.py", "print('v1')\n")
    file_path.write_text("print('v2')\n", encoding="utf-8")

    context = get_git_context(repo)

    assert len(context.changes) == 1
    assert context.changes[0].index_status == " "
    assert context.changes[0].worktree_status == "M"
    assert get_collectable_changed_files(repo, context.changes) == [file_path]
    assert context.staged_diff == ""
    assert "diff --git" in context.unstaged_diff
    assert "-print('v1')" in context.unstaged_diff
    assert "+print('v2')" in context.unstaged_diff


def test_staged_only_change_is_collected_with_cached_diff(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    file_path = _commit_file(repo, "main.py", "print('v1')\n")
    file_path.write_text("print('staged')\n", encoding="utf-8")
    _run(repo, "add", "main.py")

    context = get_git_context(repo)

    assert len(context.changes) == 1
    assert context.changes[0].status_code == "M "
    assert get_changed_files(repo, changes=context.changes) == [file_path]
    assert "diff --git" in context.staged_diff
    assert "+print('staged')" in context.staged_diff
    assert context.unstaged_diff == ""


def test_staged_added_file_is_collected_with_a_status(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    file_path = repo / "new_feature.py"
    file_path.write_text("ENABLED = True\n", encoding="utf-8")
    _run(repo, "add", "new_feature.py")

    context = get_git_context(repo)

    assert len(context.changes) == 1
    assert context.changes[0].status_code == "A "
    assert get_changed_files(repo, changes=context.changes) == [file_path]
    assert "new file mode" in context.staged_diff


def test_mixed_staged_and_unstaged_diffs_are_separate(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    staged = _commit_file(repo, "staged.py", "STAGED = 1\n")
    unstaged = _commit_file(repo, "unstaged.py", "UNSTAGED = 1\n")

    staged.write_text("STAGED = 2\n", encoding="utf-8")
    _run(repo, "add", "staged.py")
    unstaged.write_text("UNSTAGED = 2\n", encoding="utf-8")

    context = get_git_context(repo)

    assert [change.status_code for change in context.changes] == ["M ", " M"]
    assert "staged.py" in context.staged_diff
    assert "unstaged.py" not in context.staged_diff
    assert "unstaged.py" in context.unstaged_diff
    assert "a/staged.py" not in context.unstaged_diff


def test_same_file_can_have_separate_index_and_worktree_changes(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    file_path = _commit_file(repo, "main.py", "VALUE = 1\n")

    file_path.write_text("VALUE = 2\n", encoding="utf-8")
    _run(repo, "add", "main.py")
    file_path.write_text("VALUE = 3\n", encoding="utf-8")

    context = get_git_context(repo)

    assert len(context.changes) == 1
    assert context.changes[0].status_code == "MM"
    assert context.changes[0].has_staged_change is True
    assert context.changes[0].has_unstaged_change is True
    assert get_changed_files(repo, changes=context.changes) == [file_path]
    assert "VALUE = 2" in context.staged_diff
    assert "VALUE = 3" in context.unstaged_diff


def test_untracked_file_is_collected_without_diff(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    file_path = repo / "notes.py"
    file_path.write_text("NOTES = True\n", encoding="utf-8")

    context = get_git_context(repo)

    assert len(context.changes) == 1
    assert context.changes[0].status_code == "??"
    assert context.changes[0].is_untracked is True
    assert get_changed_files(repo, changes=context.changes) == [file_path]
    assert context.staged_diff == ""
    assert context.unstaged_diff == ""


def test_staged_rename_keeps_old_and_new_paths(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    _commit_file(repo, "old.py", "VALUE = 1\n")
    _run(repo, "mv", "old.py", "new.py")

    context = get_git_context(repo)

    assert len(context.changes) == 1
    change = context.changes[0]
    assert change.status_code == "R "
    assert change.original_path == "old.py"
    assert change.path == "new.py"
    assert change.display_path == "old.py -> new.py"
    assert get_changed_files(repo, changes=context.changes) == [repo / "new.py"]
    assert "old.py" in context.staged_diff
    assert "new.py" in context.staged_diff


def test_staged_copy_is_refined_from_added_to_copy(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    source = _commit_file(repo, "source.py", "A = 1\nB = 2\nC = 3\n")
    copy = repo / "copy.py"
    copy.write_bytes(source.read_bytes())
    _run(repo, "add", "copy.py")

    context = get_git_context(repo)

    assert len(context.changes) == 1
    change = context.changes[0]
    assert change.index_status == "C"
    assert change.original_path == "source.py"
    assert change.path == "copy.py"
    assert get_changed_files(repo, changes=context.changes) == [copy]


def test_deleted_file_remains_in_context_without_file_read(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    _commit_file(repo, "obsolete.py", "OLD = True\n")
    _run(repo, "rm", "obsolete.py")

    context = get_git_context(repo)

    assert len(context.changes) == 1
    assert context.changes[0].status_code == "D "
    assert context.changes[0].is_deleted is True
    assert get_changed_files(repo, changes=context.changes) == []
    assert "deleted file mode" in context.staged_diff
    assert "obsolete.py" in context.staged_diff


def test_paths_with_spaces_and_unicode_are_not_quoted_or_split(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    file_path = repo / "папка" / "my file.py"
    file_path.parent.mkdir()
    file_path.write_text("VALUE = 'ok'\n", encoding="utf-8")

    changes = get_git_changes(repo)

    assert len(changes) == 1
    assert changes[0].path == "папка/my file.py"
    assert get_changed_files(repo, changes=changes) == [file_path]


def test_filters_unsupported_files_and_excluded_directories(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    py_file = repo / "main.py"
    exe_file = repo / "app.exe"
    ignored = repo / "build" / "generated.py"
    ignored.parent.mkdir()

    py_file.write_text("print('hello')\n", encoding="utf-8")
    exe_file.write_text("binary", encoding="utf-8")
    ignored.write_text("GENERATED = True\n", encoding="utf-8")

    changes = get_git_changes(repo)

    assert [change.path for change in changes] == ["main.py"]
    assert get_changed_files(repo, changes=changes) == [py_file]


def test_includes_allowed_filename_without_extension(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    dockerfile = repo / "Dockerfile"
    dockerfile.write_text("FROM python:3.13\n", encoding="utf-8")

    changes = get_git_changes(repo)

    assert [change.path for change in changes] == ["Dockerfile"]
    assert get_changed_files(repo, changes=changes) == [dockerfile]


def test_parse_null_delimited_status_supports_rename_copy_and_spaces() -> None:
    data = (
        b"?? notes with spaces.py\0"
        b"R  new.py\0old.py\0"
        b"C  copy.py\0source.py\0"
    )

    changes = parse_git_status_z(data)

    assert [change.status_code for change in changes] == ["??", "R ", "C "]
    assert changes[0].path == "notes with spaces.py"
    assert changes[1].original_path == "old.py"
    assert changes[1].path == "new.py"
    assert changes[2].original_path == "source.py"
    assert changes[2].path == "copy.py"


def test_malformed_null_delimited_status_is_reported() -> None:
    with pytest.raises(GitCommandError, match="incomplete rename/copy"):
        parse_git_status_z(b"R  new.py\0")


def test_backward_compatible_git_diff_has_explicit_sections(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    staged = _commit_file(repo, "staged.py", "A = 1\n")
    unstaged = _commit_file(repo, "unstaged.py", "B = 1\n")
    staged.write_text("A = 2\n", encoding="utf-8")
    _run(repo, "add", "staged.py")
    unstaged.write_text("B = 2\n", encoding="utf-8")

    diff = get_git_diff(repo)

    assert "# Git Diff — Staged" in diff
    assert "# Git Diff — Unstaged" in diff
    assert "staged.py" in diff
    assert "unstaged.py" in diff


def test_git_context_respects_xccignore_for_tracked_changes(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    ignored = _commit_file(repo, "private.py", "VALUE = 1\n")
    (repo / ".xccignore").write_text("private.py\n", encoding="utf-8")
    _run(repo, "add", ".xccignore")
    _run(repo, "commit", "-m", "add xcc ignore")

    ignored.write_text("VALUE = 2\n", encoding="utf-8")

    context = get_git_context(repo)

    assert context.changes == []
    assert context.staged_diff == ""
    assert context.unstaged_diff == ""


def test_git_context_does_not_apply_gitignore_to_tracked_changes(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    tracked = _commit_file(repo, "tracked.py", "VALUE = 1\n")
    (repo / ".gitignore").write_text("tracked.py\n", encoding="utf-8")
    _run(repo, "add", ".gitignore")
    _run(repo, "commit", "-m", "add git ignore")

    tracked.write_text("VALUE = 2\n", encoding="utf-8")

    context = get_git_context(repo)

    assert [change.path for change in context.changes] == ["tracked.py"]


def test_git_rename_into_xccignored_path_is_excluded(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    _commit_file(repo, "visible.py", "VALUE = 1\n")
    (repo / "private").mkdir()
    (repo / ".xccignore").write_text("private/**\n", encoding="utf-8")
    _run(repo, "add", ".xccignore")
    _run(repo, "commit", "-m", "add xcc ignore")

    _run(repo, "mv", "visible.py", "private/visible.py")

    context = get_git_context(repo)

    assert context.changes == []
    assert context.staged_diff == ""
    assert context.unstaged_diff == ""
