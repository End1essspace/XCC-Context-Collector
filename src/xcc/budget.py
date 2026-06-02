from __future__ import annotations


def apply_char_budget(text: str, max_chars: int | None) -> str:
    if max_chars is None:
        return text

    if max_chars <= 0:
        raise ValueError("max_chars must be greater than 0")

    if len(text) <= max_chars:
        return text

    marker = (
        "\n\n"
        "# XCC Truncated\n\n"
        f"Output was truncated to {max_chars} characters.\n"
    )

    available = max_chars - len(marker)

    if available <= 0:
        return marker[-max_chars:]

    return text[:available].rstrip() + marker