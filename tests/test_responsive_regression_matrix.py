from __future__ import annotations

import pytest

from xcc.ui_responsive import (
    ABOUT_USEFUL_PAGE_MAX_WIDTH,
    DIALOG_WORK_AREA_MARGIN,
    HISTORY_USEFUL_PAGE_MAX_WIDTH,
    LARGE_CONTENT_BREAKPOINT,
    LARGE_USEFUL_PAGE_MAX_WIDTH,
    MEDIUM_CONTENT_BREAKPOINT,
    SETTINGS_TWO_COLUMN_BREAKPOINT,
    SETTINGS_USEFUL_PAGE_MAX_WIDTH,
    STANDARD_VIEWPORT_HEIGHT,
    TALL_VIEWPORT_HEIGHT,
    CollectHeightMode,
    CollectLayoutMode,
    about_page_spec,
    collect_geometry_spec,
    collect_height_mode,
    collect_layout_mode,
    collect_layout_spec,
    collect_page_width_spec,
    dialog_size_spec,
    history_page_spec,
    responsive_page_margin,
    settings_page_spec,
)


@pytest.mark.parametrize(
    ("width", "expected_mode"),
    (
        (MEDIUM_CONTENT_BREAKPOINT - 1, CollectLayoutMode.COMPACT),
        (MEDIUM_CONTENT_BREAKPOINT, CollectLayoutMode.MEDIUM),
        (MEDIUM_CONTENT_BREAKPOINT + 1, CollectLayoutMode.MEDIUM),
        (LARGE_CONTENT_BREAKPOINT - 1, CollectLayoutMode.MEDIUM),
        (LARGE_CONTENT_BREAKPOINT, CollectLayoutMode.LARGE),
        (LARGE_CONTENT_BREAKPOINT + 1, CollectLayoutMode.LARGE),
    ),
)
def test_width_breakpoint_triplets_select_expected_layout(
    width: int,
    expected_mode: CollectLayoutMode,
) -> None:
    assert collect_layout_mode(width) is expected_mode

    spec = collect_layout_spec(width)
    assert spec.mode is expected_mode

    if expected_mode is CollectLayoutMode.COMPACT:
        assert spec.mode_columns == 2
        assert spec.metric_columns == 2
        assert spec.source_actions_below is True
        assert spec.show_subtitle is False
        assert spec.show_source_helper is False
        assert spec.show_options_helper is False
    elif expected_mode is CollectLayoutMode.MEDIUM:
        assert spec.mode_columns == 4
        assert spec.metric_columns == 2
        assert spec.source_actions_below is True
        assert spec.show_subtitle is True
        assert spec.show_source_helper is True
        assert spec.show_options_helper is True
    else:
        assert spec.mode_columns == 4
        assert spec.metric_columns == 4
        assert spec.source_actions_below is False
        assert spec.show_subtitle is True
        assert spec.show_source_helper is True
        assert spec.show_options_helper is True


@pytest.mark.parametrize(
    ("height", "expected_mode"),
    (
        (STANDARD_VIEWPORT_HEIGHT - 1, CollectHeightMode.SHORT),
        (STANDARD_VIEWPORT_HEIGHT, CollectHeightMode.STANDARD),
        (STANDARD_VIEWPORT_HEIGHT + 1, CollectHeightMode.STANDARD),
        (TALL_VIEWPORT_HEIGHT - 1, CollectHeightMode.STANDARD),
        (TALL_VIEWPORT_HEIGHT, CollectHeightMode.TALL),
        (TALL_VIEWPORT_HEIGHT + 1, CollectHeightMode.TALL),
    ),
)
def test_height_threshold_triplets_select_expected_density(
    height: int,
    expected_mode: CollectHeightMode,
) -> None:
    assert collect_height_mode(height) is expected_mode

    for width_mode in CollectLayoutMode:
        spec = collect_layout_spec(
            {
                CollectLayoutMode.COMPACT: MEDIUM_CONTENT_BREAKPOINT - 1,
                CollectLayoutMode.MEDIUM: MEDIUM_CONTENT_BREAKPOINT,
                CollectLayoutMode.LARGE: LARGE_CONTENT_BREAKPOINT,
            }[width_mode]
        )
        geometry = collect_geometry_spec(spec, height)
        assert geometry.mode is expected_mode
        assert geometry.metric_min_height <= geometry.metric_preferred_height
        assert geometry.metric_preferred_height <= geometry.metric_max_height
        assert geometry.stats_card_min_height <= geometry.stats_card_max_height


@pytest.mark.parametrize(
    ("width", "expected_margin"),
    (
        (MEDIUM_CONTENT_BREAKPOINT - 1, 16),
        (MEDIUM_CONTENT_BREAKPOINT, 22),
        (MEDIUM_CONTENT_BREAKPOINT + 1, 22),
        (LARGE_CONTENT_BREAKPOINT - 1, 22),
        (LARGE_CONTENT_BREAKPOINT, 28),
        (LARGE_CONTENT_BREAKPOINT + 1, 28),
    ),
)
def test_shared_page_margin_uses_same_boundary_triplets(
    width: int,
    expected_margin: int,
) -> None:
    assert responsive_page_margin(width) == expected_margin


