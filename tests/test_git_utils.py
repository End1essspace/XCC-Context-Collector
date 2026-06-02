from pathlib import Path

from src.xcc.git_utils import is_git_repository


def test_detects_git_repository(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()

    (repo / ".git").mkdir()

    assert is_git_repository(repo) is True


def test_detects_non_git_repository(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()

    assert is_git_repository(repo) is False