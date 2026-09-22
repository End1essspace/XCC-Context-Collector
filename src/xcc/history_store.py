from __future__ import annotations

import json
import os
import re
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any, Iterable

from .models import AttachmentTransferRecord, CollectionOutcome, CollectionRunRecord

HISTORY_SCHEMA_VERSION = 1
HISTORY_MAX_RECORDS = 200
HISTORY_FILE_NAME = "history.json"
HistoryRecord = CollectionRunRecord | AttachmentTransferRecord


@dataclass(frozen=True, slots=True)
class HistoryLoadResult:
    records: tuple[HistoryRecord, ...]
    recovered_from_error: bool = False
    message: str = ""
    backup_path: Path | None = None
    dropped_records: int = 0


def default_history_path() -> Path:
    return Path.home() / ".xcc" / HISTORY_FILE_NAME


def sanitize_collection_source(source: str, mode_name: str = "") -> str:
    """Return a persistence-safe source label without private absolute paths."""

    value = str(source or "").strip()
    if not value:
        return "Unknown source"

    if _looks_absolute_path(value):
        lowered = mode_name.casefold()
        if "git" in lowered:
            return "Git repository"
        if "tree" in lowered:
            return "Project tree"
        return "Project folder"

    # Defensive fallback: path-shaped relative strings are not useful enough to
    # justify persisting. Normal generated labels such as "8 selected files"
    # remain intact.
    if "/" in value or "\\" in value:
        return "Project source"

    return value[:160]


def sanitize_history_record(record: HistoryRecord) -> HistoryRecord:
    if isinstance(record, CollectionRunRecord):
        return CollectionRunRecord(
            timestamp=_sanitize_timestamp(record.timestamp),
            mode_name=str(record.mode_name)[:80],
            source=sanitize_collection_source(record.source, record.mode_name),
            outcome=record.outcome,
            duration_seconds=max(0.0, float(record.duration_seconds)),
            files=max(0, int(record.files)),
            lines=max(0, int(record.lines)),
            source_chars=max(0, int(record.source_chars)),
            output_chars=max(0, int(record.output_chars)),
            output_tokens=max(0, int(record.output_tokens)),
            included_files=max(0, int(record.included_files)),
            omitted_files=max(0, int(record.omitted_files)),
            summarized_files=max(0, int(record.summarized_files)),
            partial_files=max(0, int(record.partial_files)),
            truncated=bool(record.truncated),
            warning_count=max(0, int(record.warning_count)),
            error_count=max(0, int(record.error_count)),
        )

    return AttachmentTransferRecord(
        timestamp=_sanitize_timestamp(record.timestamp),
        transfer_type=str(record.transfer_type)[:80],
        outcome=str(record.outcome)[:40],
        file_count=max(0, int(record.file_count)),
        total_bytes=max(0, int(record.total_bytes)),
        duration_seconds=max(0.0, float(record.duration_seconds)),
        warning_count=max(0, int(record.warning_count)),
        bundle_name=_sanitize_bundle_name(record.bundle_name),
    )


