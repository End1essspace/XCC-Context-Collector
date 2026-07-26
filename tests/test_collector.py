from pathlib import Path

from src.xcc.collector import collect_files


def test_collects_python_file(tmp_path: Path) -> None:
    file_path = tmp_path / "main.py"
    file_path.write_text("print('hello')\n", encoding="utf-8")

    files, errors = collect_files([file_path])

    assert len(files) == 1
    assert errors == []
    assert files[0].path == file_path
    assert files[0].content == "print('hello')\n"
    assert files[0].line_count == 2
    assert files[0].char_count == len("print('hello')\n")


def test_skips_unsupported_file(tmp_path: Path) -> None:
    file_path = tmp_path / "notes.exe"
    file_path.write_text("hello", encoding="utf-8")

    files, errors = collect_files([file_path])

    assert files == []
    assert len(errors) == 1
    assert "unsupported file type" in errors[0]


def test_summarizes_large_file(tmp_path: Path) -> None:
    file_path = tmp_path / "big.py"
    file_path.write_text("x" * 20, encoding="utf-8")

    files, errors = collect_files([file_path], max_file_size_bytes=10)

    assert len(files) == 1
    assert len(errors) == 1
    assert "Summarized large file" in errors[0]
    assert files[0].path == file_path
    assert "# XCC Large File Summary" in files[0].content
    assert "Full content was not included" in files[0].content
    assert files[0].is_summary is True


def test_reads_cp1251_file(tmp_path: Path) -> None:
    file_path = tmp_path / "ru.py"
    file_path.write_text("print('привет')\n", encoding="cp1251")

    files, errors = collect_files([file_path])

    assert len(files) == 1
    assert errors == []
    assert "привет" in files[0].content

def test_collects_allowed_filename_without_extension(tmp_path: Path) -> None:
    file_path = tmp_path / "Dockerfile"
    file_path.write_text("FROM python:3.13\n", encoding="utf-8")

    files, errors = collect_files([file_path])

    assert len(files) == 1
    assert errors == []
    assert files[0].path == file_path

def test_collection_reports_progress_for_each_input_path(tmp_path: Path) -> None:
    first = tmp_path / "first.py"
    second = tmp_path / "second.py"
    first.write_text("FIRST = True\n", encoding="utf-8")
    second.write_text("SECOND = True\n", encoding="utf-8")
    progress: list[tuple[int, int]] = []

    collect_files(
        [first, second],
        progress_callback=lambda current, total: progress.append((current, total)),
    )

    assert progress == [(1, 2), (2, 2)]
