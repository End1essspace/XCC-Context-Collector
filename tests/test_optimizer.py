from src.xcc.optimizer import compact_text


def test_compact_text_removes_repeated_empty_lines() -> None:
    text = "a\n\n\nb\n\n\nc\n"

    result = compact_text(text)

    assert result == "a\n\nb\n\nc\n"


def test_compact_text_strips_trailing_spaces() -> None:
    text = "a   \n b   \n"

    result = compact_text(text)

    assert result == "a\n b\n"


def test_compact_text_keeps_single_final_newline() -> None:
    text = "a"

    result = compact_text(text)

    assert result == "a\n"