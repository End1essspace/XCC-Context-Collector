from pathlib import Path

import pytest

from src.xcc.formatter import (
    format_collection,
    format_file,
    format_project_tree,
    make_display_path,
    make_display_paths,
)
from src.xcc.models import (
    CollectionOutcome,
    FileContent,
    GitChange,
    GitContext,
    SafetyWarning,
)


def _file(path: str, content: str) -> FileContent:
    return FileContent(
        path=Path(path),
        content=content,
        line_count=content.count("\n") + (1 if content else 0),
        char_count=len(content),
    )


def test_formats_collection_with_stats() -> None:
    file = FileContent(
        path=Path("main.py"),
        content="print('hello')\n",
        line_count=1,
        char_count=15,
    )

    result = format_collection([file])

    assert "# XCC Context" in result.text
    assert "XCC Version:" in result.text
    assert "Mode: Compact" in result.text
    assert "Max Output Characters:" in result.text
    assert "Files: 1" in result.text
    assert "Lines: 1" in result.text
    assert "Characters: 15" in result.text
    assert "===== file: main.py =====" in result.text
    assert "print('hello')" in result.text


def test_formats_collection_with_custom_mode_name() -> None:
    file = FileContent(
        path=Path("main.py"),
        content="print('hello')\n",
        line_count=1,
        char_count=15,
    )

    result = format_collection([file], mode_name="Git Changed Files")

    assert "Mode: Git Changed Files" in result.text


def test_formats_errors() -> None:
    result = format_collection([], ["Cannot decode file: bad.py"])

    assert "# XCC Errors" in result.text
    assert "- Cannot decode file: bad.py" in result.text
    assert result.errors == ["Cannot decode file: bad.py"]
    assert result.stats.error_count == 1
    assert result.stats.warning_count == 0
    assert result.outcome == CollectionOutcome.SUCCESS_WITH_WARNINGS


def test_make_display_path_relative_to_project_root(tmp_path: Path) -> None:
    root = tmp_path / "project"
    file_path = root / "src" / "main.py"
    file_path.parent.mkdir(parents=True)
    file_path.write_text("print('hello')", encoding="utf-8")

    display_path = make_display_path(file_path, root)

    assert display_path == "src/main.py"


def test_can_disable_project_tree_for_selected_files() -> None:
    file = FileContent(
        path=Path("src/main.py"),
        content="print('hello')\n",
        line_count=1,
        char_count=15,
    )

    result = format_collection(
        [file],
        mode_name="Selected Files",
        include_project_tree=False,
    )

    assert "Mode: Selected Files" in result.text
    assert "# Project Tree" not in result.text
    assert "# Files" in result.text
    assert "===== file: main.py =====" in result.text
    assert "print('hello')" in result.text


def test_formats_project_tree_without_file_contents(tmp_path: Path) -> None:
    root = tmp_path / "project"
    src = root / "src"
    src.mkdir(parents=True)

    file_path = src / "main.py"
    file_path.write_text("print('secret content')\n", encoding="utf-8")

    result = format_project_tree(root, compact=False)

    assert "# XCC Context" in result.text
    assert "Mode: Project Tree" in result.text
    assert "# Project Tree" in result.text
    assert "src/" in result.text
    assert "src/main.py" in result.text
    assert "# Files" not in result.text
    assert "===== file:" not in result.text
    assert "secret content" not in result.text
    assert "Files: 1" in result.text
    assert "Directories: 1" in result.text
    assert result.stats.included_files == 1
    assert result.stats.omitted_files == 0


def test_format_file_preserves_repeated_blank_lines() -> None:
    content = 'value = """first\n\n\nsecond"""\n'
    file = _file("main.py", content)

    section = format_file(file)

    assert section == f"===== file: main.py =====\n\n{content}"


