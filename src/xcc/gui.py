from __future__ import annotations

import sys

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
        self.history_page = self._build_placeholder_page(
            "History",
            "Last run history will appear here.",
        )
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

        self.nav.currentRowChanged.connect(self.pages.setCurrentIndex)
        self.nav.setCurrentRow(0)

        self.select_source_button.clicked.connect(self._select_source)
        self.mode_group.buttonClicked.connect(self._clear_source)
        self.collect_button.clicked.connect(self._collect_and_copy)
    
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
        setup_card.setMinimumHeight(210)
        setup_layout = QVBoxLayout(setup_card)
        setup_layout.setContentsMargins(24, 18, 24, 18)
        setup_layout.setSpacing(16)

        setup_layout.addWidget(self._card_title("Setup"))

        mode_row = QHBoxLayout()
        mode_label = QLabel("Mode")
        mode_label.setObjectName("FieldLabel")
        mode_label.setFixedWidth(90)

        self.mode_group = QButtonGroup(self)
        self.mode_files = QRadioButton("Selected Files")
        self.mode_folder = QRadioButton("Full Folder")
        self.mode_git = QRadioButton("Git Changed Files")

        self.mode_folder.setChecked(True)

        for index, button in enumerate([self.mode_files, self.mode_folder, self.mode_git]):
            self.mode_group.addButton(button, index)
            mode_row.addWidget(button)

        mode_row.insertWidget(0, mode_label)
        mode_row.addStretch(1)

        source_row = QHBoxLayout()
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

        source_row.addWidget(source_label)
        source_row.addWidget(self.source_input, 1)
        source_row.addWidget(self.select_source_button)

        options_row = QHBoxLayout()
        options_label = QLabel("Options")
        options_label.setObjectName("FieldLabel")
        options_label.setFixedWidth(90)

        self.compact_checkbox = QCheckBox("Compact mode")
        self.compact_checkbox.setChecked(True)

        max_chars_label = QLabel("Max chars")
        max_chars_label.setObjectName("FieldLabelSmall")

        self.max_chars_input = QLineEdit(str(MAX_OUTPUT_CHARS))
        self.max_chars_input.setValidator(QIntValidator(1, 10_000_000, self))
        self.max_chars_input.setMaximumWidth(160)
        self.max_chars_input.setFixedHeight(38)

        options_row.addWidget(options_label)
        options_row.addWidget(self.compact_checkbox)
        options_row.addSpacing(24)
        options_row.addWidget(max_chars_label)
        options_row.addWidget(self.max_chars_input)
        options_row.addStretch(1)

        setup_layout.addLayout(mode_row)
        setup_layout.addLayout(source_row)
        setup_layout.addLayout(options_row)

        layout.addWidget(setup_card)

        stats_card = self._card()
        stats_card.setMinimumHeight(150)
        stats_layout = QVBoxLayout(stats_card)
        stats_layout.setContentsMargins(24, 18, 24, 18)
        stats_layout.setSpacing(14)

        stats_layout.addWidget(self._card_title("Last Run"))

        self.files_metric = self._metric_capsule("Files", "-")
        self.lines_metric = self._metric_capsule("Lines", "-")
        self.source_chars_metric = self._metric_capsule("Source Chars", "-")
        self.output_chars_metric = self._metric_capsule("Output Chars", "-")
        self.tokens_metric = self._metric_capsule("Output Tokens", "-")
        self.truncated_metric = self._metric_capsule("Truncated", "-")
        self.errors_metric = self._metric_capsule("Errors", "-")

        metrics_row_1 = QHBoxLayout()
        metrics_row_1.setSpacing(10)
        metrics_row_1.addWidget(self.files_metric)
        metrics_row_1.addWidget(self.lines_metric)
        metrics_row_1.addWidget(self.source_chars_metric)
        metrics_row_1.addWidget(self.output_chars_metric)

        metrics_row_2 = QHBoxLayout()
        metrics_row_2.setSpacing(10)
        metrics_row_2.addWidget(self.tokens_metric)
        metrics_row_2.addWidget(self.truncated_metric)
        metrics_row_2.addWidget(self.errors_metric)
        metrics_row_2.addStretch(1)

        stats_layout.addLayout(metrics_row_1)
        stats_layout.addLayout(metrics_row_2)

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
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(18)

        layout.addWidget(self._section_title("Settings"))

        card = self._card()
        card_layout = QVBoxLayout(card)

        card_layout.addWidget(QLabel(f"Default hotkey: {DEFAULT_HOTKEY}"))
        card_layout.addWidget(QLabel(f"Default max output chars: {MAX_OUTPUT_CHARS}"))
        card_layout.addWidget(QLabel("Theme: Black / Yellow"))
        card_layout.addWidget(QLabel("Settings persistence will be added later."))

        layout.addWidget(card)
        layout.addStretch(1)

        return page

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
        return label

    def _card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("Card")
        return card
    
    def _metric_capsule(self, label: str, value: str) -> QFrame:
        capsule = QFrame()
        capsule.setObjectName("MetricCapsule")
        capsule.setMinimumWidth(150)
        capsule.setFixedHeight(56)

        layout = QVBoxLayout(capsule)
        layout.setContentsMargins(12, 8, 12, 8)
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
            }

            #Sidebar::item {
                padding: 12px 14px;
                border-radius: 10px;
                color: #C9C9C9;
                background: transparent;
            }

            #Sidebar::item:selected {
                background: #F5C542;
                color: #111111;
                font-weight: 700;
            }

            #Sidebar::item:hover {
                background: #2A2412;
                color: #F5C542;
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
                font-weight: 700;
                background: transparent;
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
                background: #1A1A1A;
                border: 1px solid #6A5520;
                border-radius: 10px;
            }

            #MetricCapsule:hover {
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
            """
        )


def run_gui() -> None:
    app = QApplication(sys.argv)
    window = XccMainWindow()
    window.show()
    sys.exit(app.exec())