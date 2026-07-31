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