def test_format_file_preserves_trailing_spaces() -> None:
    content = "first   \nsecond\t \n"
    file = _file("notes.md", content)

    section = format_file(file)

    assert section == f"===== file: notes.md =====\n\n{content}"


def test_format_file_preserves_final_blank_lines() -> None:
    content = "print('done')\n\n\n"
    file = _file("main.py", content)

    section = format_file(file)

    assert section.endswith(content)
    assert section == f"===== file: main.py =====\n\n{content}"


def test_compact_collection_preserves_python_multiline_string() -> None:
    content = 'TEMPLATE = """alpha\n\n\nbeta   \n"""\n'
    file = _file("template.py", content)

    result = format_collection(
        [file],
        compact=True,
        max_output_chars=None,
        include_project_tree=False,
    )

    assert f"===== file: template.py =====\n\n{content}" in result.text


def test_compact_collection_preserves_markdown_whitespace() -> None:
    content = "# Title\n\n\nParagraph with hard break.  \nNext line.\n\n"
    file = _file("README.md", content)

    result = format_collection(
        [file],
        compact=True,
        max_output_chars=None,
        include_project_tree=False,
    )

    assert f"===== file: README.md =====\n\n{content}" in result.text


def test_compact_collection_preserves_yaml_block_content() -> None:
    content = "message: |+\n  first\n\n\n  second  \n\n"
    file = _file("config.yaml", content)

    result = format_collection(
        [file],
        compact=True,
        max_output_chars=None,
        include_project_tree=False,
    )

    assert f"===== file: config.yaml =====\n\n{content}" in result.text


def test_compact_and_non_compact_modes_preserve_identical_source_payload() -> None:
    content = "first   \n\n\nsecond\n\n"
    file = _file("sample.txt", content)
    expected_section = f"===== file: sample.txt =====\n\n{content}"

    compact_result = format_collection(
        [file],
        compact=True,
        max_output_chars=None,
        include_project_tree=False,
    )
    expanded_result = format_collection(
        [file],
        compact=False,
        max_output_chars=None,
        include_project_tree=False,
    )

    assert expected_section in compact_result.text
    assert expected_section in expanded_result.text


def test_git_diff_is_not_compacted() -> None:
    git_diff = "diff --git a/a.py b/a.py\n+line with spaces   \n\n\n"
    result = format_collection(
        [],
        compact=True,
        max_output_chars=None,
        git_diff=git_diff,
        include_project_tree=False,
    )

    assert f"# Git Diff\n\n{git_diff}" in result.text


def test_selected_files_preserve_paths_relative_to_common_root(tmp_path: Path) -> None:
    root = tmp_path / "project"
    backend = root / "backend" / "app.py"
    frontend = root / "frontend" / "view.ts"
    backend.parent.mkdir(parents=True)
    frontend.parent.mkdir(parents=True)
    backend.write_text("print('backend')\n", encoding="utf-8")
    frontend.write_text("export const view = true;\n", encoding="utf-8")

    result = format_collection(
        [
            _file(str(backend), "print('backend')\n"),
            _file(str(frontend), "export const view = true;\n"),
        ],
        mode_name="Selected Files",
        include_project_tree=False,
        max_output_chars=None,
    )

    assert "===== file: backend/app.py =====" in result.text
    assert "===== file: frontend/view.ts =====" in result.text
    assert str(tmp_path) not in result.text


def test_selected_files_with_duplicate_names_receive_distinct_paths(tmp_path: Path) -> None:
    root = tmp_path / "project"
    backend = root / "backend" / "config.py"
    frontend = root / "frontend" / "config.py"
    backend.parent.mkdir(parents=True)
    frontend.parent.mkdir(parents=True)
    backend.write_text("BACKEND = True\n", encoding="utf-8")
    frontend.write_text("FRONTEND = True\n", encoding="utf-8")

    result = format_collection(
        [
            _file(str(backend), "BACKEND = True\n"),
            _file(str(frontend), "FRONTEND = True\n"),
        ],
        mode_name="Selected Files",
        include_project_tree=False,
        max_output_chars=None,
    )

    assert result.text.count("===== file: backend/config.py =====") == 1
    assert result.text.count("===== file: frontend/config.py =====") == 1
    assert "===== file: config.py =====" not in result.text


