from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


LARGE_CONTENT_BREAKPOINT = 1120
MEDIUM_CONTENT_BREAKPOINT = 820
MINIMUM_SUPPORTED_WINDOW_WIDTH = 920
MINIMUM_SUPPORTED_WINDOW_HEIGHT = 620

# Full HD @100% is the reference workbench composition:
# 1920 logical window width - 228 logical sidebar width = 1692.
#
# Wider logical viewports are allowed to use 75% of the width gained beyond
# that reference instead of being frozen at 1692 forever. This keeps the
# workbench visually consistent across common 1080p/QHD/4K + Windows scaling
# combinations while still reserving real outer breathing room on large
# displays. Qt already provides logical geometry after OS scaling; DPR is not
# applied to layout widths here.
WORKBENCH_REFERENCE_PAGE_WIDTH = 1692
WORKBENCH_WIDE_EXPANSION_NUMERATOR = 3
WORKBENCH_WIDE_EXPANSION_DENOMINATOR = 4
WORKBENCH_HARD_MAX_WIDTH = 3200

# About remains intentionally narrower because it is an information surface,
# not a dashboard/workbench; extra line length does not add utility there.
ABOUT_USEFUL_PAGE_MAX_WIDTH = 1320
SETTINGS_TWO_COLUMN_BREAKPOINT = LARGE_CONTENT_BREAKPOINT

INLINE_PAGE_HEADER_HEIGHT = 42
COLLECT_PAGE_WIDGET_GAPS = 3

TALL_VIEWPORT_HEIGHT = 800
STANDARD_VIEWPORT_HEIGHT = 700
DIALOG_WORK_AREA_MARGIN = 24


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


@dataclass(frozen=True, slots=True)
class PageSurfaceSpec:
    """Responsive geometry for a non-Collect page surface."""

    page_margin: int
    width: PageWidthSpec
    columns: int = 1


@dataclass(frozen=True, slots=True)
class DialogSizeSpec:
    """Work-area-aware logical size contract for a modal dialog."""

    work_area_width: int
    work_area_height: int
    usable_width: int
    usable_height: int
    minimum_width: int
    minimum_height: int
    width: int
    height: int


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


def progressive_page_width_spec(
    available_width: int,
    *,
    reference_width: int = WORKBENCH_REFERENCE_PAGE_WIDTH,
    hard_max_width: int = WORKBENCH_HARD_MAX_WIDTH,
    expansion_numerator: int = WORKBENCH_WIDE_EXPANSION_NUMERATOR,
    expansion_denominator: int = WORKBENCH_WIDE_EXPANSION_DENOMINATOR,
) -> PageWidthSpec:
    """Grow a centered workbench progressively beyond the Full HD reference.

    Up to the reference width, the page uses the complete logical viewport.
    Above it, only a controlled share of additional width becomes useful page
    width; the remainder becomes symmetric outer breathing room. The hard cap
    protects extreme/ultrawide viewports without introducing resolution- or
    DPR-specific layout branches.
    """

    if reference_width <= 0:
        raise ValueError("reference_width must be greater than 0")
    if hard_max_width < reference_width:
        raise ValueError("hard_max_width must be at least reference_width")
    if expansion_denominator <= 0:
        raise ValueError("expansion_denominator must be greater than 0")
    if not 0 <= expansion_numerator <= expansion_denominator:
        raise ValueError(
            "expansion_numerator must be between 0 and expansion_denominator"
        )

    width = max(0, available_width)

    if width <= reference_width:
        useful_width = width
    else:
        extra_width = width - reference_width
        useful_extra = (
            extra_width * expansion_numerator
        ) // expansion_denominator
        useful_width = min(
            width,
            hard_max_width,
            reference_width + useful_extra,
        )

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
    """Return Collect's progressive Full-HD-referenced workbench width."""

    return progressive_page_width_spec(content_width)


def collect_useful_page_width(content_width: int) -> int:
    """Return Collect's progressive useful logical workbench width."""

    return collect_page_width_spec(content_width).useful_width

