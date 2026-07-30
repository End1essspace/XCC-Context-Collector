from __future__ import annotations

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
    assert PALETTE.accent_border == "#57471F"
    assert PALETTE.accent == "#D2A533"
    assert PALETTE.accent_hover == "#E0B440"
    assert PALETTE.success == "#69B985"
    assert PALETTE.warning == "#D5A13B"
    assert PALETTE.error == "#D86C6C"
    assert PALETTE.neutral == "#90959D"


def test_ui_metrics_keep_supported_geometry_contract() -> None:
    assert METRICS.control_height == 40
    assert METRICS.primary_action_height == 52
    assert METRICS.footer_height == 36
    assert METRICS.sidebar_width == 216
    assert METRICS.metric_row_height == 58
    assert METRICS.card_radius == 14
    assert METRICS.control_radius == 10


def test_application_stylesheet_contains_shared_component_selectors() -> None:
    stylesheet = build_application_stylesheet()

    for selector in (
        "QMainWindow",
        "#Sidebar",
        "#CollectPage",
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
    assert "@accent" not in stylesheet
    assert "@primary" not in stylesheet


def test_tray_menu_uses_shared_palette() -> None:
    stylesheet = build_tray_menu_stylesheet()

    assert "QMenu::item:selected" in stylesheet
    assert PALETTE.shell_surface in stylesheet
    assert PALETTE.accent in stylesheet
    assert PALETTE.accent_border in stylesheet
    assert PALETTE.quiet_border in stylesheet
    assert "@" not in stylesheet
