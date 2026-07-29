from __future__ import annotations

import re
from collections.abc import Callable, Sequence
from pathlib import Path

from .cancellation import CollectionCancelled
from .config import EXCLUDED_DIRS
from .ignore import ProjectIgnoreMatcher
from .models import FileContent, GitContext, SafetyWarning

WARNING_SENSITIVE_FILENAME = "Sensitive filename"
WARNING_PRIVATE_KEY = "Private key material"
WARNING_API_TOKEN = "API token or access key"
WARNING_CREDENTIAL = "Credential assignment"
WARNING_CONNECTION_STRING = "Connection string with credentials"

_SENSITIVE_FILENAMES = {
    ".env",
    ".env.local",
    ".env.production",
    ".env.development",
    ".env.staging",
    ".npmrc",
    ".pypirc",
    ".netrc",
    "credentials",
    "credentials.json",
    "credentials.yaml",
    "credentials.yml",
    "secrets.json",
    "secrets.yaml",
    "secrets.yml",
    "service-account.json",
    "service_account.json",
    "id_rsa",
    "id_ed25519",
    "id_ecdsa",
    "id_dsa",
    "kubeconfig",
}

_SENSITIVE_FILENAME_FRAGMENTS = (
    "firebase-adminsdk",
    "service-account",
    "service_account",
)

_PRIVATE_KEY_RE = re.compile(
    r"-----BEGIN (?:RSA |EC |OPENSSH |DSA |PGP )?PRIVATE KEY-----",
    re.IGNORECASE,
)

_KNOWN_TOKEN_RES = (
    re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b"),
    re.compile(r"\bAIza[0-9A-Za-z_-]{30,}\b"),
    re.compile(r"\bsk_live_[0-9A-Za-z]{16,}\b"),
)

_SECRET_ASSIGNMENT_RE = re.compile(
    r"(?ix)"
    r"(?:^|[\s,{(])"
    r"[\"']?"
    r"(?P<name>"
    r"api[_-]?key|access[_-]?key|access[_-]?token|auth[_-]?token|"
    r"client[_-]?secret|secret[_-]?key|private[_-]?token"
    r")"
    r"[\"']?\s*(?:=|:)\s*(?P<value>[^,\s#}]+|[\"'][^\"']*[\"'])"
)

_CREDENTIAL_ASSIGNMENT_RE = re.compile(
    r"(?ix)"
    r"(?:^|[\s,{(])"
    r"[\"']?"
    r"(?P<name>password|passwd|pwd|database[_-]?url|connection[_-]?string|dsn)"
    r"[\"']?\s*(?:=|:)\s*(?P<value>[^,\s#}]+|[\"'][^\"']*[\"'])"
)

_CONNECTION_URI_RE = re.compile(
    r"\b(?:postgres(?:ql)?|mysql|mariadb|mongodb(?:\+srv)?|redis|amqp|mssql)://"
    r"[^\s/:@]+:[^\s/@]+@",
    re.IGNORECASE,
)

_DIFF_HUNK_RE = re.compile(
    r"^@@ -(?P<old>\d+)(?:,\d+)? \+(?P<new>\d+)(?:,\d+)? @@"
)

_PLACEHOLDER_VALUES = {
    "",
    "none",
    "null",
    "example",
    "sample",
    "test",
    "testing",
    "changeme",
    "change-me",
    "change_me",
    "replace-me",
    "replace_me",
    "your-key",
    "your_key",
    "your-api-key",
    "your_api_key",
    "your-token",
    "your_token",
    "your-password",
    "your_password",
    "password",
    "secret",
    "token",
    "dummy",
    "placeholder",
    "redacted",
    "<redacted>",
    "***",
}


def scan_files_for_warnings(
    files: Sequence[FileContent],
    *,
    display_paths: Sequence[str] | None = None,
    progress_callback: Callable[[int, int], None] | None = None,
    cancel_check: Callable[[], bool] | None = None,
) -> list[SafetyWarning]:
    if display_paths is not None and len(display_paths) != len(files):
        raise ValueError("display_paths must match files length")

    warnings: list[SafetyWarning] = []
    seen: set[tuple[str, str, int | None]] = set()

    total = len(files)

    for index, file in enumerate(files):
        if cancel_check is not None and cancel_check():
            raise CollectionCancelled("Collection cancelled.")
        display_path = (
            display_paths[index]
            if display_paths is not None
            else file.path.as_posix()
        )

        _append_unique(
            warnings,
            seen,
            scan_filename_for_warnings(file.path, display_path=display_path),
        )

        if file.is_summary:
            if progress_callback is not None:
                progress_callback(index + 1, total)
            continue

        _append_unique(
            warnings,
            seen,
            scan_text_for_warnings(file.content, display_path=display_path),
        )

        if progress_callback is not None:
            progress_callback(index + 1, total)

    return merge_warnings(warnings)


