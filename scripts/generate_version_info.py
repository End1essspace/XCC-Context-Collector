from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = PROJECT_ROOT / "src"
if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))

from xcc import __version__


_VERSION_RE = re.compile(
    r"^(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)"
    r"(?:[.-]?(?P<suffix>[0-9A-Za-z.-]+))?$"
)


def windows_version_tuple(version: str) -> tuple[int, int, int, int]:
    match = _VERSION_RE.fullmatch(version)
    if match is None:
        raise ValueError(f"Unsupported application version: {version}")

    return (
        int(match.group("major")),
        int(match.group("minor")),
        int(match.group("patch")),
        0,
    )


def render_version_info(version: str = __version__) -> str:
    numeric = windows_version_tuple(version)

    return f'''VSVersionInfo(
  ffi=FixedFileInfo(
    filevers={numeric},
    prodvers={numeric},
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo([
      StringTable(
        '040904B0',
        [
          StringStruct('CompanyName', 'XCON | RX'),
          StringStruct('FileDescription', 'XCC Context Collector'),
          StringStruct('FileVersion', '{version}'),
          StringStruct('InternalName', 'XCC Context Collector'),
          StringStruct('LegalCopyright', 'Copyright (C) 2026 Rafael Xudoynazarov'),
          StringStruct('OriginalFilename', 'XCC Context Collector.exe'),
          StringStruct('ProductName', 'XCC Context Collector'),
          StringStruct('ProductVersion', '{version}')
        ]
      )
    ]),
    VarFileInfo([VarStruct('Translation', [1033, 1200])])
  ]
)
'''


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate PyInstaller Windows version metadata."
    )
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render_version_info(), encoding="utf-8", newline="\n")
    print(__version__)


if __name__ == "__main__":
    main()
