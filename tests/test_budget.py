import pytest

from xcc.budget import (
    TRUNCATION_MARKER,
    apply_char_budget,
    minimal_budget_notice,
    take_complete_lines,
)


def test_returns_text_when_under_budget() -> None:
    text = "hello"

    result = apply_char_budget(text, 10)

    assert result == text


def test_line_aware_truncation_stays_within_budget() -> None:
    text = ("complete line\n" * 40) + "unfinished tail"

    result = apply_char_budget(text, 180)

    assert len(result) <= 180
    assert TRUNCATION_MARKER in result


def test_line_aware_truncation_never_keeps_partial_source_line() -> None:
    text = ("alpha   \n" * 40) + "tail-without-newline"

    result = apply_char_budget(text, 180)
    prefix = result.split(TRUNCATION_MARKER, 1)[0].rstrip("\n")

    if prefix:
        assert all(line == "alpha   " for line in prefix.splitlines())
        assert "tail-without-newline" not in prefix


def test_take_complete_lines_preserves_whitespace() -> None:
    text = "first   \nsecond\t \nthird\n"

    result = take_complete_lines(text, len("first   \nsecond\t \n"))

    assert result == "first   \nsecond\t \n"


def test_none_budget_disables_truncation() -> None:
    text = "a" * 100

    result = apply_char_budget(text, None)

    assert result == text


def test_rejects_invalid_budget() -> None:
    with pytest.raises(ValueError):
        apply_char_budget("hello", 0)


def test_minimal_notice_respects_very_small_budget() -> None:
    result = minimal_budget_notice(25)

    assert len(result) == 25
    assert result.startswith("# XCC Context")
