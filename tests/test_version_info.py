from __future__ import annotations

from scripts.generate_version_info import render_version_info, windows_version_tuple
from xcc import __version__


def test_windows_version_tuple_uses_four_numeric_parts() -> None:
    assert windows_version_tuple("1.2.3") == (1, 2, 3, 0)
    assert windows_version_tuple("1.2.3-rc1") == (1, 2, 3, 0)


def test_version_resource_uses_canonical_application_version() -> None:
    resource = render_version_info()

    assert f"StringStruct('FileVersion', '{__version__}')" in resource
    assert f"StringStruct('ProductVersion', '{__version__}')" in resource
    assert f"filevers={windows_version_tuple(__version__)}" in resource
