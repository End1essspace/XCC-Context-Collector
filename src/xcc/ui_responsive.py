from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


LARGE_CONTENT_BREAKPOINT = 1120
MEDIUM_CONTENT_BREAKPOINT = 820
MINIMUM_SUPPORTED_WINDOW_WIDTH = 920
MINIMUM_SUPPORTED_WINDOW_HEIGHT = 620

# Logical page-width cap calibrated from the approved maximized v1.3.0
# Full HD composition: 1920 logical window width - 228 logical sidebar width.
# This is a useful-width bound, not a monitor-resolution breakpoint.
LARGE_USEFUL_PAGE_MAX_WIDTH = 1692

INLINE_PAGE_HEADER_HEIGHT = 42
COLLECT_PAGE_WIDGET_GAPS = 3

TALL_VIEWPORT_HEIGHT = 800
STANDARD_VIEWPORT_HEIGHT = 700


class CollectLayoutMode(str, Enum):
    """Width-driven collect-page arrangements based on content viewport size."""

    LARGE = "large"
    MEDIUM = "medium"
    COMPACT = "compact"


class CollectHeightMode(str, Enum):
    """Height-driven density used independently from the width arrangement."""

    TALL = "tall"
    STANDARD = "standard"
    SHORT = "short"


@dataclass(frozen=True, slots=True)
class CollectLayoutSpec:
    mode: CollectLayoutMode
    page_margin: int
    sidebar_width: int
    mode_columns: int
    mode_group_max_width: int
    mode_horizontal_gap: int
    mode_vertical_gap: int
    source_actions_below: bool
    metric_columns: int
    metric_horizontal_padding: int
    metric_group_gap: int
    primary_action_height: int
    show_subtitle: bool
    show_source_helper: bool
    show_options_helper: bool


@dataclass(frozen=True, slots=True)
class CollectGeometrySpec:
    mode: CollectHeightMode
    page_top_margin: int
    page_bottom_margin: int
    page_gap: int
    setup_card_height: int
    stats_card_min_height: int
    stats_card_max_height: int
    metric_min_height: int
    metric_preferred_height: int
    metric_max_height: int


@dataclass(frozen=True, slots=True)
class PageWidthSpec:
    """Centered logical page-width distribution inside a viewport."""

    available_width: int
    useful_width: int
    left_inset: int
    right_inset: int


_LAYOUT_SPECS = {
    CollectLayoutMode.LARGE: CollectLayoutSpec(
        mode=CollectLayoutMode.LARGE,
        page_margin=28,
        sidebar_width=228,
        mode_columns=4,
        mode_group_max_width=650,
        mode_horizontal_gap=20,
        mode_vertical_gap=8,
        source_actions_below=False,
        metric_columns=4,
        metric_horizontal_padding=14,
        metric_group_gap=14,
        primary_action_height=54,
        show_subtitle=True,
        show_source_helper=True,
        show_options_helper=True,
    ),
    CollectLayoutMode.MEDIUM: CollectLayoutSpec(
        mode=CollectLayoutMode.MEDIUM,
        page_margin=22,
        sidebar_width=212,
        mode_columns=4,
        mode_group_max_width=620,
        mode_horizontal_gap=20,
        mode_vertical_gap=8,
        source_actions_below=True,
        metric_columns=2,
        metric_horizontal_padding=13,
        metric_group_gap=14,
        primary_action_height=52,
        show_subtitle=True,
        show_source_helper=True,
        show_options_helper=True,
    ),
    CollectLayoutMode.COMPACT: CollectLayoutSpec(
        mode=CollectLayoutMode.COMPACT,
        page_margin=16,
        sidebar_width=196,
        mode_columns=2,
        mode_group_max_width=520,
        mode_horizontal_gap=18,
        mode_vertical_gap=10,
        source_actions_below=True,
        metric_columns=2,
        metric_horizontal_padding=12,
        metric_group_gap=12,
        primary_action_height=48,
        show_subtitle=False,
        show_source_helper=False,
        show_options_helper=False,
    ),
}


