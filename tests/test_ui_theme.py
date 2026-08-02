from __future__ import annotations

import re

from xcc.ui_theme import (
    METRICS,
    PALETTE,
    build_application_stylesheet,
    build_tray_menu_stylesheet,
)


def test_ui_palette_matches_frozen_v130_contract() -> None:
    assert PALETTE.window_background == "#0E0F11"
    assert PALETTE.shell_surface == "#141517"
    assert PALETTE.sidebar_surface == "#111214"
    assert PALETTE.card_surface == "#17181A"
    assert PALETTE.raised_surface == "#1B1C1F"
    assert PALETTE.input_surface == "#101113"
    assert PALETTE.selected_surface == "#242016"
    assert PALETTE.hover_surface == "#1A1916"
    assert PALETTE.quiet_border == "#302D26"
    assert PALETTE.card_border == "#36352F"
    assert PALETTE.metric_border == "#2D3034"
    assert PALETTE.selected_border == "#3B3528"
    assert PALETTE.frame_border == "#35393E"
    assert PALETTE.shell_divider == "#25282C"
    assert PALETTE.control_border == "#3A3D42"
    assert PALETTE.metric_divider == "#25272A"
    assert PALETTE.accent_border == "#57471F"
    assert PALETTE.accent == "#D2A533"
    assert PALETTE.accent_hover == "#E0B440"
    assert PALETTE.success == "#69B985"
    assert PALETTE.warning == "#D5A13B"
    assert PALETTE.error == "#D86C6C"
    assert PALETTE.neutral == "#90959D"
    assert PALETTE.status_text == "#BEC2C8"


def test_ui_metrics_keep_supported_geometry_contract() -> None:
    assert METRICS.control_height == 40
    assert METRICS.primary_action_height == 52
    assert METRICS.footer_height == 36
    assert METRICS.window_titlebar_height == 48
    assert METRICS.sidebar_brand_header_height == 48
    assert METRICS.sidebar_brand_header_height == METRICS.window_titlebar_height
    assert METRICS.window_control_width == 52
    assert METRICS.sidebar_width == 228
    assert METRICS.metric_row_height == 58
    assert METRICS.card_radius == 14
    assert METRICS.control_radius == 10
    assert METRICS.page_top_margin == 18
    assert METRICS.standard_gap == 14


