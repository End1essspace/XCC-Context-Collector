from __future__ import annotations
from pathlib import Path


ALLOWED_EXTENSIONS = {
    # Python
    ".py",
    ".pyw",

    # JavaScript / TypeScript / Frontend
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".mjs",
    ".cjs",
    ".html",
    ".css",
    ".scss",
    ".sass",
    ".less",
    ".vue",
    ".svelte",

    # Backend / system languages
    ".java",
    ".kt",
    ".kts",
    ".cs",
    ".go",
    ".rs",
    ".c",
    ".h",
    ".cpp",
    ".hpp",
    ".cc",
    ".cxx",
    ".php",
    ".rb",
    ".swift",

    # Data / API / DB
    ".sql",
    ".graphql",
    ".gql",

    # Docs
    ".md",
    ".mdx",
    ".rst",
    ".txt",

    # Config
    ".json",
    ".jsonc",
    ".yaml",
    ".yml",
    ".toml",
    ".ini",
    ".cfg",
    ".conf",
    ".properties",
    ".xml",

    # Scripts
    ".sh",
    ".bash",
    ".zsh",
    ".ps1",
    ".bat",
    ".cmd",
}

EXCLUDED_DIRS = {
    ".git",
    ".idea",
    ".vscode",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "node_modules",
    "dist",
    "build",
    "bin",
    "obj",
}

ALLOWED_FILENAMES = {
    "Dockerfile",
    "Containerfile",
    "Makefile",
    "CMakeLists.txt",

    "requirements.txt",
    "pyproject.toml",
    "setup.py",
    "setup.cfg",

    "package.json",
    "tsconfig.json",
    "vite.config.js",
    "vite.config.ts",
    "next.config.js",
    "next.config.ts",

    ".gitignore",
    ".xccignore",
    ".dockerignore",
    ".gitattributes",
    ".editorconfig",

    ".env.example",
    ".env.template",
    ".env.sample",
}

ALLOWED_FILENAMES_CASEFOLD = frozenset(
    name.casefold() for name in ALLOWED_FILENAMES
)

ENCODINGS = (
    "utf-8",
    "utf-8-sig",
    "cp1251",
)

MAX_FILE_SIZE_BYTES = 512 * 1024
MAX_OUTPUT_CHARS = 3_000_000
DEFAULT_HOTKEY = "ctrl+alt+x"
DEFAULT_COLLECT_HOTKEY = "ctrl+alt+c"
DEFAULT_ATTACHMENT_HANDOFF_HOTKEY = "ctrl+alt+v"

def is_allowed_context_file(
    path: str | Path,
    *,
    allowed_extensions: set[str] | None = None,
    allowed_filenames: set[str] | None = None,
) -> bool:
    path = Path(path)

    extensions = allowed_extensions or ALLOWED_EXTENSIONS
    filenames_casefold = (
        ALLOWED_FILENAMES_CASEFOLD
        if allowed_filenames is None
        else frozenset(name.casefold() for name in allowed_filenames)
    )

    return (
        path.suffix.lower() in extensions
        or path.name.casefold() in filenames_casefold
    )


def context_file_patterns() -> list[str]:
    extension_patterns = [f"*{ext}" for ext in sorted(ALLOWED_EXTENSIONS)]
    filename_patterns = sorted(ALLOWED_FILENAMES, key=str.lower)

    return extension_patterns + filename_patterns


def qt_context_file_filter() -> str:
    patterns = " ".join(context_file_patterns())
    return f"Context files ({patterns});;All files (*.*)"