_GEOMETRY_SPECS = {
    (CollectLayoutMode.LARGE, CollectHeightMode.TALL): CollectGeometrySpec(
        mode=CollectHeightMode.TALL,
        page_top_margin=18,
        page_bottom_margin=16,
        page_gap=14,
        setup_card_height=278,
        stats_card_min_height=286,
        stats_card_max_height=334,
        metric_min_height=54,
        metric_preferred_height=58,
        metric_max_height=60,
    ),
    (CollectLayoutMode.LARGE, CollectHeightMode.STANDARD): CollectGeometrySpec(
        mode=CollectHeightMode.STANDARD,
        page_top_margin=14,
        page_bottom_margin=14,
        page_gap=12,
        setup_card_height=268,
        stats_card_min_height=280,
        stats_card_max_height=326,
        metric_min_height=52,
        metric_preferred_height=56,
        metric_max_height=58,
    ),
    (CollectLayoutMode.LARGE, CollectHeightMode.SHORT): CollectGeometrySpec(
        mode=CollectHeightMode.SHORT,
        page_top_margin=12,
        page_bottom_margin=12,
        page_gap=10,
        setup_card_height=258,
        stats_card_min_height=274,
        stats_card_max_height=314,
        metric_min_height=50,
        metric_preferred_height=54,
        metric_max_height=56,
    ),
    (CollectLayoutMode.MEDIUM, CollectHeightMode.TALL): CollectGeometrySpec(
        mode=CollectHeightMode.TALL,
        page_top_margin=18,
        page_bottom_margin=16,
        page_gap=14,
        setup_card_height=306,
        stats_card_min_height=474,
        stats_card_max_height=530,
        metric_min_height=50,
        metric_preferred_height=54,
        metric_max_height=58,
    ),
    (CollectLayoutMode.MEDIUM, CollectHeightMode.STANDARD): CollectGeometrySpec(
        mode=CollectHeightMode.STANDARD,
        page_top_margin=14,
        page_bottom_margin=14,
        page_gap=12,
        setup_card_height=296,
        stats_card_min_height=460,
        stats_card_max_height=514,
        metric_min_height=48,
        metric_preferred_height=52,
        metric_max_height=56,
    ),
    (CollectLayoutMode.MEDIUM, CollectHeightMode.SHORT): CollectGeometrySpec(
        mode=CollectHeightMode.SHORT,
        page_top_margin=12,
        page_bottom_margin=12,
        page_gap=10,
        setup_card_height=282,
        stats_card_min_height=442,
        stats_card_max_height=494,
        metric_min_height=46,
        metric_preferred_height=50,
        metric_max_height=54,
    ),
    (CollectLayoutMode.COMPACT, CollectHeightMode.TALL): CollectGeometrySpec(
        mode=CollectHeightMode.TALL,
        page_top_margin=14,
        page_bottom_margin=14,
        page_gap=12,
        setup_card_height=278,
        stats_card_min_height=454,
        stats_card_max_height=506,
        metric_min_height=48,
        metric_preferred_height=52,
        metric_max_height=56,
    ),
    (CollectLayoutMode.COMPACT, CollectHeightMode.STANDARD): CollectGeometrySpec(
        mode=CollectHeightMode.STANDARD,
        page_top_margin=12,
        page_bottom_margin=12,
        page_gap=10,
        setup_card_height=266,
        stats_card_min_height=440,
        stats_card_max_height=492,
        metric_min_height=46,
        metric_preferred_height=50,
        metric_max_height=54,
    ),
    (CollectLayoutMode.COMPACT, CollectHeightMode.SHORT): CollectGeometrySpec(
        mode=CollectHeightMode.SHORT,
        page_top_margin=10,
        page_bottom_margin=10,
        page_gap=10,
        setup_card_height=254,
        stats_card_min_height=424,
        stats_card_max_height=474,
        metric_min_height=44,
        metric_preferred_height=48,
        metric_max_height=52,
    ),
}


