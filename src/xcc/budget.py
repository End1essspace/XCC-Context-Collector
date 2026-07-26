from __future__ import annotations


TRUNCATION_MARKER = "__XCC_TRUNCATED_OUTPUT__"


def validate_char_budget(max_chars: int | None) -> None:
    if max_chars is not None and max_chars <= 0:
        raise ValueError("max_chars must be greater than 0")


def join_sections(sections: list[str]) -> str:
    text = "\n\n".join(section for section in sections if section)

    if text and not text.endswith("\n"):
        text += "\n"

    return text


def take_complete_lines(text: str, max_chars: int) -> str:
    """Return the largest prefix made only from complete logical lines."""
    if max_chars <= 0 or not text:
        return ""

    selected: list[str] = []
    used = 0

    for line in text.splitlines(keepends=True):
        if used + len(line) > max_chars:
            break

        selected.append(line)
        used += len(line)

    return "".join(selected)


def minimal_budget_notice(max_chars: int) -> str:
    validate_char_budget(max_chars)

    notice = (
        "# XCC Context\n\n"
        f"{TRUNCATION_MARKER}\n"
        "# XCC Budget Too Small\n\n"
        f"Limit: {max_chars}\n"
        "Increase Max Output Characters to include structured context.\n"
    )

    if len(notice) <= max_chars:
        return notice

    # For extremely small positive limits there is no room for a complete
    # diagnostic. No source payload is present, so a bounded marker prefix is
    # safer than cutting source code or a Git diff.
    return notice[:max_chars]


def apply_char_budget(text: str, max_chars: int | None) -> str:
    """Legacy line-aware budget helper.

    Collection formatting uses the structure-aware planner in formatter.py.
    This helper remains for callers that budget one plain generated block.
    """
    validate_char_budget(max_chars)

    if max_chars is None or len(text) <= max_chars:
        return text

    marker = (
        "\n"
        f"{TRUNCATION_MARKER}\n"
        "# XCC Truncated\n\n"
        f"Output exceeded the {max_chars}-character limit.\n"
        "Only complete lines were retained.\n"
    )

    if len(marker) >= max_chars:
        return minimal_budget_notice(max_chars)

    prefix = take_complete_lines(text, max_chars - len(marker))
    result = prefix + marker

    if len(result) > max_chars:
        return minimal_budget_notice(max_chars)

    return result
