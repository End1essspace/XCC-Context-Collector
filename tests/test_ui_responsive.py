from __future__ import annotations

import pytest

from xcc.ui_responsive import (
    ABOUT_USEFUL_PAGE_MAX_WIDTH,
    DIALOG_WORK_AREA_MARGIN,
    INLINE_PAGE_HEADER_HEIGHT,
    LARGE_CONTENT_BREAKPOINT,
    WORKBENCH_HARD_MAX_WIDTH,
    WORKBENCH_REFERENCE_PAGE_WIDTH,
    WORKBENCH_WIDE_EXPANSION_DENOMINATOR,
    WORKBENCH_WIDE_EXPANSION_NUMERATOR,
    MEDIUM_CONTENT_BREAKPOINT,
    MINIMUM_SUPPORTED_WINDOW_HEIGHT,
    MINIMUM_SUPPORTED_WINDOW_WIDTH,
    SETTINGS_TWO_COLUMN_BREAKPOINT,
    STANDARD_VIEWPORT_HEIGHT,
    TALL_VIEWPORT_HEIGHT,
    CollectHeightMode,
    CollectLayoutMode,
    about_page_spec,
    bounded_page_width,
    centered_page_width_spec,
    collect_content_min_height,
    collect_geometry_spec,
    collect_height_mode,
    collect_page_width_spec,
    collect_useful_page_width,
    collect_layout_mode,
    progressive_page_width_spec,
    dialog_size_spec,
    collect_layout_spec,
    history_page_spec,
    responsive_page_margin,
    settings_page_spec,
)


def test_collect_width_breakpoints_use_the_content_viewport() -> None:
    assert MINIMUM_SUPPORTED_WINDOW_WIDTH == 920
    assert MINIMUM_SUPPORTED_WINDOW_HEIGHT == 620
    assert MEDIUM_CONTENT_BREAKPOINT == 820
    assert LARGE_CONTENT_BREAKPOINT == 1120

    assert collect_layout_mode(819) is CollectLayoutMode.COMPACT
    assert collect_layout_mode(820) is CollectLayoutMode.MEDIUM
    assert collect_layout_mode(1119) is CollectLayoutMode.MEDIUM
    assert collect_layout_mode(1120) is CollectLayoutMode.LARGE
    assert collect_layout_mode(2560) is CollectLayoutMode.LARGE


def test_large_workbench_expands_progressively_without_resolution_modes() -> None:
    assert WORKBENCH_REFERENCE_PAGE_WIDTH == 1692
    assert WORKBENCH_WIDE_EXPANSION_NUMERATOR == 3
    assert WORKBENCH_WIDE_EXPANSION_DENOMINATOR == 4
    assert WORKBENCH_HARD_MAX_WIDTH == 3200

    # The generic fixed-cap helper remains available for intentionally bounded
    # information surfaces such as About.
    assert bounded_page_width(0, max_width=1692) == 0
    assert bounded_page_width(1692, max_width=1692) == 1692
    assert bounded_page_width(1693, max_width=1692) == 1692

    # Full HD is unchanged. Wider workbenches consume 75% of extra logical
    # width, leaving 25% as centered breathing room.
    assert collect_useful_page_width(1692) == 1692
    assert collect_useful_page_width(1820) == 1788
    assert collect_useful_page_width(2332) == 2172
    assert collect_useful_page_width(3612) == 3132
    assert collect_useful_page_width(5000) == WORKBENCH_HARD_MAX_WIDTH

    # Width distribution never creates a QHD/4K-specific layout mode.
    assert collect_layout_mode(1692) is CollectLayoutMode.LARGE
    assert collect_layout_mode(2560) is CollectLayoutMode.LARGE
    assert collect_layout_mode(3840) is CollectLayoutMode.LARGE


def test_bounded_page_width_rejects_invalid_maximum() -> None:
    with pytest.raises(ValueError, match="max_width must be greater than 0"):
        bounded_page_width(1000, max_width=0)


def test_progressive_page_width_validates_calibration_contract() -> None:
    with pytest.raises(ValueError, match="reference_width"):
        progressive_page_width_spec(2000, reference_width=0)

    with pytest.raises(ValueError, match="hard_max_width"):
        progressive_page_width_spec(
            2000,
            reference_width=1692,
            hard_max_width=1600,
        )

    with pytest.raises(ValueError, match="expansion_denominator"):
        progressive_page_width_spec(2000, expansion_denominator=0)

    with pytest.raises(ValueError, match="expansion_numerator"):
        progressive_page_width_spec(
            2000,
            expansion_numerator=5,
            expansion_denominator=4,
        )


