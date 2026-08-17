from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("PySide6")

from PySide6.QtCore import QPoint, Qt
from PySide6.QtWidgets import QApplication

from xcc.gui import XccMainWindow
from xcc.ui_responsive import CollectLayoutMode


@pytest.fixture(scope="module")
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def _settle(qapp: QApplication, window: XccMainWindow) -> None:
    for _ in range(4):
        qapp.processEvents()
        window._apply_collect_layout(force=True)
        window._apply_responsive_pages(force=True)


def _grid_positions(layout, widgets) -> list[tuple[int, int]]:
    positions: list[tuple[int, int]] = []
    for widget in widgets:
        index = layout.indexOf(widget)
        assert index >= 0
        row, column, _row_span, _column_span = layout.getItemPosition(index)
        positions.append((row, column))
    return positions


def test_collect_resize_round_trip_preserves_state_widgets_and_actions(
    qapp: QApplication,
) -> None:
    window = XccMainWindow()
    window.resize(1688, 900)
    window.show()
    _settle(qapp, window)

    # Put Collect into a state that must survive every responsive rearrangement.
    window.mode_files.setChecked(True)
    window._refresh_source_controls()
    window.max_chars_input.setText("654321")
    window.source_input.setText("Responsive state sentinel")

    widget_ids = {
        "collect_button": id(window.collect_button),
        "source_box": id(window.source_box),
        "paste_paths": id(window.paste_paths_button),
        "select_source": id(window.select_source_button),
        "mode_buttons": tuple(id(button) for button in window.mode_buttons_list),
        "metric_groups": tuple(id(group) for group in window.metric_groups),
    }

    cases = (
        (
            (920, 620),
            CollectLayoutMode.COMPACT,
            [(0, 0), (0, 1), (1, 0), (1, 1)],
            True,
            Qt.ScrollBarPolicy.ScrollBarAsNeeded,
        ),
        (
            (1200, 760),
            CollectLayoutMode.MEDIUM,
            [(0, 0), (0, 1), (1, 0), (1, 1)],
            True,
            Qt.ScrollBarPolicy.ScrollBarAsNeeded,
        ),
        (
            (1688, 900),
            CollectLayoutMode.LARGE,
            [(0, 0), (0, 2), (0, 4), (0, 6)],
            False,
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff,
        ),
        # Round-trip back through the narrow composition catches accidental
        # widget recreation, duplicate controls, and state loss.
        (
            (920, 620),
            CollectLayoutMode.COMPACT,
            [(0, 0), (0, 1), (1, 0), (1, 1)],
            True,
            Qt.ScrollBarPolicy.ScrollBarAsNeeded,
        ),
    )

    for (
        (width, height),
        expected_mode,
        expected_metric_positions,
        source_actions_below,
        expected_vertical_policy,
    ) in cases:
        window.resize(width, height)
        _settle(qapp, window)

        assert window.pages.currentWidget() is window.collect_page
        assert window._collect_layout_mode is expected_mode
        assert window._collect_layout_spec is not None
        assert (
            window._collect_layout_spec.source_actions_below
            is source_actions_below
        )

        assert id(window.collect_button) == widget_ids["collect_button"]
        assert id(window.source_box) == widget_ids["source_box"]
        assert id(window.paste_paths_button) == widget_ids["paste_paths"]
        assert id(window.select_source_button) == widget_ids["select_source"]
        assert (
            tuple(id(button) for button in window.mode_buttons_list)
            == widget_ids["mode_buttons"]
        )
        assert (
            tuple(id(group) for group in window.metric_groups)
            == widget_ids["metric_groups"]
        )

        assert window.mode_files.isChecked()
        assert window.max_chars_input.text() == "654321"
        assert window.source_input.text() == "Responsive state sentinel"

        assert window.collect_button.isVisible()
        assert window.collect_button.isEnabled()
        assert window.paste_paths_button.isVisible()
        assert window.select_source_button.isVisible()
        assert (
            window.collect_page_scroll.horizontalScrollBarPolicy()
            == Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        assert (
            window.collect_page_scroll.verticalScrollBarPolicy()
            == expected_vertical_policy
        )

        metric_positions = _grid_positions(
            window.metrics_layout,
            window.metric_groups,
        )
        assert metric_positions == expected_metric_positions

        source_y = window.source_box.geometry().y()
        paste_y = window.paste_paths_button.geometry().y()
        select_y = window.select_source_button.geometry().y()
        if source_actions_below:
            assert paste_y > source_y
            assert select_y > source_y
        else:
            assert paste_y == source_y
            assert select_y == source_y

        button_bottom = window.collect_button.mapTo(
            window.collect_page_viewport,
            QPoint(0, window.collect_button.height()),
        ).y()
        if expected_vertical_policy == Qt.ScrollBarPolicy.ScrollBarAlwaysOff:
            assert button_bottom <= window.collect_page_viewport.height()

    window._is_quitting = True
    window.close()


def test_all_normal_main_surfaces_forbid_horizontal_page_scrolling(
    qapp: QApplication,
) -> None:
    window = XccMainWindow()
    window.resize(920, 620)
    window.show()
    _settle(qapp, window)

    assert (
        window.collect_page_scroll.horizontalScrollBarPolicy()
        == Qt.ScrollBarPolicy.ScrollBarAlwaysOff
    )
    assert (
        window.settings_page_scroll.horizontalScrollBarPolicy()
        == Qt.ScrollBarPolicy.ScrollBarAlwaysOff
    )
    assert (
        window.about_page_scroll.horizontalScrollBarPolicy()
        == Qt.ScrollBarPolicy.ScrollBarAlwaysOff
    )
    assert (
        window.history_scroll_area.horizontalScrollBarPolicy()
        == Qt.ScrollBarPolicy.ScrollBarAlwaysOff
    )

    window._is_quitting = True
    window.close()