def dialog_size_spec(
    work_area_width: int,
    work_area_height: int,
    *,
    preferred_width: int,
    preferred_height: int,
    minimum_width: int,
    minimum_height: int,
    edge_margin: int = DIALOG_WORK_AREA_MARGIN,
) -> DialogSizeSpec:
    """Clamp one dialog to the current logical screen work area.

    ``availableGeometry()`` already excludes taskbars/docks. The additional
    edge margin keeps the modal visually detached from the work-area edge while
    preserving its preferred desktop size whenever enough room exists.
    """

    if preferred_width <= 0 or preferred_height <= 0:
        raise ValueError("preferred dialog size must be greater than 0")
    if minimum_width <= 0 or minimum_height <= 0:
        raise ValueError("minimum dialog size must be greater than 0")
    if edge_margin < 0:
        raise ValueError("edge_margin must not be negative")

    area_width = max(1, work_area_width)
    area_height = max(1, work_area_height)
    usable_width = max(1, area_width - (edge_margin * 2))
    usable_height = max(1, area_height - (edge_margin * 2))

    fitted_minimum_width = min(minimum_width, usable_width)
    fitted_minimum_height = min(minimum_height, usable_height)
    width = max(
        fitted_minimum_width,
        min(preferred_width, usable_width),
    )
    height = max(
        fitted_minimum_height,
        min(preferred_height, usable_height),
    )

    return DialogSizeSpec(
        work_area_width=area_width,
        work_area_height=area_height,
        usable_width=usable_width,
        usable_height=usable_height,
        minimum_width=fitted_minimum_width,
        minimum_height=fitted_minimum_height,
        width=width,
        height=height,
    )


def responsive_page_margin(content_width: int) -> int:
    """Return the shared horizontal page margin for a logical viewport."""

    width = max(0, content_width)
    if width >= LARGE_CONTENT_BREAKPOINT:
        return 28
    if width >= MEDIUM_CONTENT_BREAKPOINT:
        return 22
    return 16


def page_surface_spec(
    content_width: int,
    *,
    max_width: int,
    columns: int = 1,
) -> PageSurfaceSpec:
    if columns <= 0:
        raise ValueError("columns must be greater than 0")

    return PageSurfaceSpec(
        page_margin=responsive_page_margin(content_width),
        width=centered_page_width_spec(content_width, max_width=max_width),
        columns=columns,
    )


def workbench_page_surface_spec(
    content_width: int,
    *,
    columns: int = 1,
) -> PageSurfaceSpec:
    if columns <= 0:
        raise ValueError("columns must be greater than 0")

    return PageSurfaceSpec(
        page_margin=responsive_page_margin(content_width),
        width=progressive_page_width_spec(content_width),
        columns=columns,
    )


def settings_page_spec(content_width: int) -> PageSurfaceSpec:
    columns = 2 if max(0, content_width) >= SETTINGS_TWO_COLUMN_BREAKPOINT else 1
    return workbench_page_surface_spec(
        content_width,
        columns=columns,
    )


def history_page_spec(content_width: int) -> PageSurfaceSpec:
    return workbench_page_surface_spec(content_width)


def about_page_spec(
    content_width: int,
    *,
    interface_scale: float = 1.0,
) -> PageSurfaceSpec:
    """Return About geometry while respecting the explicit XCC UI scale.

    About intentionally keeps a narrower readability surface than the main
    workbench. Because that surface has its own logical max-width, it must also
    follow the user's explicit XCC scale override; otherwise the fixed 1320px
    cap visually cancels part of Interface scale on this page. Windows/Qt DPI
    is already represented by ``content_width`` and is not multiplied here.
    """

    if interface_scale <= 0:
        raise ValueError("interface_scale must be greater than 0")

    badge_columns = 4 if max(0, content_width) >= MEDIUM_CONTENT_BREAKPOINT else 2
    scaled_max_width = max(
        1,
        round(ABOUT_USEFUL_PAGE_MAX_WIDTH * interface_scale),
    )
    return page_surface_spec(
        content_width,
        max_width=scaled_max_width,
        columns=badge_columns,
    )