@pytest.mark.parametrize(
    ("width", "expected_columns"),
    (
        (SETTINGS_TWO_COLUMN_BREAKPOINT - 1, 1),
        (SETTINGS_TWO_COLUMN_BREAKPOINT, 2),
        (SETTINGS_TWO_COLUMN_BREAKPOINT + 1, 2),
    ),
)
def test_settings_column_breakpoint_triplet(
    width: int,
    expected_columns: int,
) -> None:
    spec = settings_page_spec(width)
    assert spec.columns == expected_columns
    assert spec.width.available_width == width


@pytest.mark.parametrize(
    ("width", "expected_columns"),
    (
        (MEDIUM_CONTENT_BREAKPOINT - 1, 2),
        (MEDIUM_CONTENT_BREAKPOINT, 4),
        (MEDIUM_CONTENT_BREAKPOINT + 1, 4),
    ),
)
def test_about_badge_breakpoint_triplet(
    width: int,
    expected_columns: int,
) -> None:
    spec = about_page_spec(width)
    assert spec.columns == expected_columns
    assert spec.width.available_width == width


@pytest.mark.parametrize(
    ("max_width", "spec_factory"),
    (
        (LARGE_USEFUL_PAGE_MAX_WIDTH, collect_page_width_spec),
        (SETTINGS_USEFUL_PAGE_MAX_WIDTH, lambda width: settings_page_spec(width).width),
        (HISTORY_USEFUL_PAGE_MAX_WIDTH, lambda width: history_page_spec(width).width),
        (ABOUT_USEFUL_PAGE_MAX_WIDTH, lambda width: about_page_spec(width).width),
    ),
)
def test_useful_width_cap_triplets_are_centered(
    max_width: int,
    spec_factory,
) -> None:
    below = spec_factory(max_width - 1)
    exact = spec_factory(max_width)
    above = spec_factory(max_width + 1)

    assert below.useful_width == max_width - 1
    assert below.left_inset == 0
    assert below.right_inset == 0

    assert exact.useful_width == max_width
    assert exact.left_inset == 0
    assert exact.right_inset == 0

    assert above.useful_width == max_width
    assert above.left_inset + above.right_inset == 1
    assert abs(above.left_inset - above.right_inset) <= 1


def test_sidebar_hysteresis_transition_triplets_are_explicit() -> None:
    compact_to_medium = MEDIUM_CONTENT_BREAKPOINT + (212 - 196)
    medium_to_large = LARGE_CONTENT_BREAKPOINT + (228 - 212)
    compact_to_large = LARGE_CONTENT_BREAKPOINT + (228 - 196)

    assert (
        collect_layout_mode(
            compact_to_medium - 1,
            current_mode=CollectLayoutMode.COMPACT,
        )
        is CollectLayoutMode.COMPACT
    )
    assert (
        collect_layout_mode(
            compact_to_medium,
            current_mode=CollectLayoutMode.COMPACT,
        )
        is CollectLayoutMode.MEDIUM
    )
    assert (
        collect_layout_mode(
            compact_to_medium + 1,
            current_mode=CollectLayoutMode.COMPACT,
        )
        is CollectLayoutMode.MEDIUM
    )

    assert (
        collect_layout_mode(
            medium_to_large - 1,
            current_mode=CollectLayoutMode.MEDIUM,
        )
        is CollectLayoutMode.MEDIUM
    )
    assert (
        collect_layout_mode(
            medium_to_large,
            current_mode=CollectLayoutMode.MEDIUM,
        )
        is CollectLayoutMode.LARGE
    )
    assert (
        collect_layout_mode(
            medium_to_large + 1,
            current_mode=CollectLayoutMode.MEDIUM,
        )
        is CollectLayoutMode.LARGE
    )

    assert (
        collect_layout_mode(
            compact_to_large - 1,
            current_mode=CollectLayoutMode.COMPACT,
        )
        is CollectLayoutMode.MEDIUM
    )
    assert (
        collect_layout_mode(
            compact_to_large,
            current_mode=CollectLayoutMode.COMPACT,
        )
        is CollectLayoutMode.LARGE
    )
    assert (
        collect_layout_mode(
            compact_to_large + 1,
            current_mode=CollectLayoutMode.COMPACT,
        )
        is CollectLayoutMode.LARGE
    )


@pytest.mark.parametrize(
    ("work_width", "work_height", "expected_width", "expected_height"),
    (
        # One logical pixel below the preferred-size threshold.
        (
            820 + (DIALOG_WORK_AREA_MARGIN * 2) - 1,
            590 + (DIALOG_WORK_AREA_MARGIN * 2) - 1,
            819,
            589,
        ),
        # Exact threshold.
        (
            820 + (DIALOG_WORK_AREA_MARGIN * 2),
            590 + (DIALOG_WORK_AREA_MARGIN * 2),
            820,
            590,
        ),
        # One logical pixel above the threshold must not enlarge the dialog.
        (
            820 + (DIALOG_WORK_AREA_MARGIN * 2) + 1,
            590 + (DIALOG_WORK_AREA_MARGIN * 2) + 1,
            820,
            590,
        ),
    ),
)
def test_dialog_preferred_size_boundary_triplet(
    work_width: int,
    work_height: int,
    expected_width: int,
    expected_height: int,
) -> None:
    spec = dialog_size_spec(
        work_width,
        work_height,
        preferred_width=820,
        preferred_height=590,
        minimum_width=640,
        minimum_height=420,
    )

    assert spec.width == expected_width
    assert spec.height == expected_height
    assert spec.width <= spec.usable_width
    assert spec.height <= spec.usable_height
