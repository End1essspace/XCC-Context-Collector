from __future__ import annotations

from pathlib import Path

ATTACHMENTS_PAGE_TITLE = "Attachments"
ATTACHMENTS_PAGE_SUBTITLE = (
    "Prepare original project files for AI handoff and transfer them without conversion."
)


def format_attachment_size(size_bytes: int) -> str:
    value = max(0, int(size_bytes))
    units = ("B", "KB", "MB", "GB", "TB")
    amount = float(value)
    unit = units[0]
    for unit in units:
        if amount < 1024.0 or unit == units[-1]:
            break
        amount /= 1024.0

    if unit == "B":
        return f"{int(amount)} {unit}"
    if amount >= 100:
        number = f"{amount:.0f}"
    elif amount >= 10:
        number = f"{amount:.1f}"
    else:
        number = f"{amount:.2f}"
    if '.' in number:
        number = number.rstrip('0').rstrip('.')
    return f"{number} {unit}"


def attachment_display_path(path: Path, project_root: Path | None) -> str:
    if project_root is not None:
        try:
            return path.resolve(strict=False).relative_to(
                project_root.resolve(strict=False)
            ).as_posix()
        except (OSError, RuntimeError, ValueError):
            pass
    return str(path)
