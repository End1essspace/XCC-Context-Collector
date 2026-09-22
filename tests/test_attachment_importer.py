from __future__ import annotations

from pathlib import Path

from xcc.attachment_importer import (
    AttachmentSelection,
    build_attachment_selection,
    import_attachment_files,
    import_attachments,
    revalidate_attachment_files,
)


def test_attachment_import_accepts_binary_and_unknown_extensions(tmp_path: Path) -> None:
    root = tmp_path / "project"
    root.mkdir()
    blend = root / "model.blend"
    binary = root / "payload.bin"
    unknown = root / "data.customext"
    for path, data in ((blend, b"blend"), (binary, b"bin"), (unknown, b"custom")):
        path.write_bytes(data)

    result = import_attachments(
        "model.blend\npayload.bin\ndata.customext",
        project_root=root,
    )

    assert result.added_paths == (blend.resolve(), binary.resolve(), unknown.resolve())
    assert result.issue_count == 0
    assert result.added_bytes == 5 + 3 + 6


def test_attachment_import_preserves_order_and_windows_style_deduplication(tmp_path: Path) -> None:
    root = tmp_path / "project"
    root.mkdir()
    first = root / "A.asset"
    second = root / "B.png"
    first.write_text("a", encoding="utf-8")
    second.write_bytes(b"bb")

    result = import_attachments(
        "A.asset\nB.png",
        project_root=root,
        existing_paths=[first],
    )

    assert result.added_paths == (second.resolve(),)
    assert result.duplicates == ("A.asset",)


def test_relative_root_escape_is_rejected_but_absolute_external_file_is_valid(tmp_path: Path) -> None:
    root = tmp_path / "project"
    root.mkdir()
    inside = root / "inside.unity"
    outside = tmp_path / "outside.fbx"
    inside.write_text("scene", encoding="utf-8")
    outside.write_bytes(b"fbx")

    result = import_attachments(
        f"inside.unity\n../outside.fbx\n{outside}",
        project_root=root,
    )

    assert result.added_paths == (inside.resolve(), outside.resolve())
    assert result.outside_root == ("../outside.fbx",)
    assert result.external == (outside.resolve(),)


def test_missing_directories_and_relative_paths_without_root_are_explicit(tmp_path: Path) -> None:
    folder = tmp_path / "folder"
    folder.mkdir()

    result = import_attachments("missing.bin\nfolder/", project_root=tmp_path)
    assert result.missing == ("missing.bin",)
    assert result.directories == ("folder/",)

    rootless = import_attachments("Assets/Game.unity")
    assert rootless.root_required == ("Assets/Game.unity",)
    assert rootless.needs_project_root_selection


def test_direct_file_picker_path_has_no_extension_allowlist(tmp_path: Path) -> None:
    file = tmp_path / "library.dll"
    file.write_bytes(b"dll")

    result = import_attachment_files([file])

    assert result.added_paths == (file.resolve(),)
    assert result.issue_count == 0


def test_selection_reports_mixed_locations_and_aggregate_size(tmp_path: Path) -> None:
    root = tmp_path / "project"
    root.mkdir()
    inside = root / "inside.asset"
    outside = tmp_path / "outside.png"
    inside.write_bytes(b"123")
    outside.write_bytes(b"12345")

    selection = build_attachment_selection([inside, outside], project_root=root)

    assert selection.file_count == 2
    assert selection.total_bytes == 8
    assert selection.has_mixed_locations
    assert selection.scope_label == "Mixed locations"


def test_revalidate_attachment_files_fails_when_source_disappears(tmp_path: Path) -> None:
    file = tmp_path / "file.bin"
    file.write_bytes(b"123")
    assert revalidate_attachment_files([file])[0].size_bytes == 3
    file.unlink()

    try:
        revalidate_attachment_files([file])
    except FileNotFoundError as exc:
        assert "no longer exists" in str(exc)
    else:
        raise AssertionError("stale attachment must fail revalidation")


def test_attachment_size_formatting_matches_product_copy() -> None:
    from xcc.ui_attachments import format_attachment_size

    assert format_attachment_size(0) == "0 B"
    assert format_attachment_size(84 * 1024) == "84 KB"
    assert format_attachment_size(int(2.4 * 1024 * 1024)) == "2.4 MB"
    assert format_attachment_size(150 * 1024 * 1024) == "150 MB"