def collect_layout_mode(
    content_width: int,
    *,
    current_mode: CollectLayoutMode | None = None,
) -> CollectLayoutMode:
    """Return a stable viewport mode with sidebar-width hysteresis."""

    width = max(0, content_width)
    large_entry = LARGE_CONTENT_BREAKPOINT
    medium_entry = MEDIUM_CONTENT_BREAKPOINT

    if current_mode is CollectLayoutMode.MEDIUM:
        large_entry += (
            _LAYOUT_SPECS[CollectLayoutMode.LARGE].sidebar_width
            - _LAYOUT_SPECS[CollectLayoutMode.MEDIUM].sidebar_width
        )
    elif current_mode is CollectLayoutMode.COMPACT:
        medium_entry += (
            _LAYOUT_SPECS[CollectLayoutMode.MEDIUM].sidebar_width
            - _LAYOUT_SPECS[CollectLayoutMode.COMPACT].sidebar_width
        )
        large_entry += (
            _LAYOUT_SPECS[CollectLayoutMode.LARGE].sidebar_width
            - _LAYOUT_SPECS[CollectLayoutMode.COMPACT].sidebar_width
        )

    if width >= large_entry:
        return CollectLayoutMode.LARGE
    if width >= medium_entry:
        return CollectLayoutMode.MEDIUM
    return CollectLayoutMode.COMPACT


def collect_height_mode(viewport_height: int) -> CollectHeightMode:
    if viewport_height >= TALL_VIEWPORT_HEIGHT:
        return CollectHeightMode.TALL
    if viewport_height >= STANDARD_VIEWPORT_HEIGHT:
        return CollectHeightMode.STANDARD
    return CollectHeightMode.SHORT


def collect_layout_spec(
    content_width: int,
    *,
    current_mode: CollectLayoutMode | None = None,
) -> CollectLayoutSpec:
    return _LAYOUT_SPECS[
        collect_layout_mode(
            content_width,
            current_mode=current_mode,
        )
    ]


def collect_geometry_spec(
    layout_spec: CollectLayoutSpec,
    viewport_height: int,
) -> CollectGeometrySpec:
    height_mode = collect_height_mode(max(0, viewport_height))
    return _GEOMETRY_SPECS[(layout_spec.mode, height_mode)]


def collect_content_min_height(
    layout_spec: CollectLayoutSpec,
    geometry_spec: CollectGeometrySpec,
) -> int:
    """Return the natural Collect-page height before vertical scrolling."""

    return (
        geometry_spec.page_top_margin
        + geometry_spec.page_bottom_margin
        + INLINE_PAGE_HEADER_HEIGHT
        + geometry_spec.setup_card_height
        + geometry_spec.stats_card_min_height
        + layout_spec.primary_action_height
        + (geometry_spec.page_gap * COLLECT_PAGE_WIDGET_GAPS)
    )


def bounded_page_width(available_width: int, *, max_width: int) -> int:
    """Return a non-negative logical page width bounded by product usefulness.

    The helper deliberately does not select a layout from a physical display
    resolution. Callers pass the actual logical content viewport width.
    """

    if max_width <= 0:
        raise ValueError("max_width must be greater than 0")

    return min(max(0, available_width), max_width)


def centered_page_width_spec(
    available_width: int,
    *,
    max_width: int,
) -> PageWidthSpec:
    """Return centered insets for one bounded logical page surface.

    The viewport remains the source of truth for responsive mode selection.
    This helper only distributes width that is no longer useful to the page.
    """

    width = max(0, available_width)
    useful_width = bounded_page_width(width, max_width=max_width)
    spare_width = width - useful_width
    left_inset = spare_width // 2
    right_inset = spare_width - left_inset

    return PageWidthSpec(
        available_width=width,
        useful_width=useful_width,
        left_inset=left_inset,
        right_inset=right_inset,
    )


def collect_page_width_spec(content_width: int) -> PageWidthSpec:
    """Return Collect's centered useful-width distribution."""

    return centered_page_width_spec(
        content_width,
        max_width=LARGE_USEFUL_PAGE_MAX_WIDTH,
    )


def collect_useful_page_width(content_width: int) -> int:
    """Bound Collect to the approved large-layout useful width."""

    return collect_page_width_spec(content_width).useful_width
