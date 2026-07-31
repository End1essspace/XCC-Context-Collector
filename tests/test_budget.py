import pytest

from xcc.budget import (
    TRUNCATION_MARKER,
    join_sections,
    minimal_budget_notice,
    validate_char_budget,
)


def test_join_sections_omits_empty_sections_and_adds_one_final_newline() -> None:
    result = join_sections(["# Header", "", "Body\n"])

    assert result == "# Header\n\nBody\n"


@pytest.mark.parametrize("value", [1, 120_000, None])
def test_validate_char_budget_accepts_supported_values(value: int | None) -> None:
    validate_char_budget(value)


@pytest.mark.parametrize("value", [0, -1])
def test_validate_char_budget_rejects_non_positive_limits(value: int) -> None:
    with pytest.raises(ValueError):
        validate_char_budget(value)


def test_minimal_notice_respects_very_small_budget() -> None:
    result = minimal_budget_notice(25)

    assert len(result) == 25
    assert result.startswith("# XCC Context")


def test_minimal_notice_includes_explicit_marker_when_budget_allows() -> None:
    result = minimal_budget_notice(220)

    assert TRUNCATION_MARKER in result
    assert "# XCC Budget Too Small" in result
    assert len(result) <= 220