def scan_paths_for_filename_warnings(
    paths: Sequence[str | Path],
    *,
    project_root: str | Path | None = None,
) -> list[SafetyWarning]:
    warnings: list[SafetyWarning] = []
    seen: set[tuple[str, str, int | None]] = set()
    root = Path(project_root).resolve() if project_root is not None else None

    for raw_path in paths:
        path = Path(raw_path)
        if root is not None:
            try:
                display_path = path.resolve().relative_to(root).as_posix()
            except (OSError, ValueError):
                display_path = path.name
        else:
            display_path = path.name

        _append_unique(
            warnings,
            seen,
            scan_filename_for_warnings(path, display_path=display_path),
        )

    return warnings


def scan_project_filename_warnings(
    project_root: str | Path,
    *,
    excluded_dirs: set[str] | None = None,
    respect_xccignore: bool = True,
    respect_gitignore: bool = True,
    progress_callback: Callable[[int, int], None] | None = None,
    cancel_check: Callable[[], bool] | None = None,
) -> list[SafetyWarning]:
    root = Path(project_root)
    excluded = excluded_dirs or EXCLUDED_DIRS
    matcher = ProjectIgnoreMatcher.from_project_root(
        root,
        respect_xccignore=respect_xccignore,
        respect_gitignore=respect_gitignore,
    )

    warnings: list[SafetyWarning] = []
    seen: set[tuple[str, str, int | None]] = set()

    processed_files = 0

    for path in root.rglob("*"):
        if cancel_check is not None and cancel_check():
            raise CollectionCancelled("Collection cancelled.")

        if not path.is_file():
            continue

        try:
            relative = path.relative_to(root)
        except ValueError:
            continue

        if any(part in excluded for part in relative.parts[:-1]):
            continue

        if matcher.is_ignored(relative, is_dir=False):
            continue

        _append_unique(
            warnings,
            seen,
            scan_filename_for_warnings(
                path,
                display_path=relative.as_posix(),
            ),
        )
        processed_files += 1
        if progress_callback is not None:
            progress_callback(processed_files, 0)

    return warnings


def scan_git_context_for_warnings(
    context: GitContext,
    *,
    cancel_check: Callable[[], bool] | None = None,
) -> list[SafetyWarning]:
    warnings: list[SafetyWarning] = []
    seen: set[tuple[str, str, int | None]] = set()

    for diff in (context.staged_diff, context.unstaged_diff):
        if cancel_check is not None and cancel_check():
            raise CollectionCancelled("Collection cancelled.")

        _append_unique(
            warnings,
            seen,
            scan_git_diff_for_warnings(
                diff,
                cancel_check=cancel_check,
            ),
        )

    return warnings


def scan_git_diff_for_warnings(
    diff: str,
    *,
    cancel_check: Callable[[], bool] | None = None,
) -> list[SafetyWarning]:
    if not diff:
        return []

    warnings: list[SafetyWarning] = []
    old_path = "Git diff"
    new_path = "Git diff"
    old_line: int | None = None
    new_line: int | None = None

    for raw_line in diff.splitlines():
        if cancel_check is not None and cancel_check():
            raise CollectionCancelled("Collection cancelled.")

        if raw_line.startswith("--- "):
            old_path = _normalize_diff_path(raw_line[4:])
            continue

        if raw_line.startswith("+++ "):
            new_path = _normalize_diff_path(raw_line[4:])
            continue

        hunk_match = _DIFF_HUNK_RE.match(raw_line)
        if hunk_match:
            old_line = int(hunk_match.group("old"))
            new_line = int(hunk_match.group("new"))
            continue

        if old_line is None or new_line is None or not raw_line:
            continue

        prefix = raw_line[0]
        payload = raw_line[1:]

        if prefix == "+":
            path = new_path if new_path != "/dev/null" else old_path
            _append_line_warnings(
                warnings,
                payload,
                display_path=path,
                line_number=new_line,
            )
            new_line += 1
            continue

        if prefix == "-":
            path = old_path if old_path != "/dev/null" else new_path
            _append_line_warnings(
                warnings,
                payload,
                display_path=path,
                line_number=old_line,
            )
            old_line += 1
            continue

        if prefix == " ":
            old_line += 1
            new_line += 1

    return merge_warnings(warnings)


def scan_filename_for_warnings(
    path: str | Path,
    *,
    display_path: str | None = None,
) -> list[SafetyWarning]:
    file_path = Path(path)
    name = file_path.name.casefold()

    is_sensitive = name in _SENSITIVE_FILENAMES or any(
        fragment in name for fragment in _SENSITIVE_FILENAME_FRAGMENTS
    )
    if not is_sensitive:
        return []

    return [
        SafetyWarning(
            path=display_path or file_path.as_posix(),
            category=WARNING_SENSITIVE_FILENAME,
        )
    ]


