from pathlib import Path
import subprocess

from src.xcc.git_utils import get_changed_files, get_git_diff, is_git_repository


def test_detects_git_repository(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()

    (repo / ".git").mkdir()

    assert is_git_repository(repo) is True


def test_detects_non_git_repository(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()

    assert is_git_repository(repo) is False

def test_get_changed_files_returns_empty_for_clean_repo(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()

    assert get_changed_files(repo) == []

def test_get_changed_files_returns_modified_file(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()

    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=repo, check=True)

    file_path = repo / "main.py"
    file_path.write_text("print('v1')\n", encoding="utf-8")

    subprocess.run(["git", "add", "."], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-m", "initial"], cwd=repo, check=True, capture_output=True)

    file_path.write_text("print('v2')\n", encoding="utf-8")

    changed_files = get_changed_files(repo)

    assert changed_files == [file_path]

def test_get_changed_files_filters_unsupported_files(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()

    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=repo, check=True)

    py_file = repo / "main.py"
    exe_file = repo / "app.exe"

    py_file.write_text("print('hello')\n", encoding="utf-8")
    exe_file.write_text("binary", encoding="utf-8")

    changed_files = get_changed_files(repo)

    assert py_file in changed_files
    assert exe_file not in changed_files


def test_get_git_diff_returns_modified_content(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()

    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=repo, check=True)

    file_path = repo / "main.py"
    file_path.write_text("print('v1')\n", encoding="utf-8")

    subprocess.run(["git", "add", "."], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-m", "initial"], cwd=repo, check=True, capture_output=True)

    file_path.write_text("print('v2')\n", encoding="utf-8")

    diff = get_git_diff(repo)

    assert "diff --git" in diff
    assert "-print('v1')" in diff
    assert "+print('v2')" in diff

def test_get_changed_files_includes_allowed_filename(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()

    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=repo, check=True)

    dockerfile = repo / "Dockerfile"
    dockerfile.write_text("FROM python:3.13\n", encoding="utf-8")

    changed_files = get_changed_files(repo)

    assert dockerfile in changed_files