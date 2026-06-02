from __future__ import annotations


def compact_text(text: str) -> str:
    lines = text.splitlines()

    compacted: list[str] = []
    previous_empty = False

    for line in lines:
        cleaned = line.rstrip()
        is_empty = cleaned == ""

        if is_empty and previous_empty:
            continue

        compacted.append(cleaned)
        previous_empty = is_empty

    return "\n".join(compacted).strip() + "\n"