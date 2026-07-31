from __future__ import annotations

import tomllib
from pathlib import Path

from xcc import __version__

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _metadata() -> dict:
    return tomllib.loads(
        (PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    )


def test_pyproject_defines_canonical_project_metadata() -> None:
    metadata = _metadata()
    project = metadata["project"]

    assert project["name"] == "xcc-context-collector"
    assert project["requires-python"] == ">=3.13,<3.14"
    assert project["dynamic"] == ["version"]
    assert metadata["tool"]["setuptools"]["dynamic"]["version"] == {
        "attr": "xcc.__version__"
    }
    assert __version__ == "1.3.0"


def test_dependency_groups_keep_runtime_minimal() -> None:
    project = _metadata()["project"]
    runtime = project["dependencies"]
    extras = project["optional-dependencies"]

    assert runtime == [
        "PySide6>=6.8,<6.12",
        "pyperclip>=1.9,<2",
    ]
    assert extras["dev"] == [
        "pytest>=8.3,<10",
        "pytest-cov>=6,<8",
    ]
    assert extras["build"] == ["pyinstaller>=6.11,<7"]
    assert extras["legacy"] == ["keyboard==0.13.5"]
    assert all("keyboard" not in dependency for dependency in runtime)


def test_pyproject_exposes_supported_gui_entry_point() -> None:
    project = _metadata()["project"]

    assert project["gui-scripts"] == {
        "xcc-context-collector": "xcc.gui:run_gui"
    }


def test_requirements_file_is_only_a_compatibility_wrapper() -> None:
    lines = [
        line.strip()
        for line in (PROJECT_ROOT / "requirements.txt")
        .read_text(encoding="utf-8")
        .splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]

    assert lines == ["-e ."]


def test_build_script_reads_canonical_version() -> None:
    script = (PROJECT_ROOT / "scripts" / "build_release.ps1").read_text(
        encoding="utf-8"
    )

    assert "from xcc import __version__" in script
    assert "generate_version_info.py" in script
    assert "--version-file" in script
    assert "VERSION.txt" in script


def test_v130_ui_reference_contract_is_frozen() -> None:
    reference_path = PROJECT_ROOT / "docs" / "UI_REFERENCE_v1.3.0.md"
    roadmap_path = PROJECT_ROOT / "docs" / "roadmap.md"

    assert reference_path.is_file()

    reference = reference_path.read_text(encoding="utf-8")
    roadmap = roadmap_path.read_text(encoding="utf-8")

    required_reference_markers = (
        "# XCC v1.3.0 Final UI Reference Contract",
        "Status: **FROZEN FOR IMPLEMENTATION**",
        "Minimum supported window: `920 × 620`",
        "## 5. Application Shell",
        "## 6. Collect Page Contract",
        "## 7. Last Run Contract",
        "## 8. Responsive Layout Contract",
        "## 9. Dialog Contract",
        "The title and subtitle share one 42 px row",
        "`Select Files`",
        "`Select Folder`",
        "`Select Repository`",
        "Source file contents remain unchanged.",
        "Transactional behavior is non-negotiable",
    )

    for marker in required_reference_markers:
        assert marker in reference

    assert "## M15.2 — Final UI Reference Contract" in roadmap
    assert "**Status: DONE**" in roadmap[roadmap.index("## M15.2"):roadmap.index("## M15.3")]
    assert "docs/UI_REFERENCE_v1.3.0.md" in roadmap

def test_v130_ui_foundation_modules_are_registered() -> None:
    theme_path = PROJECT_ROOT / "src" / "xcc" / "ui_theme.py"
    components_path = PROJECT_ROOT / "src" / "xcc" / "ui_components.py"
    gui_path = PROJECT_ROOT / "src" / "xcc" / "gui.py"
    roadmap_path = PROJECT_ROOT / "docs" / "roadmap.md"

    assert theme_path.is_file()
    assert components_path.is_file()

    theme = theme_path.read_text(encoding="utf-8")
    components = components_path.read_text(encoding="utf-8")
    gui = gui_path.read_text(encoding="utf-8")
    roadmap = roadmap_path.read_text(encoding="utf-8")

    assert "class UiPalette" in theme
    assert "class UiMetrics" in theme
    assert "def build_application_stylesheet" in theme
    assert "def build_tray_menu_stylesheet" in theme
    assert "class MetricCapsule" in components
    assert "class StatusCapsule" in components
    assert "def make_primary_button" in components
    assert "def make_secondary_button" in components
    assert "from .ui_theme import (" in gui
    assert "from .ui_components import (" in gui
    assert "self.setStyleSheet(build_application_stylesheet())" in gui
    assert "tray_menu.setStyleSheet(build_tray_menu_stylesheet())" in gui
    assert "## M15.3 — Theme and Reusable UI Foundation" in roadmap


def test_v130_application_shell_redesign_is_registered() -> None:
    shell_path = PROJECT_ROOT / "src" / "xcc" / "ui_shell.py"
    sidebar_path = PROJECT_ROOT / "src" / "xcc" / "ui_sidebar.py"
    components_path = PROJECT_ROOT / "src" / "xcc" / "ui_components.py"
    gui_path = PROJECT_ROOT / "src" / "xcc" / "gui.py"
    roadmap_path = PROJECT_ROOT / "docs" / "roadmap.md"

    assert shell_path.is_file()

    shell = shell_path.read_text(encoding="utf-8")
    sidebar = sidebar_path.read_text(encoding="utf-8")
    components = components_path.read_text(encoding="utf-8")
    gui = gui_path.read_text(encoding="utf-8")
    roadmap = roadmap_path.read_text(encoding="utf-8")

    assert "class RuntimeState(Enum)" in shell
    assert "def default_footer_message" in shell
    assert "class RuntimeStatusCapsule" in components
    assert "make_runtime_status_capsule" in gui
    assert "FooterStatusDot" in gui
    assert "from .ui_sidebar import SidebarNavigation" in gui
    assert "class SidebarNavigation" in sidebar
    assert "QListWidget" not in sidebar
    assert "## M15.4 — Application Shell Redesign" in roadmap
    m154 = roadmap[
        roadmap.index("## M15.4"):
        roadmap.index("## M15.5")
    ]
    assert "**Status: DONE**" in m154

def test_v130_collect_setup_redesign_is_registered() -> None:
    collect_policy_path = PROJECT_ROOT / "src" / "xcc" / "ui_collect.py"
    components_path = PROJECT_ROOT / "src" / "xcc" / "ui_components.py"
    gui_path = PROJECT_ROOT / "src" / "xcc" / "gui.py"
    roadmap_path = PROJECT_ROOT / "docs" / "roadmap.md"

    assert collect_policy_path.is_file()

    collect_policy = collect_policy_path.read_text(encoding="utf-8")
    components = components_path.read_text(encoding="utf-8")
    gui = gui_path.read_text(encoding="utf-8")
    roadmap = roadmap_path.read_text(encoding="utf-8")

    assert "class CollectModePresentation" in collect_policy
    assert "def collect_mode_presentation" in collect_policy
    assert "def selected_files_source_summary" in collect_policy
    assert "COMPACT_MODE_HELPER" in collect_policy
    assert "class PageHeader" in components
    assert "make_page_header" in gui
    assert "collect_mode_presentation" in gui
    assert '"Select Source"' not in gui
    assert "SourceHelperText" in gui
    assert "OptionsHelperText" in gui
    assert "## M15.5 — Collect Setup Redesign" in roadmap

    m155 = roadmap[
        roadmap.index("## M15.5"):
        roadmap.index("## M15.6")
    ]
    assert "**Status: DONE**" in m155

def test_v130_last_run_metrics_redesign_is_registered() -> None:
    metrics_policy_path = PROJECT_ROOT / "src" / "xcc" / "ui_metrics.py"
    components_path = PROJECT_ROOT / "src" / "xcc" / "ui_components.py"
    gui_path = PROJECT_ROOT / "src" / "xcc" / "gui.py"
    theme_path = PROJECT_ROOT / "src" / "xcc" / "ui_theme.py"
    roadmap_path = PROJECT_ROOT / "docs" / "roadmap.md"
    reference_path = PROJECT_ROOT / "docs" / "UI_REFERENCE_v1.3.0.md"

    assert metrics_policy_path.is_file()

    metrics_policy = metrics_policy_path.read_text(encoding="utf-8")
    components = components_path.read_text(encoding="utf-8")
    gui = gui_path.read_text(encoding="utf-8")
    theme = theme_path.read_text(encoding="utf-8")
    roadmap = roadmap_path.read_text(encoding="utf-8")
    reference = reference_path.read_text(encoding="utf-8")

    assert "def format_metric_integer" in metrics_policy
    assert "def outcome_metric_state" in metrics_policy
    assert "class IconTitle" in components
    assert "def render_tinted_svg" in components
    assert "def make_tinted_svg_icon" in components
    assert "METRICS.metric_row_height" in components
    assert "root_layout.addWidget(self._build_header())" not in gui
    assert "def _build_header" not in gui
    assert "self.collect_page_header.add_action(self.header_status)" in gui
    assert "format_metric_integer(record.output_chars)" in gui
    assert "outcome_metric_state(record.outcome)" in gui
    assert "#MetricDivider" in theme
    assert "metric_row_height: int = 58" in theme
    assert "58 px" in reference

    required_assets = (
        "ui-setup.svg",
        "ui-last-run.svg",
        "ui-volume.svg",
        "ui-output.svg",
        "ui-coverage.svg",
        "ui-health.svg",
        "ui-paste-paths.svg",
        "ui-collect-copy.svg",
    )
    for asset_name in required_assets:
        assert (PROJECT_ROOT / "assets" / asset_name).is_file()

    m156 = roadmap[
        roadmap.index("## M15.6"):
        roadmap.index("## M15.7")
    ]
    assert "**Status: DONE**" in m156
    assert "### M15.6.1 — Icon Rendering and Visual Polish" in m156
    assert "official Lucide SVG files are tinted at runtime" in m156


def test_v130_responsive_collect_layout_is_registered() -> None:
    responsive_path = PROJECT_ROOT / "src" / "xcc" / "ui_responsive.py"
    sidebar_path = PROJECT_ROOT / "src" / "xcc" / "ui_sidebar.py"
    gui_path = PROJECT_ROOT / "src" / "xcc" / "gui.py"
    components_path = PROJECT_ROOT / "src" / "xcc" / "ui_components.py"
    theme_path = PROJECT_ROOT / "src" / "xcc" / "ui_theme.py"
    roadmap_path = PROJECT_ROOT / "docs" / "roadmap.md"

    assert responsive_path.is_file()
    assert sidebar_path.is_file()

    responsive = responsive_path.read_text(encoding="utf-8")
    sidebar = sidebar_path.read_text(encoding="utf-8")
    gui = gui_path.read_text(encoding="utf-8")
    components = components_path.read_text(encoding="utf-8")
    theme = theme_path.read_text(encoding="utf-8")
    roadmap = roadmap_path.read_text(encoding="utf-8")

    assert "class CollectLayoutMode" in responsive
    assert "class CollectHeightMode" in responsive
    assert "class CollectLayoutSpec" in responsive
    assert "class CollectGeometrySpec" in responsive
    assert "LARGE_CONTENT_BREAKPOINT = 1120" in responsive
    assert "MEDIUM_CONTENT_BREAKPOINT = 820" in responsive
    assert "MINIMUM_SUPPORTED_WINDOW_WIDTH = 920" in responsive
    assert "def collect_geometry_spec" in responsive
    assert "def collect_page_fits" in responsive

    assert "class SidebarNavButton" in sidebar
    assert "class SidebarNavigation" in sidebar
    assert "QListWidget" not in sidebar

    assert "def eventFilter" in gui
    assert "def _collect_viewport_size" in gui
    assert "def _apply_collect_geometry" in gui
    assert "collect_page_scroll.viewport().height()" in gui
    assert "self.collect_page_content.setMinimumHeight(0)" in gui
    assert "layout.addWidget(stats_card, 1)" in gui
    assert "layout.addWidget(metric, 1)" in gui
    assert "class ElidedLabel" in components
    assert "maximum_height" in components
    assert "#SidebarNavButton" in theme
    assert "#SidebarIdentity" in theme

    m157 = roadmap[
        roadmap.index("## M15.7"):
        roadmap.index("## M15.8")
    ]
    assert "**Status: DONE**" in m157
    assert "M15.7.5 SIDEBAR BRAND SCALE POLISH" in m157
    assert "### M15.7.2 — Geometry Architecture Reset and Sidebar Rebuild" in m157
    assert "### M15.7.3 — Mode Group and Sidebar Brand Composition" in m157
    assert "### M15.7.4 — Product Density and Branding Polish" in m157
    assert "### M15.7.5 — Sidebar Brand Scale Polish" in m157
    assert "content viewport" in m157
    assert "expanding Last Run" in m157
    assert "real navigation buttons" in m157
    assert "compact left-aligned radio group" in m157
    assert "complete the final validated polish at 64 px" in m157
    assert "balanced Setup and Last Run density" in m157
    assert "mode_group_max_width" in responsive
    assert "ModeSelectorGroup" in gui
    assert "SidebarBrandIcon" in sidebar
    assert "identity_mark" not in sidebar
    assert "#SidebarBrandMark" not in theme

def test_v130_sidebar_wheel_navigation_is_documented() -> None:
    sidebar = (PROJECT_ROOT / "src" / "xcc" / "ui_sidebar.py").read_text(
        encoding="utf-8"
    )
    readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
    architecture = (
        PROJECT_ROOT / "docs" / "ARCHITECTURE.md"
    ).read_text(encoding="utf-8")
    reference = (
        PROJECT_ROOT / "docs" / "UI_REFERENCE_v1.3.0.md"
    ).read_text(encoding="utf-8")
    roadmap = (PROJECT_ROOT / "docs" / "roadmap.md").read_text(
        encoding="utf-8"
    )

    assert "def _handle_wheel_event" in sidebar
    assert "setFocus(Qt.FocusReason.MouseFocusReason)" in sidebar
    assert "wheel navigation across the complete sidebar" in readme
    assert "## Sidebar interaction boundary" in architecture
    assert "no sidebar `QScrollArea` or visible scrollbar is created" in architecture
    assert "wheel navigation does not create a scrollbar or `QScrollArea`" in reference
    assert "M15.9.1 — Sidebar Wheel Navigation and Focus Synchronization" in roadmap

