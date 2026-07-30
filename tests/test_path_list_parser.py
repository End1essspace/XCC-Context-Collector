from __future__ import annotations

from xcc.path_list_parser import (
    contains_relative_paths,
    is_absolute_path_text,
    parse_path_list,
)


def test_parse_path_list_handles_plain_ai_file_list() -> None:
    text = """
    src/cagex_desktop/ui/pages/flow_page.py
    src/cagex_desktop/ui/main_window.py

    AI_PROJECT_CONTEXT.md
    docs/CAGEX_DESKTOP_ROADMAP.md
    """

    assert parse_path_list(text) == [
        "src/cagex_desktop/ui/pages/flow_page.py",
        "src/cagex_desktop/ui/main_window.py",
        "AI_PROJECT_CONTEXT.md",
        "docs/CAGEX_DESKTOP_ROADMAP.md",
    ]


def test_parse_path_list_prefers_fenced_blocks_over_surrounding_prose() -> None:
    text = """
    Пришли эти файлы из CAGE-X Desktop:

    ```text
    src/app.py
    tests/test_app.py
    ```

    После этого продолжим реализацию.
    """

    assert parse_path_list(text) == ["src/app.py", "tests/test_app.py"]


def test_parse_path_list_removes_markdown_bullets_numbers_and_wrappers() -> None:
    text = """
    - `src/app.py`
    * "src/theme.py"
    1. 'tests/test_app.py'
    2) docs/guide.md,
    """

    assert parse_path_list(text) == [
        "src/app.py",
        "src/theme.py",
        "tests/test_app.py",
        "docs/guide.md",
    ]


def test_parse_path_list_preserves_paths_with_spaces() -> None:
    assert parse_path_list("src/legacy files/old adapter.py") == [
        "src/legacy files/old adapter.py"
    ]


def test_parse_path_list_deduplicates_mixed_separator_and_case_variants() -> None:
    text = "src/App.py\nsrc\\app.py\n"

    assert parse_path_list(text) == ["src/App.py"]


def test_parse_path_list_rejects_globs_urls_headings_and_plain_prose() -> None:
    text = """
    # Files
    src/**/*.py
    https://example.com/file.py
    Пришли эти файлы из проекта
    src/app.py
    """

    assert parse_path_list(text) == ["src/app.py"]


def test_absolute_path_detection_supports_windows_unc_and_posix() -> None:
    assert is_absolute_path_text(r"D:\projects\xcc\src\app.py") is True
    assert is_absolute_path_text(r"\\server\share\src\app.py") is True
    assert is_absolute_path_text("/tmp/project/src/app.py") is True
    assert is_absolute_path_text("src/app.py") is False


def test_contains_relative_paths() -> None:
    assert contains_relative_paths(["src/app.py"]) is True
    assert contains_relative_paths([r"D:\project\src\app.py"]) is False

def test_parse_path_list_handles_grouped_ai_request_from_real_workflow() -> None:
    text = """
    Пришли эти файлы из CAGE-X Desktop:

    ```text
    src/cagex_desktop/ui/pages/flow_page.py
    src/cagex_desktop/ui/main_window.py
    src/cagex_desktop/ui/theme.py
    src/cagex_desktop/ui/icon_catalog.py

    src/cagex_desktop/core_bridge/adapter.py
    src/cagex_desktop/core_bridge/engine_service.py

    src/cagex_desktop/models/product_state.py

    AI_PROJECT_CONTEXT.md
    docs/CAGEX_DESKTOP_ROADMAP.md
    ```
    """

    assert parse_path_list(text) == [
        "src/cagex_desktop/ui/pages/flow_page.py",
        "src/cagex_desktop/ui/main_window.py",
        "src/cagex_desktop/ui/theme.py",
        "src/cagex_desktop/ui/icon_catalog.py",
        "src/cagex_desktop/core_bridge/adapter.py",
        "src/cagex_desktop/core_bridge/engine_service.py",
        "src/cagex_desktop/models/product_state.py",
        "AI_PROJECT_CONTEXT.md",
        "docs/CAGEX_DESKTOP_ROADMAP.md",
    ]