def test_dialog_size_spec_preserves_preferred_size_when_work_area_allows() -> None:
    spec = dialog_size_spec(
        1920,
        1040,
        preferred_width=820,
        preferred_height=590,
        minimum_width=640,
        minimum_height=420,
    )

    assert DIALOG_WORK_AREA_MARGIN == 24
    assert spec.usable_width == 1872
    assert spec.usable_height == 992
    assert spec.minimum_width == 640
    assert spec.minimum_height == 420
    assert spec.width == 820
    assert spec.height == 590


def test_dialog_size_spec_clamps_to_constrained_work_area() -> None:
    spec = dialog_size_spec(
        700,
        500,
        preferred_width=860,
        preferred_height=610,
        minimum_width=640,
        minimum_height=420,
    )

    assert spec.usable_width == 652
    assert spec.usable_height == 452
    assert spec.minimum_width == 640
    assert spec.minimum_height == 420
    assert spec.width == 652
    assert spec.height == 452

    tiny = dialog_size_spec(
        500,
        350,
        preferred_width=860,
        preferred_height=610,
        minimum_width=640,
        minimum_height=420,
    )
    assert tiny.minimum_width == tiny.usable_width == 452
    assert tiny.minimum_height == tiny.usable_height == 302
    assert tiny.width == 452
    assert tiny.height == 302


def test_dialog_size_spec_rejects_invalid_geometry_contract() -> None:
    with pytest.raises(ValueError, match="preferred dialog size"):
        dialog_size_spec(
            1920,
            1080,
            preferred_width=0,
            preferred_height=590,
            minimum_width=640,
            minimum_height=420,
        )

    with pytest.raises(ValueError, match="minimum dialog size"):
        dialog_size_spec(
            1920,
            1080,
            preferred_width=820,
            preferred_height=590,
            minimum_width=0,
            minimum_height=420,
        )

    with pytest.raises(ValueError, match="edge_margin"):
        dialog_size_spec(
            1920,
            1080,
            preferred_width=820,
            preferred_height=590,
            minimum_width=640,
            minimum_height=420,
            edge_margin=-1,
        )


def test_centered_page_width_spec_distributes_only_excess_width() -> None:
    narrow = centered_page_width_spec(1200, max_width=1692)
    assert narrow.available_width == 1200
    assert narrow.useful_width == 1200
    assert narrow.left_inset == 0
    assert narrow.right_inset == 0

    wide = centered_page_width_spec(2001, max_width=1692)
    assert wide.available_width == 2001
    assert wide.useful_width == 1692
    assert wide.left_inset == 154
    assert wide.right_inset == 155
    assert (
        wide.left_inset + wide.useful_width + wide.right_inset
        == wide.available_width
    )

    collect = collect_page_width_spec(2560)
    assert collect.useful_width == 2343
    assert collect.left_inset == 108
    assert collect.right_inset == 109


def test_sidebar_width_hysteresis_prevents_breakpoint_oscillation() -> None:
    assert (
        collect_layout_mode(
            1124,
            current_mode=CollectLayoutMode.MEDIUM,
        )
        is CollectLayoutMode.MEDIUM
    )
    assert (
        collect_layout_mode(
            1136,
            current_mode=CollectLayoutMode.MEDIUM,
        )
        is CollectLayoutMode.LARGE
    )
    assert (
        collect_layout_mode(
            824,
            current_mode=CollectLayoutMode.COMPACT,
        )
        is CollectLayoutMode.COMPACT
    )
    assert (
        collect_layout_mode(
            836,
            current_mode=CollectLayoutMode.COMPACT,
        )
        is CollectLayoutMode.MEDIUM
    )


def test_height_density_is_independent_from_width_layout() -> None:
    assert STANDARD_VIEWPORT_HEIGHT == 700
    assert TALL_VIEWPORT_HEIGHT == 800

    assert collect_height_mode(699) is CollectHeightMode.SHORT
    assert collect_height_mode(700) is CollectHeightMode.STANDARD
    assert collect_height_mode(799) is CollectHeightMode.STANDARD
    assert collect_height_mode(800) is CollectHeightMode.TALL


