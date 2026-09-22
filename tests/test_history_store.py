from __future__ import annotations

import json
from pathlib import Path

from xcc.history_store import (
    HISTORY_MAX_RECORDS,
    export_history_json,
    load_history,
    sanitize_collection_source,
    save_history,
)
from xcc.models import AttachmentTransferRecord, CollectionOutcome, CollectionRunRecord


def _collection(index: int = 0, *, source: str = r"C:\Users\Alice\secret-project") -> CollectionRunRecord:
    return CollectionRunRecord(
        timestamp=f"2026-09-22T17:20:{index:02d}+05:00",
        mode_name="Full Folder",
        source=source,
        outcome=CollectionOutcome.SUCCESS,
        files=3,
        output_chars=120,
    )


def _attachment(index: int = 0) -> AttachmentTransferRecord:
    return AttachmentTransferRecord(
        timestamp=f"2026-09-22T17:21:{index:02d}+05:00",
        transfer_type="Copy Files",
        outcome="SUCCESS",
        file_count=8,
        total_bytes=4096,
        bundle_name=r"C:\Users\Alice\.xcc\attachment-bundles\XCC-Attachments.zip",
    )


def test_source_sanitizer_removes_windows_and_posix_absolute_paths() -> None:
    assert sanitize_collection_source(r"C:\Users\Alice\repo", "Full Folder") == "Project folder"
    assert sanitize_collection_source("/home/alice/repo", "Git Changed Files") == "Git repository"
    assert sanitize_collection_source("8 selected files", "Selected Files") == "8 selected files"


def test_save_and_load_roundtrip_is_metadata_only(tmp_path: Path) -> None:
    path = tmp_path / "history.json"
    save_history([_collection(), _attachment()], path)

    raw = path.read_text(encoding="utf-8")
    assert r"C:\\Users\\Alice" not in raw
    assert "secret-project" not in raw
    assert '"privacy": "metadata-only"' in raw

    result = load_history(path)
    assert not result.recovered_from_error
    assert len(result.records) == 2
    assert isinstance(result.records[0], CollectionRunRecord)
    assert result.records[0].source == "Project folder"
    assert isinstance(result.records[1], AttachmentTransferRecord)
    assert result.records[1].bundle_name == "XCC-Attachments.zip"


def test_retention_is_bounded(tmp_path: Path) -> None:
    path = tmp_path / "history.json"
    records = [_collection(i % 60, source=f"{i} selected files") for i in range(HISTORY_MAX_RECORDS + 17)]
    saved = save_history(records, path)
    assert len(saved) == HISTORY_MAX_RECORDS
    assert len(load_history(path).records) == HISTORY_MAX_RECORDS


def test_invalid_json_is_backed_up_and_recovers_empty(tmp_path: Path) -> None:
    path = tmp_path / "history.json"
    path.write_text("{broken", encoding="utf-8")

    result = load_history(path)
    assert result.recovered_from_error
    assert result.records == ()
    assert result.backup_path is not None
    assert result.backup_path.exists()
    assert not path.exists()


def test_valid_records_survive_one_corrupt_record(tmp_path: Path) -> None:
    path = tmp_path / "history.json"
    save_history([_collection(source="3 selected files")], path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["records"].append({"type": "collection", "outcome": "NOPE"})
    path.write_text(json.dumps(payload), encoding="utf-8")

    result = load_history(path)
    assert result.recovered_from_error
    assert result.dropped_records == 1
    assert len(result.records) == 1


def test_export_is_documented_machine_readable_json(tmp_path: Path) -> None:
    destination = tmp_path / "export.json"
    export_history_json([_collection(), _attachment()], destination)
    payload = json.loads(destination.read_text(encoding="utf-8"))
    assert payload["schema_version"] == 1
    assert payload["format"] == "xcc-runtime-history"
    assert payload["privacy"] == "metadata-only"
    assert [item["type"] for item in payload["records"]] == ["collection", "attachment"]
