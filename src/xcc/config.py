from __future__ import annotations


APP_NAME = "XCC"
APP_FULL_NAME = "XCC Context Collector"

ALLOWED_EXTENSIONS = {
    ".py",
}

EXCLUDED_DIRS = {
    ".git",
    ".idea",
    ".vscode",
    ".venv",
    "venv",
    "__pycache__",
    "node_modules",
    "dist",
    "build",
    "bin",
    "obj",
}

ENCODINGS = (
    "utf-8",
    "utf-8-sig",
    "cp1251",
)

MAX_FILE_SIZE_BYTES = 512 * 1024
MAX_OUTPUT_CHARS = 120_000