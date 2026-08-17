from __future__ import annotations

import pytest

from xcc.ui_responsive import (
    ABOUT_USEFUL_PAGE_MAX_WIDTH,
    DIALOG_WORK_AREA_MARGIN,
    LARGE_CONTENT_BREAKPOINT,
    WORKBENCH_HARD_MAX_WIDTH,
    WORKBENCH_REFERENCE_PAGE_WIDTH,
    MEDIUM_CONTENT_BREAKPOINT,
    SETTINGS_TWO_COLUMN_BREAKPOINT,
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
    "spec_factory",
    (
        collect_page_width_spec,
        lambda width: settings_page_spec(width).width,
        lambda width: history_page_spec(width).width,
    ),
)
def test_workbench_reference_boundary_starts_progressive_outer_space(
    spec_factory,
) -> None:
    below = spec_factory(WORKBENCH_REFERENCE_PAGE_WIDTH - 1)
    exact = spec_factory(WORKBENCH_REFERENCE_PAGE_WIDTH)
    above = spec_factory(WORKBENCH_REFERENCE_PAGE_WIDTH + 1)

    assert below.useful_width == WORKBENCH_REFERENCE_PAGE_WIDTH - 1
    assert below.left_inset == 0
    assert below.right_inset == 0

    assert exact.useful_width == WORKBENCH_REFERENCE_PAGE_WIDTH
    assert exact.left_inset == 0
    assert exact.right_inset == 0

    # With integer 3/4 growth, the first extra logical pixel becomes centered
    # breathing room. Larger viewports then expand progressively.
    assert above.useful_width == WORKBENCH_REFERENCE_PAGE_WIDTH
    assert above.left_inset + above.right_inset == 1


def test_about_fixed_readability_cap_triplet_remains_centered() -> None:
    below = about_page_spec(ABOUT_USEFUL_PAGE_MAX_WIDTH - 1).width
    exact = about_page_spec(ABOUT_USEFUL_PAGE_MAX_WIDTH).width
    above = about_page_spec(ABOUT_USEFUL_PAGE_MAX_WIDTH + 1).width

    assert below.useful_width == ABOUT_USEFUL_PAGE_MAX_WIDTH - 1
    assert exact.useful_width == ABOUT_USEFUL_PAGE_MAX_WIDTH
    assert above.useful_width == ABOUT_USEFUL_PAGE_MAX_WIDTH
    assert above.left_inset + above.right_inset == 1


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



@pytest.mark.parametrize(
    (
        "label",
        "physical_width",
        "display_scale",
        "expected_mode",
        "expected_content_width",
        "expected_useful_width",
    ),
    (
        ("1366x768 @ 100%", 1366, 1.00, CollectLayoutMode.LARGE, 1138, 1138),
        ("1920x1080 @ 100%", 1920, 1.00, CollectLayoutMode.LARGE, 1692, 1692),
        ("1920x1080 @ 125%", 1920, 1.25, CollectLayoutMode.LARGE, 1308, 1308),
        ("1920x1080 @ 150%", 1920, 1.50, CollectLayoutMode.MEDIUM, 1068, 1068),
        ("2560x1440 @ 100%", 2560, 1.00, CollectLayoutMode.LARGE, 2332, 2172),
        ("2560x1440 @ 125%", 2560, 1.25, CollectLayoutMode.LARGE, 1820, 1788),
        ("2560x1440 @ 150%", 2560, 1.50, CollectLayoutMode.LARGE, 1479, 1479),
        ("3840x2160 @ 100%", 3840, 1.00, CollectLayoutMode.LARGE, 3612, 3132),
        ("3840x2160 @ 125%", 3840, 1.25, CollectLayoutMode.LARGE, 2844, 2556),
        ("3840x2160 @ 150%", 3840, 1.50, CollectLayoutMode.LARGE, 2332, 2172),
    ),
)
def test_major_windows_resolution_scaling_matrix_uses_qt_logical_width_once(
    label: str,
    physical_width: int,
    display_scale: float,
    expected_mode: CollectLayoutMode,
    expected_content_width: int,
    expected_useful_width: int,
) -> None:
    """Freeze the common-resolution/scaling behavior in Qt logical space.

    Production code never branches on these physical resolutions or scales.
    This matrix only translates common Windows setups into representative Qt
    logical widths and verifies the progressive Full-HD-referenced workbench.
    """

    del label
    logical_window_width = round(physical_width / display_scale)

    # Resolve the sidebar/content pair to the same fixed point used by the
    # application: the selected layout mode owns its sidebar width.
    resolved = None
    for sidebar_width in (196, 212, 228):
        content_width = max(0, logical_window_width - sidebar_width)
        spec = collect_layout_spec(content_width)
        if spec.sidebar_width == sidebar_width:
            resolved = (content_width, spec)
            break

    assert resolved is not None
    content_width, layout_spec = resolved
    page_width = collect_page_width_spec(content_width)

    assert layout_spec.mode is expected_mode
    assert content_width == expected_content_width
    assert page_width.useful_width == expected_useful_width
    assert page_width.useful_width <= WORKBENCH_HARD_MAX_WIDTH
    assert (
        page_width.left_inset
        + page_width.useful_width
        + page_width.right_inset
        == content_width
    )