def scan_text_for_warnings(
    text: str,
    *,
    display_path: str,
) -> list[SafetyWarning]:
    warnings: list[SafetyWarning] = []
    seen_categories: set[tuple[str, int]] = set()

    for line_number, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if not stripped or _is_comment_only_line(stripped):
            continue

        for category in _warning_categories_for_line(line):
            key = (category, line_number)
            if key in seen_categories:
                continue

            seen_categories.add(key)
            warnings.append(
                SafetyWarning(
                    path=display_path,
                    line_number=line_number,
                    category=category,
                )
            )

    return warnings


def merge_warnings(*warning_groups: Sequence[SafetyWarning]) -> list[SafetyWarning]:
    merged: list[SafetyWarning] = []
    seen: set[tuple[str, str, int | None]] = set()

    for group in warning_groups:
        _append_unique(merged, seen, group)

    return merged


def format_warning_lines(
    warnings: Sequence[SafetyWarning],
    *,
    max_items: int = 20,
) -> list[str]:
    lines = [
        f"- {warning.location} — {warning.category}"
        for warning in warnings[:max_items]
    ]

    remaining = len(warnings) - len(lines)
    if remaining > 0:
        lines.append(f"- ... {remaining} additional warning(s) not listed")

    return lines



def should_show_safety_confirmation(
    warnings: Sequence[SafetyWarning],
    *,
    enabled: bool,
) -> bool:
    """Return whether the GUI should interrupt copy with a confirmation dialog.

    Warning detection remains active even when confirmation is disabled so the
    generated context, outcome, metrics, and history stay transparent.
    """
    return enabled and bool(warnings)

def build_warning_confirmation_text(
    warnings: Sequence[SafetyWarning],
    *,
    max_items: int = 20,
) -> str:
    lines = [
        "XCC found potentially sensitive context.",
        "",
        *format_warning_lines(warnings, max_items=max_items),
        "",
        "Only file paths, line numbers, and warning categories are shown.",
        "Secret values are not displayed or stored in runtime history.",
        "Detection is heuristic and may produce false positives.",
        "",
        "Continue and copy this context?",
    ]
    return "\n".join(lines)


def _looks_like_real_secret(raw_value: str) -> bool:
    value = raw_value.strip().strip("\"'").strip()
    lowered = value.casefold()

    if lowered in _PLACEHOLDER_VALUES:
        return False

    if not value:
        return False

    if value.startswith(("${", "$env:", "%", "{{", "<")):
        return False

    if any(
        marker in lowered
        for marker in (
            "os.getenv",
            "os.environ",
            "process.env",
            "getenv(",
            "secretref",
            "vault:",
        )
    ):
        return False

    if lowered.startswith(("your_", "your-", "example_", "example-")):
        return False

    # Short values such as "dev" or "1234" are too ambiguous. Known token
    # prefixes are handled separately above.
    return len(value) >= 8


def _warning_categories_for_line(line: str) -> list[str]:
    stripped = line.strip()
    if not stripped or _is_comment_only_line(stripped):
        return []

    categories: list[str] = []

    if _PRIVATE_KEY_RE.search(line):
        categories.append(WARNING_PRIVATE_KEY)

    if any(pattern.search(line) for pattern in _KNOWN_TOKEN_RES):
        categories.append(WARNING_API_TOKEN)

    secret_match = _SECRET_ASSIGNMENT_RE.search(line)
    if secret_match and _looks_like_real_secret(secret_match.group("value")):
        categories.append(WARNING_API_TOKEN)

    credential_match = _CREDENTIAL_ASSIGNMENT_RE.search(line)
    if credential_match and _looks_like_real_secret(
        credential_match.group("value")
    ):
        categories.append(WARNING_CREDENTIAL)

    if _CONNECTION_URI_RE.search(line):
        categories.append(WARNING_CONNECTION_STRING)

    return list(dict.fromkeys(categories))


def _append_line_warnings(
    target: list[SafetyWarning],
    line: str,
    *,
    display_path: str,
    line_number: int,
) -> None:
    for category in _warning_categories_for_line(line):
        target.append(
            SafetyWarning(
                path=display_path,
                category=category,
                line_number=line_number,
            )
        )


def _normalize_diff_path(raw_path: str) -> str:
    value = raw_path.strip()
    if value == "/dev/null":
        return value

    if value.startswith(("a/", "b/")):
        value = value[2:]

    return value.replace("\\", "/")


def _is_comment_only_line(stripped: str) -> bool:
    return stripped.startswith(("#", "//", ";", "<!--", "*"))


def _append_unique(
    target: list[SafetyWarning],
    seen: set[tuple[str, str, int | None]],
    candidates: Sequence[SafetyWarning],
) -> None:
    for warning in candidates:
        key = (warning.path, warning.category, warning.line_number)
        if key in seen:
            continue

        seen.add(key)
        target.append(warning)