def test_selected_files_from_cross_root_paths_use_shortest_unique_suffixes() -> None:
    from pathlib import PurePosixPath

    paths = [
        PurePosixPath("/opt/team_a/config.py"),
        PurePosixPath("/srv/team_b/config.py"),
    ]

    display_paths = make_display_paths(paths)

    assert display_paths == ["team_a/config.py", "team_b/config.py"]
    assert all(not path.startswith("/") for path in display_paths)


def test_selected_files_from_different_drives_use_drive_only_when_required() -> None:
    from pathlib import PureWindowsPath

    paths = [
        PureWindowsPath("C:/work/config.py"),
        PureWindowsPath("D:/work/config.py"),
    ]

    display_paths = make_display_paths(paths)

    assert display_paths == ["C:/work/config.py", "D:/work/config.py"]


def test_selected_windows_paths_use_forward_slashes() -> None:
    from pathlib import PureWindowsPath

    paths = [
        PureWindowsPath("C:/work/project/src/main.py"),
        PureWindowsPath("C:/work/project/tests/test_main.py"),
    ]

    display_paths = make_display_paths(paths)

    assert display_paths == ["src/main.py", "tests/test_main.py"]
    assert all("\\" not in path for path in display_paths)


def test_selected_files_preserve_non_ascii_directory_names(tmp_path: Path) -> None:
    root = tmp_path / "проект"
    server = root / "сервер" / "config.py"
    client = root / "клиент" / "config.py"
    server.parent.mkdir(parents=True)
    client.parent.mkdir(parents=True)
    server.write_text("SERVER = True\n", encoding="utf-8")
    client.write_text("CLIENT = True\n", encoding="utf-8")

    display_paths = make_display_paths([server, client])

    assert display_paths == ["сервер/config.py", "клиент/config.py"]


def test_single_selected_file_keeps_filename_only(tmp_path: Path) -> None:
    file_path = tmp_path / "private" / "nested" / "main.py"
    file_path.parent.mkdir(parents=True)
    file_path.write_text("print('hello')\n", encoding="utf-8")

    display_paths = make_display_paths([file_path])

    assert display_paths == ["main.py"]


def test_exact_boundary_budget_keeps_full_output() -> None:
    files = [
        _file("src/a.py", "A = 1\n"),
        _file("src/b.py", "B = 2\n"),
    ]

    limit = 1_000
    for _ in range(10):
        candidate = format_collection(
            files,
            include_project_tree=False,
            max_output_chars=limit,
        )
        next_limit = len(candidate.text)
        if next_limit == limit:
            break
        limit = next_limit

    result = format_collection(
        files,
        include_project_tree=False,
        max_output_chars=limit,
    )

    assert len(result.text) == limit
    assert result.was_truncated is False
    assert "# XCC Budget Summary" not in result.text
    assert result.stats.included_files == 2
    assert result.stats.omitted_files == 0
    assert result.stats.output_chars == len(result.text)


def test_structure_aware_budget_keeps_only_complete_file_sections() -> None:
    files = [
        _file("src/a.py", "a" * 100 + "\n"),
        _file("src/b.py", "b" * 100 + "\n"),
        _file("src/c.py", "c" * 100 + "\n"),
    ]

    result = format_collection(
        files,
        include_project_tree=False,
        max_output_chars=460,
    )

    assert len(result.text) <= 460
    assert result.was_truncated is True
    assert "===== file: a.py =====\n\n" + ("a" * 100) + "\n" in result.text
    assert "===== file: b.py =====" not in result.text
    assert "===== file: c.py =====" not in result.text
    assert ("b" * 25) not in result.text
    assert ("c" * 25) not in result.text
    assert result.stats.included_files == 1
    assert result.stats.omitted_files == 2
    assert result.stats.partial_files == 0
    assert result.omitted_paths == ["b.py", "c.py"]


