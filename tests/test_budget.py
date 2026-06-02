import pytest

from src.xcc.budget import apply_char_budget


def test_returns_text_when_under_budget() -> None:
    text = "hello"

    result = apply_char_budget(text, 10)

    assert result == text


def test_truncates_text_when_over_budget() -> None:
    text = "a" * 100

    result = apply_char_budget(text, 60)

    assert len(result) <= 60
    assert "XCC Truncated" in result


def test_none_budget_disables_truncation() -> None:
    text = "a" * 100

    result = apply_char_budget(text, None)

    assert result == text


def test_rejects_invalid_budget() -> None:
    with pytest.raises(ValueError):
        apply_char_budget("hello", 0)