def test_application_stylesheet_contains_shared_component_selectors() -> None:
    stylesheet = build_application_stylesheet()

    for selector in (
        "QMainWindow",
        "#WindowFrame",
        "#SidebarBrandHeader",
        "#WindowTitleBar",
        '#WindowFrame[maximized="true"]',
        "#WindowVersionCapsule",
        "#WindowControlButton",
        "#ShellBody",
        "#Sidebar",
        "#StatusBar",
        "#SidebarBrandIcon",
        "#SidebarBrandLabel",
        "#SidebarNavButton",
        "#ModeSelectorGroup",
        '#SidebarNavButton[selected="true"]',
        "#CollectPage",
        "#CollectPageScroll",
        "#PageHeader",
        "#PageHeaderActions",
        "#Card",
        "#PrimaryButton",
        "#SecondaryButton",
        "#MetricCapsule",
        "#MetricDivider",
        "#MetricGroupHeader",
        "#MetricGroupIcon",
        "#StatusCapsule",
        "#RuntimeStatusCapsule",
        "#RuntimeStatusDot",
        "#FooterStatusDot",
        "#HelperText",
        "#SourceHelperText",
        "#OptionsHelperText",
        '#SourceInputBox[reviewable="true"]',
        "#PastePathsButton",
        "#SelectSourceButton",
        "#PastePathsDialog",
        "#SelectedFilesReviewDialog",
        "#DialogHeader",
        "#DialogSection",
        "#DialogSectionTitle",
        "#DialogSectionMeta",
        "#DialogFooter",
        "#DialogSummary",
        '#DialogSummary[state="success"]',
        '#DialogSummary[state="warning"]',
        '#DialogSummary[state="error"]',
        "#DialogPrimaryButton",
        "#DialogSecondaryButton",
        "#DialogQuietButton",
        '#ReviewRootInput[scope="mixed"]',
        "#SelectedFilesReviewList",
        '#MetricValue[state="success"]',
        '#MetricValue[state="warning"]',
        '#MetricValue[state="error"]',
        '#MetricValue[state="neutral"]',
        '#RuntimeStatusDot[state="success"]',
        '#FooterStatusDot[state="warning"]',
    ):
        assert selector in stylesheet

    assert PALETTE.window_background in stylesheet
    assert PALETTE.accent in stylesheet
    assert PALETTE.success in stylesheet
    assert PALETTE.error in stylesheet
    assert "qlineargradient" in stylesheet
    assert "#SidebarBrandMark" not in stylesheet
    assert "#SidebarIdentity" not in stylesheet
    assert "#WindowBrandIcon" not in stylesheet
    assert "#WindowBrandTitle" not in stylesheet
    assert 'border-radius: 7px;' in stylesheet
    assert '#WindowControlButton[role="close"]' in stylesheet
    assert '#WindowControlButton[role="close"][maximized="true"]' not in stylesheet
    assert "font-size: 11.25pt" in stylesheet
    assert not re.search(r"font-size:\s*[^;]*px", stylesheet)
    assert "min-height: 42px" in stylesheet
    assert "#WindowControlButton:focus" not in stylesheet
    assert f"border: 1px solid {PALETTE.frame_border};" in stylesheet
    assert stylesheet.count(f"border-bottom: 1px solid {PALETTE.shell_divider};") == 2
    assert stylesheet.count(f"border-top: 1px solid {PALETTE.shell_divider};") == 1
    assert f"border-right: 1px solid {PALETTE.shell_divider};" in stylesheet
    assert f"background: {PALETTE.metric_divider};" in stylesheet
    assert stylesheet.count(f"border: 1px solid {PALETTE.control_border};") >= 6
    assert "#484238" not in stylesheet
    assert "#2A2D32" not in stylesheet
    assert "#SidebarFooter" not in stylesheet

    for selector in (
        "QLineEdit",
        "QPushButton",
        "#SourceInputBox",
        "#SelectSourceButton",
        "#ClearSourceButton",
    ):
        match = re.search(
            rf"(?ms)^{re.escape(selector)}\s*\{{(?P<body>.*?)^\}}",
            stylesheet,
        )
        assert match is not None
        assert f"border: 1px solid {PALETTE.control_border};" in match.group("body")

    assert "#B68225" in stylesheet
    assert "#C89B30" in stylesheet
    assert "#BF942F" in stylesheet
    assert "#DDB342" in stylesheet
    assert "#E5BC49" in stylesheet
    assert "stop: 0.48" in stylesheet
    assert "#D8AD42" not in stylesheet
    assert "#PrimaryButton:focus" in stylesheet
    assert "#DialogPrimaryButton:focus" in stylesheet
    assert "#ClearSourceButton:focus" in stylesheet
    assert "#SourceInputEmbedded:focus" in stylesheet
    assert "QLineEdit:disabled" in stylesheet
    assert "QRadioButton:disabled" in stylesheet
    assert "@accent" not in stylesheet
    assert "@primary" not in stylesheet