def test_budget_summary_lists_omitted_files_in_deterministic_order() -> None:
    files = [
        _file("src/first.py", "1" * 100 + "\n"),
        _file("src/second.py", "2" * 100 + "\n"),
        _file("src/third.py", "3" * 100 + "\n"),
    ]

    result = format_collection(
        files,
        include_project_tree=False,
        max_output_chars=470,
    )

    second_index = result.text.index("- second.py")
    third_index = result.text.index("- third.py")

    assert second_index < third_index
    assert result.omitted_paths == ["second.py", "third.py"]


def test_budget_summary_used_value_matches_final_output_length() -> None:
    files = [
        _file("src/a.py", "a" * 100 + "\n"),
        _file("src/b.py", "b" * 100 + "\n"),
        _file("src/c.py", "c" * 100 + "\n"),
    ]

    result = format_collection(
        files,
        include_project_tree=False,
        max_output_chars=460,
    )

    assert f"Used: {len(result.text)}" in result.text
    assert result.stats.output_chars == len(result.text)
    assert result.stats.budget_limit == 460


def test_budget_stats_distinguish_large_file_summaries() -> None:
    summary = FileContent(
        path=Path("src/generated.py"),
        content="# XCC Large File Summary\n",
        line_count=0,
        char_count=0,
        is_summary=True,
    )
    normal = _file("src/main.py", "print('ok')\n")

    result = format_collection(
        [summary, normal],
        include_project_tree=False,
        max_output_chars=None,
    )

    assert result.stats.included_files == 2
    assert result.stats.summarized_files == 1
    assert result.stats.omitted_files == 0


def test_large_git_diff_is_omitted_instead_of_cut_mid_line() -> None:
    git_diff = "".join(
        f"+complete diff line {index:03d}\\n"
        for index in range(100)
    )
    file = _file("src/main.py", "print('ok')\n")

    result = format_collection(
        [file],
        git_diff=git_diff,
        include_project_tree=False,
        max_output_chars=430,
    )

    assert len(result.text) <= 430
    assert "Git diff: omitted" in result.text
    assert "+complete diff line" not in result.text
    assert "===== file: main.py =====" in result.text


def test_project_tree_budget_keeps_complete_tree_lines(tmp_path: Path) -> None:
    root = tmp_path / "project"

    for index in range(50):
        file_path = root / "src" / f"module_{index:02d}.py"
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text("x = 1\n", encoding="utf-8")

    result = format_project_tree(
        root,
        max_output_chars=450,
    )

    assert len(result.text) <= 450
    assert result.was_truncated is True
    assert "Project tree: partial" in result.text
    assert result.stats.included_files < 50
    assert result.stats.omitted_files > 0
    assert result.stats.included_files + result.stats.omitted_files == 50

    for line in result.text.splitlines():
        if line.startswith("src/"):
            assert line.endswith("/") or line.endswith(".py")


@pytest.mark.parametrize("limit", [1, 10, 50, 100, 250, 400, 460])
def test_collection_output_never_exceeds_configured_limit(limit: int) -> None:
    files = [
        _file("src/a.py", "a" * 200 + "\n"),
        _file("src/b.py", "b" * 200 + "\n"),
    ]

    result = format_collection(
        files,
        include_project_tree=False,
        max_output_chars=limit,
    )

    assert len(result.text) <= limit


