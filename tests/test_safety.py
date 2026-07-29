from pathlib import Path

from xcc.models import FileContent, GitContext, SafetyWarning
from xcc.safety import (
    WARNING_API_TOKEN,
    WARNING_CONNECTION_STRING,
    WARNING_CREDENTIAL,
    WARNING_PRIVATE_KEY,
    WARNING_SENSITIVE_FILENAME,
    build_warning_confirmation_text,
    format_warning_lines,
    scan_files_for_warnings,
    scan_git_context_for_warnings,
    scan_project_filename_warnings,
    scan_text_for_warnings,
    should_show_safety_confirmation,
)


def _file(path: str, content: str, *, is_summary: bool = False) -> FileContent:
    return FileContent(
        path=Path(path),
        content=content,
        line_count=content.count("\n") + (1 if content else 0),
        char_count=len(content),
        is_summary=is_summary,
    )


def test_detects_private_key_token_and_credentials_without_values() -> None:
    content = (
        "-----BEGIN PRIVATE KEY-----\n"
        'API_KEY = "sk_live_1234567890abcdef"\n'
        'password = "supersecret123"\n'
        'DATABASE_URL = "postgresql://user:secretpass@localhost/app"\n'
    )

    warnings = scan_text_for_warnings(content, display_path="config.py")
    categories = {warning.category for warning in warnings}

    assert WARNING_PRIVATE_KEY in categories
    assert WARNING_API_TOKEN in categories
    assert WARNING_CREDENTIAL in categories
    assert WARNING_CONNECTION_STRING in categories
    assert all(warning.path == "config.py" for warning in warnings)
    assert all(warning.line_number is not None for warning in warnings)

    rendered = "\n".join(format_warning_lines(warnings))
    assert "sk_live_1234567890abcdef" not in rendered
    assert "supersecret123" not in rendered
    assert "secretpass" not in rendered


def test_ignores_placeholders_environment_references_and_comments() -> None:
    content = (
        '# API_KEY = "real-looking-but-commented-value"\n'
        'API_KEY = "your_api_key"\n'
        'password = os.getenv("DB_PASSWORD")\n'
        'token = "example"\n'
    )

    assert scan_text_for_warnings(content, display_path="example.py") == []


def test_detects_sensitive_filename_without_reading_value() -> None:
    file = _file("config/credentials.json", '{"token": "your_token"}\n')

    warnings = scan_files_for_warnings(
        [file],
        display_paths=["config/credentials.json"],
    )

    assert any(w.category == WARNING_SENSITIVE_FILENAME for w in warnings)
    assert all(w.path == "config/credentials.json" for w in warnings)


def test_large_file_summary_is_not_scanned_as_secret_content() -> None:
    file = _file(
        "generated.py",
        'API_KEY = "sk_live_1234567890abcdef"\n',
        is_summary=True,
    )

    assert scan_files_for_warnings([file], display_paths=["generated.py"]) == []


def test_git_diff_scans_added_and_removed_secret_lines() -> None:
    context = GitContext(
        staged_diff=(
            "diff --git a/config.py b/config.py\n"
            "--- a/config.py\n"
            "+++ b/config.py\n"
            "@@ -1,2 +1,2 @@\n"
            '-password = "oldsecret123"\n'
            '+password = "newsecret456"\n'
            " normal = 1\n"
        )
    )

    warnings = scan_git_context_for_warnings(context)

    assert len(warnings) == 1
    assert warnings[0].path == "config.py"
    assert warnings[0].line_number == 1
    assert warnings[0].category == WARNING_CREDENTIAL


def test_confirmation_text_never_contains_secret_values() -> None:
    file = _file("settings.py", 'password = "supersecret123"\n')
    warnings = scan_files_for_warnings([file], display_paths=["settings.py"])

    text = build_warning_confirmation_text(warnings)

    assert "settings.py:1" in text
    assert WARNING_CREDENTIAL in text
    assert "supersecret123" not in text
    assert "heuristic" in text.lower()


def test_project_filename_scan_respects_project_ignore_rules(tmp_path: Path) -> None:
    ignored = tmp_path / "private" / "credentials.json"
    visible = tmp_path / "config" / "secrets.json"
    ignored.parent.mkdir()
    visible.parent.mkdir()
    ignored.write_text("{}", encoding="utf-8")
    visible.write_text("{}", encoding="utf-8")
    (tmp_path / ".xccignore").write_text("private/**\n", encoding="utf-8")

    warnings = scan_project_filename_warnings(tmp_path)
    paths = {warning.path for warning in warnings}

    assert "config/secrets.json" in paths
    assert "private/credentials.json" not in paths


def test_safety_confirmation_can_be_disabled_without_hiding_findings() -> None:
    warnings = [
        SafetyWarning(
            path="config.py",
            category=WARNING_CREDENTIAL,
            line_number=4,
        )
    ]

    assert should_show_safety_confirmation(warnings, enabled=True) is True
    assert should_show_safety_confirmation(warnings, enabled=False) is False
    assert warnings[0].category == WARNING_CREDENTIAL


def test_safety_confirmation_is_not_requested_without_findings() -> None:
    assert should_show_safety_confirmation([], enabled=True) is False