def test_content_canvas_and_header_backgrounds_are_unified() -> None:
    stylesheet = build_application_stylesheet()

    assert '#101216' not in stylesheet
    assert '#0C0E11' not in stylesheet

    for selector in ("#SidebarBrandHeader", "#WindowTitleBar"):
        header_rule = re.search(
            rf'(?ms)^{re.escape(selector)}\s*\{{(?P<body>.*?)^\}}',
            stylesheet,
        )
        assert header_rule is not None
        assert f'background: {PALETTE.shell_surface};' in header_rule.group('body')
        assert f'border-bottom: 1px solid {PALETTE.shell_divider};' in header_rule.group('body')

    content_rule = re.search(
        r'(?ms)^#CollectPage,\n#HistoryPage,\n#SettingsPage,\n#AboutPage,\n#CollectPageScroll,\n#CollectPageScroll > QWidget,\n#CollectPageScroll > QWidget > QWidget\s*\{(?P<body>.*?)^\}',
        stylesheet,
    )
    assert content_rule is not None
    assert 'background: transparent;' in content_rule.group('body')
    assert 'border: none;' in content_rule.group('body')

    footer_rule = re.search(
        r'(?ms)^#StatusBar\s*\{(?P<body>.*?)^\}',
        stylesheet,
    )
    assert footer_rule is not None
    assert f'background: {PALETTE.shell_surface};' in footer_rule.group('body')
    assert f'border-top: 1px solid {PALETTE.shell_divider};' in footer_rule.group('body')
    assert 'border-bottom-left-radius: 11px;' in footer_rule.group('body')
    assert 'border-bottom-right-radius: 11px;' in footer_rule.group('body')
    assert '#SidebarFooter' not in stylesheet

def test_final_polish_keeps_resting_surfaces_quiet_and_states_clear() -> None:
    stylesheet = build_application_stylesheet()

    def rule(selector: str) -> str:
        match = re.search(
            rf"(?ms)^{re.escape(selector)}\s*\{{(?P<body>.*?)^\}}",
            stylesheet,
        )
        assert match is not None
        return match.group("body")

    brand_lockup = rule("#SidebarBrandLabel")
    assert "color: #F2F4F7;" in brand_lockup
    assert "font-size: 11.25pt;" in brand_lockup
    assert "font-weight: 700;" in brand_lockup
    assert "#SidebarBrandTitle" not in stylesheet
    assert "#SidebarBrandSubtitle" not in stylesheet
    assert "#SidebarBrandSeparator" not in stylesheet

    section_label = rule("#SidebarSectionLabel")
    assert f"color: {PALETTE.muted_text};" in section_label

    selected_nav = rule('#SidebarNavButton[selected="true"]')
    assert f"border: 1px solid {PALETTE.selected_border};" in selected_nav
    assert f"border-left: 3px solid {PALETTE.accent};" in selected_nav

    card = rule("#Card")
    assert f"border: 1px solid {PALETTE.card_border};" in card

    metric = rule("#MetricCapsule")
    assert f"border: 1px solid {PALETTE.metric_border};" in metric
    assert "stop: 0 #1C1E22" in metric
    assert "stop: 1 #181A1D" in metric

    footer = rule("#StatusText")
    assert f"color: {PALETTE.status_text};" in footer
    assert "font-size: 8.25pt;" in footer

    primary = rule("#PrimaryButton")
    assert "stop: 0 #D3AA3C" in primary
    assert "stop: 0.48 #C89B30" in primary
    assert "stop: 1 #B68225" in primary
    assert "border: 1px solid #BF942F;" in primary

    subtitle = rule("#PageSubtitle")
    assert "padding: 3px 0px 0px 0px;" in subtitle

    assert "@card_border" not in stylesheet
    assert "@metric_border" not in stylesheet
    assert "@selected_border" not in stylesheet
    assert "@status_text" not in stylesheet


def test_tray_menu_uses_shared_palette() -> None:
    stylesheet = build_tray_menu_stylesheet()

    assert "QMenu::item:selected" in stylesheet
    assert PALETTE.shell_surface in stylesheet
    assert PALETTE.accent in stylesheet
    assert PALETTE.accent_border in stylesheet
    assert PALETTE.quiet_border in stylesheet
    assert not re.search(r"font-size:\s*[^;]*px", stylesheet)
    assert "@" not in stylesheet


def test_custom_header_styles_drop_legacy_subtitle_and_footer_version() -> None:
    stylesheet = build_application_stylesheet()

    assert "#WindowBrandSubtitle" not in stylesheet
    assert "#StatusVersion" not in stylesheet

