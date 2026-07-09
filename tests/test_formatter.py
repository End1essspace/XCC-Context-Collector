from pathlib import Path

from src.xcc.formatter import format_collection, make_display_path
from src.xcc.models import FileContent


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