def test_large_tall_layout_fits_a_normal_maximized_viewport() -> None:
    spec = collect_layout_spec(1400)
    geometry = collect_geometry_spec(spec, 835)

    assert spec.mode is CollectLayoutMode.LARGE
    assert spec.metric_columns == 4
    assert spec.mode_group_max_width == 650
    assert spec.mode_horizontal_gap == 20
    assert spec.mode_vertical_gap == 8
    assert spec.source_actions_below is False
    assert spec.sidebar_width == 228
    assert spec.primary_action_height == 54
    assert geometry.mode is CollectHeightMode.TALL
    assert geometry.setup_card_height == 278
    assert geometry.stats_card_min_height == 286
    assert geometry.stats_card_max_height == 334
    assert geometry.metric_min_height == 54
    assert geometry.metric_preferred_height == 58
    assert geometry.metric_max_height == 60
    assert INLINE_PAGE_HEADER_HEIGHT == 42
    assert collect_content_min_height(spec, geometry) == 736
    assert collect_content_min_height(spec, geometry) <= 835


def test_medium_layout_wraps_source_and_uses_two_by_two_metrics() -> None:
    spec = collect_layout_spec(980)
    geometry = collect_geometry_spec(spec, 760)

    assert spec.mode is CollectLayoutMode.MEDIUM
    assert spec.metric_columns == 2
    assert spec.mode_columns == 4
    assert spec.mode_group_max_width == 620
    assert spec.mode_horizontal_gap == 20
    assert spec.mode_vertical_gap == 8
    assert spec.source_actions_below is True
    assert spec.sidebar_width == 212
    assert geometry.mode is CollectHeightMode.STANDARD
    assert geometry.setup_card_height == 296
    assert geometry.stats_card_min_height == 460
    assert geometry.stats_card_max_height == 514
    assert collect_content_min_height(spec, geometry) > 760


def test_compact_layout_keeps_every_control_reachable_by_vertical_scroll() -> None:
    spec = collect_layout_spec(724)
    geometry = collect_geometry_spec(spec, 555)

    assert spec.mode is CollectLayoutMode.COMPACT
    assert spec.metric_columns == 2
    assert spec.mode_columns == 2
    assert spec.mode_group_max_width == 520
    assert spec.mode_horizontal_gap == 18
    assert spec.mode_vertical_gap == 10
    assert spec.source_actions_below is True
    assert spec.page_margin == 16
    assert spec.sidebar_width == 196
    assert spec.show_subtitle is False
    assert spec.show_source_helper is False
    assert spec.show_options_helper is False
    assert geometry.mode is CollectHeightMode.SHORT
    assert geometry.setup_card_height == 254
    assert geometry.stats_card_min_height == 424
    assert geometry.stats_card_max_height == 474
    assert collect_content_min_height(spec, geometry) == 818
    assert collect_content_min_height(spec, geometry) > 555


def test_height_changes_recalculate_geometry_inside_one_width_mode() -> None:
    spec = collect_layout_spec(1400)
    tall = collect_geometry_spec(spec, 850)
    standard = collect_geometry_spec(spec, 750)
    short = collect_geometry_spec(spec, 650)

    assert tall.mode is CollectHeightMode.TALL
    assert standard.mode is CollectHeightMode.STANDARD
    assert short.mode is CollectHeightMode.SHORT
    assert tall.setup_card_height > standard.setup_card_height > short.setup_card_height
    assert (
        tall.metric_preferred_height
        > standard.metric_preferred_height
        > short.metric_preferred_height
    )

def test_non_collect_surface_policy_reflows_and_bounds_by_viewport() -> None:
    assert SETTINGS_TWO_COLUMN_BREAKPOINT == LARGE_CONTENT_BREAKPOINT
    assert ABOUT_USEFUL_PAGE_MAX_WIDTH == 1320

    assert responsive_page_margin(819) == 16
    assert responsive_page_margin(820) == 22
    assert responsive_page_margin(1119) == 22
    assert responsive_page_margin(1120) == 28

    assert settings_page_spec(1119).columns == 1
    assert settings_page_spec(1120).columns == 2
    assert settings_page_spec(2560).width.useful_width == 2343

    assert history_page_spec(2560).width.useful_width == 2343

    compact_about = about_page_spec(819)
    assert compact_about.columns == 2
    assert compact_about.page_margin == 16

    large_about = about_page_spec(2560)
    assert large_about.columns == 4
    assert large_about.width.useful_width == ABOUT_USEFUL_PAGE_MAX_WIDTH
    assert large_about.width.left_inset == 620
    assert large_about.width.right_inset == 620

    scaled_about = about_page_spec(2560, interface_scale=1.25)
    assert scaled_about.columns == 4
    assert scaled_about.width.useful_width == 1650
    assert scaled_about.width.left_inset == 455
    assert scaled_about.width.right_inset == 455


def test_about_interface_scale_rejects_invalid_multiplier() -> None:
    with pytest.raises(ValueError, match="interface_scale"):
        about_page_spec(1600, interface_scale=0)