def test_formats_typed_git_context_with_separate_status_and_diffs() -> None:
    context = GitContext(
        changes=[
            GitChange("M", " ", "src/staged.py"),
            GitChange(" ", "M", "src/unstaged.py"),
            GitChange("R", " ", "src/new.py", "src/old.py"),
            GitChange("?", "?", "notes with spaces.py"),
        ],
        staged_diff="diff --git a/src/staged.py b/src/staged.py\n+STAGED = True\n",
        unstaged_diff="diff --git a/src/unstaged.py b/src/unstaged.py\n+UNSTAGED = True\n",
    )

    result = format_collection(
        [],
        git_context=context,
        include_project_tree=False,
        max_output_chars=None,
    )

    assert "# Git Changes" in result.text
    assert "- [M ] src/staged.py" in result.text
    assert "- [ M] src/unstaged.py" in result.text
    assert "- [R ] src/old.py -> src/new.py" in result.text
    assert "- [??] notes with spaces.py" in result.text
    assert "# Git Diff — Staged" in result.text
    assert "+STAGED = True" in result.text
    assert "# Git Diff — Unstaged" in result.text
    assert "+UNSTAGED = True" in result.text


def test_deleted_only_git_context_does_not_require_file_sections() -> None:
    context = GitContext(
        changes=[GitChange("D", " ", "obsolete.py")],
        staged_diff=(
            "diff --git a/obsolete.py b/obsolete.py\n"
            "deleted file mode 100644\n"
        ),
    )

    result = format_collection(
        [],
        git_context=context,
        include_project_tree=False,
        max_output_chars=None,
    )

    assert "- [D ] obsolete.py" in result.text
    assert "deleted file mode" in result.text
    assert "# Files" not in result.text
    assert result.stats.files == 0


def test_large_typed_git_context_is_omitted_as_one_budget_section() -> None:
    context = GitContext(
        changes=[GitChange("M", " ", "src/main.py")],
        staged_diff="".join(
            f"+complete staged line {index:03d}\n"
            for index in range(100)
        ),
    )
    file = _file("src/main.py", "print('ok')\n")

    result = format_collection(
        [file],
        git_context=context,
        include_project_tree=False,
        max_output_chars=430,
    )

    assert len(result.text) <= 430
    assert "Git diff: omitted" in result.text
    assert "+complete staged line" not in result.text
    assert "===== file: main.py =====" in result.text


def test_git_change_status_preserves_index_and_worktree_columns() -> None:
    context = GitContext(
        changes=[GitChange("M", "M", "src/main.py")],
    )

    result = format_collection(
        [],
        git_context=context,
        include_project_tree=False,
        max_output_chars=None,
    )

    assert "- [MM] src/main.py" in result.text


def test_formats_safety_warnings_without_secret_values() -> None:
    file = _file("settings.py", 'password = "supersecret123"\n')
    warning = SafetyWarning(
        path="settings.py",
        line_number=1,
        category="Credential assignment",
    )

    result = format_collection(
        [file],
        warnings=[warning],
        include_project_tree=False,
        max_output_chars=None,
    )

    assert "# XCC Safety Warnings" in result.text
    assert "settings.py:1 — Credential assignment" in result.text
    assert "supersecret123" in result.text
    warning_section = result.text.split("# XCC Safety Warnings", 1)[1].split("# Files", 1)[0]
    assert "supersecret123" not in warning_section
    assert result.stats.warning_count == 1
    assert result.stats.error_count == 0
    assert result.outcome == CollectionOutcome.SUCCESS_WITH_WARNINGS
    assert result.warnings == [warning]


def test_budget_prioritizes_safety_warning_section() -> None:
    files = [
        _file("src/a.py", "a" * 300 + "\n"),
        _file("src/b.py", "b" * 300 + "\n"),
    ]
    warning = SafetyWarning(
        path="src/a.py",
        line_number=1,
        category="API token or access key",
    )

    result = format_collection(
        files,
        warnings=[warning],
        include_project_tree=False,
        max_output_chars=520,
    )

    assert len(result.text) <= 520
    assert "# XCC Safety Warnings" in result.text
    assert "Safety warnings: included" in result.text
