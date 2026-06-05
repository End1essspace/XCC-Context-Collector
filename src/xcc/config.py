from __future__ import annotations


APP_NAME = "XCC"
APP_FULL_NAME = "XCC Context Collector"

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
    ".dockerignore",
    ".gitattributes",
    ".editorconfig",

    ".env.example",
    ".env.template",
    ".env.sample",
}

ENCODINGS = (
    "utf-8",
    "utf-8-sig",
    "cp1251",
)

MAX_FILE_SIZE_BYTES = 512 * 1024
MAX_OUTPUT_CHARS = 120_000
DEFAULT_HOTKEY = "ctrl+alt+x"