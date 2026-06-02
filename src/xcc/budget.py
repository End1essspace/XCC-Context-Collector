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
        "Some files may be incomplete or missing from the final context.\n"
    )

    available = max_chars - len(marker)

    if available <= 0:
        return (
            "# XCC Truncated\n"
            f"Limit: {max_chars}\n"
        )[:max_chars]

    return text[:available].rstrip() + marker