def load_history(
    path: str | Path | None = None,
    *,
    max_records: int = HISTORY_MAX_RECORDS,
) -> HistoryLoadResult:
    history_path = Path(path) if path is not None else default_history_path()
    if not history_path.exists():
        return HistoryLoadResult(())

    try:
        raw = json.loads(history_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        backup = _backup_corrupt_history(history_path)
        return HistoryLoadResult(
            (),
            recovered_from_error=True,
            message=f"History was unreadable and has been reset: {exc}",
            backup_path=backup,
        )

    if not isinstance(raw, dict) or raw.get("schema_version") != HISTORY_SCHEMA_VERSION:
        backup = _backup_corrupt_history(history_path)
        return HistoryLoadResult(
            (),
            recovered_from_error=True,
            message="History format was invalid or unsupported and has been reset.",
            backup_path=backup,
        )

    raw_records = raw.get("records")
    if not isinstance(raw_records, list):
        backup = _backup_corrupt_history(history_path)
        return HistoryLoadResult(
            (),
            recovered_from_error=True,
            message="History records were invalid and have been reset.",
            backup_path=backup,
        )

    records: list[HistoryRecord] = []
    dropped = 0
    for item in raw_records:
        try:
            records.append(_record_from_json(item))
        except (KeyError, TypeError, ValueError):
            dropped += 1

    records = records[: max(0, int(max_records))]
    if dropped:
        return HistoryLoadResult(
            tuple(records),
            recovered_from_error=True,
            message=(
                f"History recovered with {dropped} invalid record"
                f"{'s' if dropped != 1 else ''} skipped."
            ),
            dropped_records=dropped,
        )
    return HistoryLoadResult(tuple(records))


def save_history(
    records: Iterable[HistoryRecord],
    path: str | Path | None = None,
    *,
    max_records: int = HISTORY_MAX_RECORDS,
) -> tuple[HistoryRecord, ...]:
    history_path = Path(path) if path is not None else default_history_path()
    sanitized = tuple(
        sanitize_history_record(record)
        for record in list(records)[: max(0, int(max_records))]
    )
    payload = _history_document(sanitized)
    _atomic_write_json(history_path, payload)
    return sanitized


def export_history_json(
    records: Iterable[HistoryRecord],
    destination: str | Path,
    *,
    max_records: int = HISTORY_MAX_RECORDS,
) -> Path:
    target = Path(destination)
    sanitized = tuple(
        sanitize_history_record(record)
        for record in list(records)[: max(0, int(max_records))]
    )
    payload = _history_document(sanitized)
    _atomic_write_json(target, payload)
    return target


def history_timestamp_for_display(value: str) -> str:
    text = str(value or "").strip()
    if not text:
        return "Unknown time"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return text
    return parsed.strftime("%Y-%m-%d %H:%M:%S")


def _history_document(records: tuple[HistoryRecord, ...]) -> dict[str, Any]:
    return {
        "schema_version": HISTORY_SCHEMA_VERSION,
        "format": "xcc-runtime-history",
        "privacy": "metadata-only",
        "records": [_record_to_json(record) for record in records],
    }


def _record_to_json(record: HistoryRecord) -> dict[str, Any]:
    safe = sanitize_history_record(record)
    if isinstance(safe, CollectionRunRecord):
        data = asdict(safe)
        data["outcome"] = safe.outcome.value
        return {"type": "collection", **data}
    return {"type": "attachment", **asdict(safe)}


def _record_from_json(raw: Any) -> HistoryRecord:
    if not isinstance(raw, dict):
        raise TypeError("history record must be an object")
    record_type = raw.get("type")
    if record_type == "collection":
        record = CollectionRunRecord(
            timestamp=_required_str(raw, "timestamp"),
            mode_name=_required_str(raw, "mode_name"),
            source=_required_str(raw, "source"),
            outcome=CollectionOutcome(_required_str(raw, "outcome")),
            duration_seconds=_non_negative_float(raw.get("duration_seconds", 0.0)),
            files=_non_negative_int(raw.get("files", 0)),
            lines=_non_negative_int(raw.get("lines", 0)),
            source_chars=_non_negative_int(raw.get("source_chars", 0)),
            output_chars=_non_negative_int(raw.get("output_chars", 0)),
            output_tokens=_non_negative_int(raw.get("output_tokens", 0)),
            included_files=_non_negative_int(raw.get("included_files", 0)),
            omitted_files=_non_negative_int(raw.get("omitted_files", 0)),
            summarized_files=_non_negative_int(raw.get("summarized_files", 0)),
            partial_files=_non_negative_int(raw.get("partial_files", 0)),
            truncated=_required_bool(raw.get("truncated", False)),
            warning_count=_non_negative_int(raw.get("warning_count", 0)),
            error_count=_non_negative_int(raw.get("error_count", 0)),
        )
        return sanitize_history_record(record)

    if record_type == "attachment":
        record = AttachmentTransferRecord(
            timestamp=_required_str(raw, "timestamp"),
            transfer_type=_required_str(raw, "transfer_type"),
            outcome=_required_str(raw, "outcome"),
            file_count=_non_negative_int(raw.get("file_count", 0)),
            total_bytes=_non_negative_int(raw.get("total_bytes", 0)),
            duration_seconds=_non_negative_float(raw.get("duration_seconds", 0.0)),
            warning_count=_non_negative_int(raw.get("warning_count", 0)),
            bundle_name=_optional_str(raw.get("bundle_name")),
        )
        return sanitize_history_record(record)

    raise ValueError("unsupported history record type")


def _atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    try:
        temp.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        os.replace(temp, path)
    finally:
        try:
            temp.unlink(missing_ok=True)
        except OSError:
            pass


def _backup_corrupt_history(path: Path) -> Path | None:
    if not path.exists():
        return None
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    candidate = path.with_name(f"history.corrupt-{stamp}.json")
    counter = 1
    while candidate.exists():
        candidate = path.with_name(f"history.corrupt-{stamp}-{counter:02d}.json")
        counter += 1
    try:
        os.replace(path, candidate)
    except OSError:
        return None
    return candidate


def _looks_absolute_path(value: str) -> bool:
    if (
        Path(value).is_absolute()
        or PureWindowsPath(value).is_absolute()
        or PurePosixPath(value).is_absolute()
    ):
        return True
    return bool(re.match(r"^[A-Za-z]:[\\/]", value)) or value.startswith("\\\\")


def _sanitize_bundle_name(value: str | None) -> str | None:
    if not value:
        return None
    name = PureWindowsPath(str(value)).name or Path(str(value)).name
    return name[:180] if name else None


def _sanitize_timestamp(value: str) -> str:
    text = str(value or "").strip()
    return text[:64] if text else datetime.now().astimezone().isoformat(timespec="seconds")


def _required_str(raw: dict[str, Any], key: str) -> str:
    value = raw[key]
    if not isinstance(value, str):
        raise TypeError(key)
    return value


def _optional_str(value: Any) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise TypeError("optional string")
    return value


def _required_bool(value: Any) -> bool:
    if not isinstance(value, bool):
        raise TypeError("boolean")
    return value


def _non_negative_int(value: Any) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise TypeError("non-negative integer")
    return value


def _non_negative_float(value: Any) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError("non-negative number")
    number = float(value)
    if number < 0:
        raise ValueError("negative number")
    return number
