from __future__ import annotations

import sys
from datetime import datetime
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QApplication,
    QButtonGroup,
    QCheckBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QSizePolicy,
    QSpacerItem,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
    QGridLayout,
    QScrollArea,
)
from PySide6.QtGui import QIntValidator
from . import __version__
from .config import DEFAULT_HOTKEY, MAX_OUTPUT_CHARS
from pathlib import Path
from .clipboard import copy_to_clipboard
from .collector import collect_files
from .formatter import format_collection
from .git_utils import get_changed_files, get_git_diff, is_git_repository
from .scanner import scan_project_files

class XccMainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("XCC Context Collector")
        self.setMinimumSize(920, 620)

        self.selected_paths: list[Path] = []
        self.project_root: Path | None = None
        self.history_entries: list[dict[str, object]] = []

        self._setup_ui()
        self._apply_theme()

    def _setup_ui(self) -> None:
        root = QWidget()
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        root_layout.addWidget(self._build_header())

        body = QWidget()
        body_layout = QHBoxLayout(body)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)

        self.nav = self._build_nav()
        self.pages = QStackedWidget()

        self.collect_page = self._build_collect_page()
        self.history_page = self._build_history_page()
        self.settings_page = self._build_settings_page()
        self.about_page = self._build_about_page()

        self.pages.addWidget(self.collect_page)
        self.pages.addWidget(self.history_page)
        self.pages.addWidget(self.settings_page)
        self.pages.addWidget(self.about_page)

        body_layout.addWidget(self.nav)
        body_layout.addWidget(self.pages, 1)

        root_layout.addWidget(body, 1)

        self.status_label = QLabel("Ready")
        self.status_label.setObjectName("StatusBar")
        self.status_label.setFixedHeight(38)
        root_layout.addWidget(self.status_label)

        self.setCentralWidget(root)

        self.nav.currentRowChanged.connect(self._change_page)
        self.nav.setCurrentRow(0)

        self.select_source_button.clicked.connect(self._select_source)
        self.mode_group.buttonClicked.connect(self._clear_source)
        self.collect_button.clicked.connect(self._collect_and_copy)

    def _build_history_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(18)

        layout.addWidget(self._section_title("History"))

        history_card = self._card()
        history_card.setMinimumHeight(260)

        history_layout = self._card_layout(history_card)
        history_layout.addWidget(self._card_title("Runtime History"))

        self.history_scroll_area = QScrollArea()
        self.history_scroll_area.setObjectName("HistoryScrollArea")
        self.history_scroll_area.setWidgetResizable(True)
        self.history_scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.history_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.history_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        self.history_list_container = QWidget()
        self.history_list_container.setObjectName("TransparentWidget")

        self.history_list_layout = QVBoxLayout(self.history_list_container)
        self.history_list_layout.setContentsMargins(0, 0, 0, 0)
        self.history_list_layout.setSpacing(12)

        self.history_empty_label = QLabel(
            "No runs yet.\nCollect context to see runtime history here."
        )
        self.history_empty_label.setObjectName("HistoryEmpty")
        self.history_empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.history_empty_label.setMinimumHeight(140)

        self.history_list_layout.addWidget(self.history_empty_label)
        self.history_list_layout.addStretch(1)

        self.history_scroll_area.setWidget(self.history_list_container)

        history_layout.addWidget(self.history_scroll_area, 1)

        layout.addWidget(history_card, 1)
        layout.addStretch(0)

        return page

    def _build_header(self) -> QWidget:
        header = QFrame()
        header.setObjectName("Header")
        header.setFixedHeight(56)

        layout = QHBoxLayout(header)
        layout.setContentsMargins(18, 0, 18, 0)
        layout.setSpacing(12)

        title = QLabel("XCC Context Collector — AI-ready project context collector")
        title.setObjectName("HeaderTitle")

        self.header_status = QLabel("Ready")
        self.header_status.setObjectName("StatusCapsule")
        self.header_status.setFixedHeight(34)

        hotkey = QLabel(f"Hotkey: {DEFAULT_HOTKEY}")
        hotkey.setObjectName("HotkeyCapsule")
        hotkey.setFixedHeight(34)

        layout.addWidget(title, 1)
        layout.addWidget(self.header_status)
        layout.addWidget(hotkey)

        return header

    def _build_nav(self) -> QListWidget:
        nav = QListWidget()
        nav.setObjectName("Sidebar")
        nav.setFixedWidth(190)
        nav.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        for title in ["Collect", "History", "Settings", "About"]:
            item = QListWidgetItem(title)
            item.setSizeHint(item.sizeHint())
            nav.addItem(item)

        return nav

    def _build_collect_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(18)

        layout.addWidget(self._section_title("Collect Context"))

        setup_card = self._card()
        setup_card.setMinimumHeight(230)

        setup_layout = self._card_layout(setup_card)
        setup_layout.addWidget(self._card_title("Setup"))

        setup_grid = QGridLayout()
        setup_grid.setContentsMargins(0, 6, 0, 0)
        setup_grid.setHorizontalSpacing(14)
        setup_grid.setVerticalSpacing(14)

        mode_label = QLabel("Mode")
        mode_label.setObjectName("FieldLabel")
        mode_label.setFixedWidth(90)

        self.mode_group = QButtonGroup(self)
        self.mode_files = QRadioButton("Selected Files")
        self.mode_folder = QRadioButton("Full Folder")
        self.mode_git = QRadioButton("Git Changed Files")

        self.mode_folder.setChecked(True)

        mode_buttons = QWidget()
        mode_buttons.setObjectName("TransparentWidget")
        mode_buttons_layout = QHBoxLayout(mode_buttons)
        mode_buttons_layout.setContentsMargins(0, 0, 0, 0)
        mode_buttons_layout.setSpacing(22)

        for index, button in enumerate([self.mode_files, self.mode_folder, self.mode_git]):
            self.mode_group.addButton(button, index)
            mode_buttons_layout.addWidget(button)

        mode_buttons_layout.addStretch(1)

        source_label = QLabel("Source")
        source_label.setObjectName("FieldLabel")
        source_label.setFixedWidth(90)

        self.source_input = QLineEdit()
        self.source_input.setPlaceholderText("No source selected")
        self.source_input.setReadOnly(True)
        self.source_input.setFixedHeight(40)

        self.select_source_button = QPushButton("Select Source")
        self.select_source_button.setMinimumWidth(160)
        self.select_source_button.setFixedHeight(40)

        options_label = QLabel("Options")
        options_label.setObjectName("FieldLabel")
        options_label.setFixedWidth(90)

        self.compact_checkbox = QCheckBox("Compact mode")
        self.compact_checkbox.setChecked(True)
        self.compact_checkbox.setFixedHeight(40)

        max_chars_label = QLabel("Max chars")
        max_chars_label.setObjectName("FieldLabelSmall")
        max_chars_label.setFixedHeight(40)

        self.max_chars_input = QLineEdit(str(MAX_OUTPUT_CHARS))
        self.max_chars_input.setValidator(QIntValidator(1, 10_000_000, self))
        self.max_chars_input.setMaximumWidth(160)
        self.max_chars_input.setFixedHeight(40)

        setup_grid.addWidget(mode_label, 0, 0)
        setup_grid.addWidget(mode_buttons, 0, 1, 1, 2)

        setup_grid.addWidget(source_label, 1, 0)
        setup_grid.addWidget(self.source_input, 1, 1)
        setup_grid.addWidget(self.select_source_button, 1, 2)

        setup_grid.addWidget(options_label, 2, 0)

        options_box = QWidget()
        options_box.setObjectName("TransparentWidget")
        options_box_layout = QHBoxLayout(options_box)
        options_box_layout.setContentsMargins(0, 0, 0, 0)
        options_box_layout.setSpacing(16)

        options_box_layout.addWidget(self.compact_checkbox)
        options_box_layout.addSpacing(24)
        options_box_layout.addWidget(max_chars_label)
        options_box_layout.addWidget(self.max_chars_input)
        options_box_layout.addStretch(1)

        setup_grid.addWidget(options_box, 2, 1, 1, 2)

        setup_grid.setColumnStretch(0, 0)
        setup_grid.setColumnStretch(1, 1)
        setup_grid.setColumnStretch(2, 0)

        setup_layout.addLayout(setup_grid)

        layout.addWidget(setup_card)

        stats_card = self._card()
        stats_card.setMinimumHeight(210)

        stats_layout = self._card_layout(stats_card)

        stats_layout.addWidget(self._card_title("Last Run"))

        self.files_metric = self._metric_capsule("Files", "-")
        self.lines_metric = self._metric_capsule("Lines", "-")
        self.source_chars_metric = self._metric_capsule("Source Chars", "-")

        self.output_chars_metric = self._metric_capsule("Output Chars", "-")
        self.tokens_metric = self._metric_capsule("Output Tokens", "-")

        self.truncated_metric = self._metric_capsule("Truncated", "-")
        self.errors_metric = self._metric_capsule("Errors", "-")

        columns_row = QHBoxLayout()
        columns_row.setSpacing(20)
        columns_row.setContentsMargins(0, 0, 0, 0)

        volume_column = QVBoxLayout()
        volume_column.setContentsMargins(0, 0, 0, 0)
        volume_column.setSpacing(8)
        volume_title = QLabel("Volume")
        volume_title.setObjectName("MetricGroupTitle")
        volume_column.addWidget(volume_title)
        volume_column.addWidget(self.files_metric)
        volume_column.addWidget(self.lines_metric)
        volume_column.addWidget(self.source_chars_metric)

        output_column = QVBoxLayout()
        output_column.setContentsMargins(0, 0, 0, 0)
        output_column.setSpacing(8)
        output_title = QLabel("Output")
        output_title.setObjectName("MetricGroupTitle")
        output_column.addWidget(output_title)
        output_column.addWidget(self.output_chars_metric)
        output_column.addWidget(self.tokens_metric)
        output_column.addStretch(1)

        health_column = QVBoxLayout()
        health_column.setContentsMargins(0, 0, 0, 0)
        health_column.setSpacing(8)
        health_title = QLabel("Health")
        health_title.setObjectName("MetricGroupTitle")
        health_column.addWidget(health_title)
        health_column.addWidget(self.truncated_metric)
        health_column.addWidget(self.errors_metric)
        health_column.addStretch(1)

        columns_row.addLayout(volume_column, 1)
        columns_row.addLayout(output_column, 1)
        columns_row.addLayout(health_column, 1)

        stats_layout.addLayout(columns_row)

        layout.addWidget(stats_card)

        layout.addStretch(1)

        self.collect_button = QPushButton("Collect && Copy")
        self.collect_button.setObjectName("PrimaryButton")
        self.collect_button.setFixedHeight(52)

        layout.addWidget(self.collect_button)

        return page

    def _current_mode(self) -> str:
        checked_id = self.mode_group.checkedId()

        if checked_id == 0:
            return "files"

        if checked_id == 1:
            return "folder"

        return "git"

    def _change_page(self, index: int) -> None:
        if index == 2:
            self._refresh_settings_page()

        self.pages.setCurrentIndex(index)

    def _current_mode_name(self) -> str:
        mode = self._current_mode()

        return {
            "files": "Selected Files",
            "folder": "Full Folder",
            "git": "Git Changed Files",
        }.get(mode, "Unknown")

    def _settings_row(self, label: str, value: str) -> QFrame:
        row = QFrame()
        row.setObjectName("SettingsRow")
        row.setFixedHeight(44)
        row.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        layout = QHBoxLayout(row)
        layout.setContentsMargins(14, 0, 14, 0)
        layout.setSpacing(12)

        label_widget = QLabel(label)
        label_widget.setObjectName("SettingsLabel")

        value_widget = QLabel(value)
        value_widget.setObjectName("SettingsValue")
        value_widget.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        row.value_label = value_widget

        layout.addWidget(label_widget, 1)
        layout.addWidget(value_widget, 1)

        return row

    def _settings_note(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setObjectName("SettingsNote")
        label.setWordWrap(True)
        return label

    def _refresh_settings_page(self) -> None:
        if hasattr(self, "settings_current_mode"):
            self.settings_current_mode.value_label.setText(self._current_mode_name())

        if hasattr(self, "settings_compact_mode"):
            self.settings_compact_mode.value_label.setText(
                "Enabled" if self.compact_checkbox.isChecked() else "Disabled"
            )

        if hasattr(self, "settings_current_max_chars"):
            self.settings_current_max_chars.value_label.setText(
                self.max_chars_input.text().strip() or "Not set"
            )

    def _select_source(self) -> None:
        mode = self._current_mode()

        self.selected_paths = []
        self.project_root = None

        if mode == "files":
            selected, _ = QFileDialog.getOpenFileNames(
                self,
                "Select context files",
                "",
                "Context files (*.py *.pyw *.md *.txt *.json *.yaml *.yml *.toml *.ini *.cfg);;All files (*.*)",
            )

            if not selected:
                self._set_status("Source selection cancelled.")
                return

            self.selected_paths = [Path(path) for path in selected]
            self.source_input.setText(f"{len(self.selected_paths)} files selected")
            self._set_status(f"Selected {len(self.selected_paths)} files.")
            return

        selected_folder = QFileDialog.getExistingDirectory(
            self,
            "Select project folder",
            "",
        )

        if not selected_folder:
            self._set_status("Source selection cancelled.")
            return

        folder = Path(selected_folder)

        if mode == "git" and not is_git_repository(folder):
            self._set_status("Selected folder is not a Git repository.")
            QMessageBox.warning(
                self,
                "XCC",
                "Selected folder is not a Git repository.",
            )
            return

        self.project_root = folder
        self.source_input.setText(str(folder))

        if mode == "git":
            self._set_status("Git repository selected.")
        else:
            self._set_status("Project folder selected.")

    def _collect_and_copy(self) -> None:
        try:
            max_output_chars = self._read_max_output_chars()
            mode = self._current_mode()
            selected_paths, project_root = self._resolve_selected_paths(mode)

            if not selected_paths:
                self._set_status("No files selected or found.")
                QMessageBox.warning(self, "XCC", "No files selected or found.")
                return

            files, errors = collect_files(selected_paths)

            mode_name = {
                "files": "Selected Files",
                "folder": "Full Folder",
                "git": "Git Changed Files",
            }.get(mode, "Unknown")

            git_diff = None
            if mode == "git" and project_root is not None:
                git_diff = get_git_diff(project_root)

            result = format_collection(
                files,
                errors,
                project_root=project_root,
                compact=self.compact_checkbox.isChecked(),
                mode_name=mode_name,
                max_output_chars=max_output_chars,
                git_diff=git_diff,
            )

            if not result.text.strip():
                self._set_status("Nothing to copy.")
                QMessageBox.warning(self, "XCC", "Nothing to copy.")
                return

            copy_to_clipboard(result.text)

            output_chars = len(result.text)
            output_tokens = output_chars // 4

            self._update_metrics(
                files=result.stats.files,
                lines=result.stats.lines,
                source_chars=result.stats.chars,
                output_chars=output_chars,
                output_tokens=output_tokens,
                truncated=result.was_truncated,
                errors=len(result.errors),
            )
            self._add_history_entry(
                mode_name=mode_name,
                source=self._current_source_label(mode, project_root),
                files=result.stats.files,
                lines=result.stats.lines,
                source_chars=result.stats.chars,
                output_chars=output_chars,
                output_tokens=output_tokens,
                truncated=result.was_truncated,
                errors=len(result.errors),
            )

            self._show_success_feedback()

        except Exception as exc:
            self._set_status("Error.")
            QMessageBox.critical(self, "XCC", str(exc))

    def _read_max_output_chars(self) -> int:
        raw_value = self.max_chars_input.text().strip()

        if not raw_value:
            raise ValueError("Max output chars is required.")

        value = int(raw_value)

        if value <= 0:
            raise ValueError("Max output chars must be greater than 0.")

        return value

    def _resolve_selected_paths(self, mode: str) -> tuple[list[Path], Path | None]:
        if mode == "files":
            return self.selected_paths, None

        if self.project_root is None:
            raise ValueError("Select a source folder first.")

        if mode == "folder":
            return scan_project_files(self.project_root), self.project_root

        if not is_git_repository(self.project_root):
            raise ValueError("Selected folder is not a Git repository.")

        return get_changed_files(self.project_root), self.project_root

    def _update_metrics(
        self,
        *,
        files: int,
        lines: int,
        source_chars: int,
        output_chars: int,
        output_tokens: int,
        truncated: bool,
        errors: int,
    ) -> None:
        self._set_metric_value(self.files_metric, str(files))
        self._set_metric_value(self.lines_metric, str(lines))
        self._set_metric_value(self.source_chars_metric, str(source_chars))
        self._set_metric_value(self.output_chars_metric, str(output_chars))
        self._set_metric_value(self.tokens_metric, str(output_tokens))
        self._set_metric_value(self.truncated_metric, "Yes" if truncated else "No")
        self._set_metric_value(self.errors_metric, str(errors))

    def _set_metric_value(self, metric: QFrame, value: str) -> None:
        metric.value_label.setText(value)

    def _clear_source(self) -> None:
        self.selected_paths = []
        self.project_root = None
        self.source_input.clear()
        self.source_input.setPlaceholderText("No source selected")
        self._set_status("Source cleared.")

    def _set_status(self, message: str) -> None:
        self.status_label.setText(message)
        self.header_status.setText(message if len(message) <= 18 else "Ready")

    def _show_success_feedback(self) -> None:
        self._set_status("Copied to clipboard.")
        self.header_status.setText("Copied")
        self.collect_button.setText("Copied!")

        QTimer.singleShot(1500, self._reset_success_feedback)

    def _reset_success_feedback(self) -> None:
        self.header_status.setText("Ready")
        self.collect_button.setText("Collect && Copy")

    def _build_settings_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(18)

        layout.addWidget(self._section_title("Settings"))

        defaults_card = self._card()
        defaults_layout = self._card_layout(defaults_card)
        defaults_layout.addWidget(self._card_title("Runtime Defaults"))

        defaults_layout.addWidget(
            self._settings_row("Default hotkey", DEFAULT_HOTKEY)
        )
        defaults_layout.addWidget(
            self._settings_row("Default max output chars", str(MAX_OUTPUT_CHARS))
        )
        defaults_layout.addWidget(
            self._settings_row("App version", __version__)
        )

        session_card = self._card()
        session_layout = self._card_layout(session_card)
        session_layout.addWidget(self._card_title("Current Session"))

        self.settings_current_mode = self._settings_row(
            "Current mode",
            self._current_mode_name(),
        )
        self.settings_compact_mode = self._settings_row(
            "Compact mode",
            "Enabled" if self.compact_checkbox.isChecked() else "Disabled",
        )
        self.settings_current_max_chars = self._settings_row(
            "Current max chars",
            self.max_chars_input.text().strip() or "Not set",
        )

        session_layout.addWidget(self.settings_current_mode)
        session_layout.addWidget(self.settings_compact_mode)
        session_layout.addWidget(self.settings_current_max_chars)

        persistence_card = self._card()
        persistence_layout = self._card_layout(persistence_card)
        persistence_layout.addWidget(self._card_title("Persistence"))

        persistence_layout.addWidget(
            self._settings_row("Settings persistence", "Planned in v0.6")
        )
        persistence_layout.addWidget(
            self._settings_note(
                "This page reflects the current runtime session only. "
                "Saving defaults to config.json will be implemented in v0.6."
            )
        )

        layout.addWidget(defaults_card)
        layout.addWidget(session_card)
        layout.addWidget(persistence_card)
        layout.addStretch(1)

        return page
    
    def _current_source_label(self, mode: str, project_root: Path | None) -> str:
        if mode == "files":
            count = len(self.selected_paths)
            return f"{count} selected file{'s' if count != 1 else ''}"

        if project_root is not None:
            return str(project_root)

        return "Unknown source"
    
    def _build_about_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(18)

        layout.addWidget(self._section_title("About"))

        card = self._card()
        card_layout = QVBoxLayout(card)

        card_layout.addWidget(QLabel("XCC Context Collector"))
        card_layout.addWidget(QLabel(f"Version: {__version__}"))
        card_layout.addWidget(QLabel("Purpose: collect AI-ready project context and copy it to clipboard."))

        layout.addWidget(card)
        layout.addStretch(1)

        return page

    def _build_placeholder_page(self, title: str, text: str) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(18)

        layout.addWidget(self._section_title(title))

        card = self._card()
        card_layout = QVBoxLayout(card)
        card_layout.addWidget(QLabel(text))

        layout.addWidget(card)
        layout.addStretch(1)

        return page

    def _section_title(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setObjectName("SectionTitle")
        return label

    def _card_title(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setObjectName("CardTitle")
        label.setFixedHeight(18)
        label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        return label

    def _card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("Card")
        return card
    
    def _card_layout(self, card: QFrame) -> QVBoxLayout:
        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 18, 24, 18)
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        return layout
    
    def _add_history_entry(
        self,
        *,
        mode_name: str,
        source: str,
        files: int,
        lines: int,
        source_chars: int,
        output_chars: int,
        output_tokens: int,
        truncated: bool,
        errors: int,
    ) -> None:
        entry = {
            "time": datetime.now().strftime("%H:%M:%S"),
            "mode_name": mode_name,
            "source": source,
            "files": files,
            "lines": lines,
            "source_chars": source_chars,
            "output_chars": output_chars,
            "output_tokens": output_tokens,
            "truncated": truncated,
            "errors": errors,
        }

        self.history_entries.insert(0, entry)
        self._render_history_entries()
        
    def _render_history_entries(self) -> None:
        while self.history_list_layout.count():
            item = self.history_list_layout.takeAt(0)
            widget = item.widget()

            if widget is not None:
                widget.deleteLater()

        if not self.history_entries:
            self.history_list_layout.addWidget(self.history_empty_label)
            self.history_list_layout.addStretch(1)
            return

        for entry in self.history_entries[:20]:
            self.history_list_layout.addWidget(self._history_entry_widget(entry))

        self.history_list_layout.addStretch(1)

    def _history_entry_widget(self, entry: dict[str, object]) -> QWidget:
        row = QFrame()
        row.setObjectName("HistoryEntry")
        row.setFixedHeight(96)
        row.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        layout = QVBoxLayout(row)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(7)

        top_row = QHBoxLayout()
        top_row.setContentsMargins(0, 0, 0, 0)
        top_row.setSpacing(8)

        time_label = QLabel(str(entry["time"]))
        time_label.setObjectName("HistoryTime")

        mode_label = QLabel(str(entry["mode_name"]))
        mode_label.setObjectName("HistoryModeCapsule")
        mode_label.setFixedHeight(26)

        top_row.addWidget(time_label)
        top_row.addStretch(1)
        top_row.addWidget(mode_label)

        source_label = QLabel(str(entry["source"]))
        source_label.setObjectName("HistorySource")
        source_label.setWordWrap(False)

        stats_label = QLabel(
            f"Files {entry['files']} · "
            f"Lines {entry['lines']} · "
            f"Source {entry['source_chars']} chars · "
            f"Output {entry['output_chars']} chars"
        )
        stats_label.setObjectName("HistoryStats")

        health_label = QLabel(
            f"Tokens {entry['output_tokens']} · "
            f"Truncated {'Yes' if entry['truncated'] else 'No'} · "
            f"Errors {entry['errors']}"
        )
        health_label.setObjectName("HistoryHealth")

        layout.addLayout(top_row)
        layout.addWidget(source_label)
        layout.addWidget(stats_label)
        layout.addWidget(health_label)

        return row

    def _metric_capsule(self, label: str, value: str) -> QFrame:
        capsule = QFrame()
        capsule.setObjectName("MetricCapsule")
        capsule.setMinimumWidth(0)
        capsule.setFixedHeight(52)

        layout = QVBoxLayout(capsule)
        layout.setContentsMargins(14, 6, 14, 6)
        layout.setSpacing(2)

        label_widget = QLabel(label)
        label_widget.setObjectName("MetricLabel")

        value_widget = QLabel(value)
        value_widget.setObjectName("MetricValue")

        capsule.value_label = value_widget

        layout.addWidget(label_widget)
        layout.addWidget(value_widget)

        return capsule
    
    def _apply_theme(self) -> None:
        self.setStyleSheet(
            """
            QMainWindow {
                background: #0F0F10;
            }

            QWidget {
                background: #0F0F10;
                color: #F2F2F2;
                font-family: Segoe UI;
                font-size: 13px;
            }

            #Header {
                background: #151515;
                border-bottom: 1px solid #2F2A1C;
            }

            #HeaderTitle {
                font-size: 15px;
                font-weight: 700;
                color: #F5C542;
                background: transparent;
            }

            #StatusCapsule,
            #HotkeyCapsule {
                background: #1A1A1A;
                border: 1px solid #6A5520;
                border-radius: 10px;
                padding: 4px 12px;
                color: #F2F2F2;
            }

            #HotkeyCapsule {
                color: #F5C542;
            }

            #Sidebar {
                background: #121212;
                border-right: 1px solid #2F2A1C;
                padding: 10px;
                outline: none;
            }

            #Sidebar::item {
                padding: 12px 14px;
                margin: 4px 0;
                border-radius: 10px;
                color: #C9C9C9;
                background: transparent;
            }

            #Sidebar::item:hover {
                background: #241F10;
                color: #F5C542;
            }

            #Sidebar::item:selected {
                background: #F5C542;
                color: #111111;
                font-weight: 700;
            }

            #Sidebar::item:selected:hover {
                background: #FFD95A;
                color: #111111;
            }

            #SectionTitle {
                font-size: 22px;
                font-weight: 700;
                color: #F2F2F2;
                background: transparent;
            }

            #Card {
                background: #161616;
                border: 1px solid #6A5520;
                border-radius: 14px;
            }

            #CardTitle {
                color: #F5C542;
                font-size: 13px;
                font-weight: 800;
                background: transparent;
                padding: 0px;
                margin: 0px;
            }
            #FieldLabel {
                color: #D6D6D6;
                font-weight: 700;
                background: transparent;
            }

            #FieldLabelSmall {
                color: #B8B8B8;
                background: transparent;
            }

            QLineEdit {
                background: #101010;
                border: 1px solid #6A5520;
                border-radius: 10px;
                padding: 8px 10px;
                color: #F2F2F2;
                selection-background-color: #F5C542;
                selection-color: #111111;
            }

            QLineEdit:hover {
                border: 1px solid #D2A92E;
            }

            QLineEdit:focus {
                border: 1px solid #F5C542;
            }

            QPushButton {
                background: #1A1A1A;
                border: 1px solid #6A5520;
                border-radius: 10px;
                padding: 9px 14px;
                color: #F2F2F2;
            }

            QPushButton:hover {
                background: #232323;
                border: 1px solid #F5C542;
                color: #F5C542;
            }

            QPushButton:pressed {
                background: #2A2412;
            }

            #PrimaryButton {
                background: #F5C542;
                color: #111111;
                font-size: 15px;
                font-weight: 800;
                border: 1px solid #F5C542;
                border-radius: 12px;
            }

            #PrimaryButton:hover {
                background: #FFD95A;
                border: 1px solid #FFD95A;
                color: #111111;
            }

            #PrimaryButton:pressed {
                background: #E0B83B;
                border: 1px solid #E0B83B;
            }

            QRadioButton,
            QCheckBox {
                spacing: 8px;
                padding: 2px 0;
                background: transparent;
            }

            QRadioButton:hover,
            QCheckBox:hover {
                color: #F5C542;
            }

            QRadioButton::indicator,
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                background: #101010;
                border: 1px solid #6A5520;
            }

            QRadioButton::indicator {
                border-radius: 8px;
            }

            QCheckBox::indicator {
                border-radius: 4px;
            }

            QRadioButton::indicator:hover,
            QCheckBox::indicator:hover {
                border: 1px solid #F5C542;
            }

            QRadioButton::indicator:checked,
            QCheckBox::indicator:checked {
                background: #F5C542;
                border: 1px solid #F5C542;
            }

            #MetricCapsule {
                background: #181818;
                border: 1px solid #5E4A1A;
                border-radius: 10px;
            }

            #MetricCapsule:hover {
                background: #1E1B12;
                border: 1px solid #F5C542;
            }

            #MetricLabel {
                color: #AFAFAF;
                font-size: 11px;
                background: transparent;
            }

            #MetricValue {
                color: #F5C542;
                font-size: 15px;
                font-weight: 800;
                background: transparent;
            }

            #StatusBar {
                background: #151515;
                border-top: 1px solid #2F2A1C;
                padding-left: 16px;
                color: #B8B8B8;
            }
            #MetricGroupTitle {
                color: #E0E0E0;
                font-size: 12px;
                font-weight: 700;
                background: transparent;
                margin-bottom: 2px;
            }
            #TransparentWidget {
                background: transparent;
            }
            #HistoryEntry {
                background: #181818;
                border: 1px solid #4F3F18;
                border-radius: 10px;
            }

            #HistoryEntry:hover {
                background: #1E1B12;
                border: 1px solid #F5C542;
            }

            #HistoryTime {
                color: #F5C542;
                font-size: 12px;
                font-weight: 800;
                background: transparent;
            }

            #HistoryModeCapsule {
                background: #101010;
                border: 1px solid #6A5520;
                border-radius: 8px;
                padding: 3px 10px;
                color: #F2F2F2;
                font-size: 11px;
                font-weight: 700;
            }

            #HistorySource {
                color: #D6D6D6;
                font-size: 12px;
                background: transparent;
            }

            #HistoryStats {
                color: #AFAFAF;
                font-size: 11px;
                background: transparent;
            }

            #HistoryHealth {
                color: #8F8F8F;
                font-size: 11px;
                background: transparent;
            }

            #HistoryEmpty {
                color: #8F8F8F;
                font-size: 13px;
                background: transparent;
            }
            #HistoryScrollArea {
                background: transparent;
                border: none;
            }

            #HistoryScrollArea QWidget {
                background: transparent;
            }

            QScrollBar:vertical {
                background: #101010;
                width: 10px;
                margin: 0px;
                border-radius: 5px;
            }

            QScrollBar::handle:vertical {
                background: #5E4A1A;
                min-height: 28px;
                border-radius: 5px;
            }

            QScrollBar::handle:vertical:hover {
                background: #F5C542;
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }

            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background: transparent;
            }
            #SettingsRow {
                background: #181818;
                border: 1px solid #4F3F18;
                border-radius: 10px;
            }

            #SettingsRow:hover {
                background: #1E1B12;
                border: 1px solid #F5C542;
            }

            #SettingsLabel {
                color: #B8B8B8;
                font-size: 12px;
                font-weight: 600;
                background: transparent;
            }

            #SettingsValue {
                color: #F5C542;
                font-size: 12px;
                font-weight: 800;
                background: transparent;
            }

            #SettingsNote {
                color: #8F8F8F;
                font-size: 12px;
                background: transparent;
            }
            """
        )


def run_gui() -> None:
    app = QApplication(sys.argv)
    window = XccMainWindow()
    window.show()
    sys.exit(app.exec())