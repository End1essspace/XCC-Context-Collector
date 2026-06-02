from __future__ import annotations

import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QButtonGroup,
    QCheckBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QPushButton,
    QRadioButton,
    QSizePolicy,
    QSpacerItem,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from . import __version__
from .config import DEFAULT_HOTKEY, MAX_OUTPUT_CHARS


class XccMainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("XCC Context Collector")
        self.setMinimumSize(920, 620)

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
        self.status_label.setFixedHeight(32)
        root_layout.addWidget(self.status_label)

        self.setCentralWidget(root)

        self.nav.currentRowChanged.connect(self.pages.setCurrentIndex)
        self.nav.setCurrentRow(0)

    def _build_header(self) -> QWidget:
        header = QFrame()
        header.setObjectName("Header")
        header.setFixedHeight(72)

        layout = QHBoxLayout(header)
        layout.setContentsMargins(24, 0, 24, 0)

        title_box = QVBoxLayout()
        title = QLabel("XCC Context Collector")
        title.setObjectName("HeaderTitle")

        subtitle = QLabel("AI-ready project context collector")
        subtitle.setObjectName("HeaderSubtitle")

        title_box.addWidget(title)
        title_box.addWidget(subtitle)

        self.header_status = QLabel("Ready")
        self.header_status.setObjectName("StatusCapsule")

        hotkey = QLabel(f"Hotkey: {DEFAULT_HOTKEY}")
        hotkey.setObjectName("HotkeyCapsule")

        layout.addLayout(title_box)
        layout.addStretch(1)
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
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(18)

        layout.addWidget(self._section_title("Collect Context"))

        mode_card = self._card()
        mode_layout = QVBoxLayout(mode_card)
        mode_layout.setContentsMargins(24, 18, 24, 18)
        mode_layout.setSpacing(10)
        mode_layout.addWidget(self._card_title("Mode"))

        self.mode_group = QButtonGroup(self)
        self.mode_files = QRadioButton("Selected Files")
        self.mode_folder = QRadioButton("Full Folder")
        self.mode_git = QRadioButton("Git Changed Files")

        self.mode_folder.setChecked(True)

        for index, button in enumerate([self.mode_files, self.mode_folder, self.mode_git]):
            self.mode_group.addButton(button, index)
            mode_layout.addWidget(button)

        layout.addWidget(mode_card)

        source_card = self._card()
        source_layout = QVBoxLayout(source_card)
        source_layout.setContentsMargins(24, 18, 24, 18)
        source_layout.setSpacing(10)
        source_layout.addWidget(self._card_title("Source"))

        source_row = QHBoxLayout()
        self.source_input = QLineEdit()
        self.source_input.setPlaceholderText("No source selected")
        self.source_input.setReadOnly(True)
        self.source_input.setFixedHeight(38)

        self.select_source_button = QPushButton("Select Source")
        self.select_source_button.setMinimumWidth(150)
        self.select_source_button.setFixedHeight(38)

        source_row.addWidget(self.source_input, 1)
        source_row.addWidget(self.select_source_button)

        source_layout.addLayout(source_row)
        layout.addWidget(source_card)

        options_card = self._card()
        options_layout = QVBoxLayout(options_card)
        options_layout.setContentsMargins(24, 18, 24, 18)
        options_layout.setSpacing(10)
        options_layout.addWidget(self._card_title("Options"))

        self.compact_checkbox = QCheckBox("Compact mode")
        self.compact_checkbox.setChecked(True)

        max_chars_row = QHBoxLayout()
        max_chars_label = QLabel("Max output chars")
        self.max_chars_input = QLineEdit(str(MAX_OUTPUT_CHARS))
        self.max_chars_input.setFixedHeight(36)
        self.max_chars_input.setMaximumWidth(180)

        max_chars_row.addWidget(max_chars_label)
        max_chars_row.addWidget(self.max_chars_input)
        max_chars_row.addStretch(1)

        options_layout.addWidget(self.compact_checkbox)
        options_layout.addLayout(max_chars_row)

        layout.addWidget(options_card)

        stats_card = self._card()
        stats_layout = QVBoxLayout(stats_card)
        stats_layout.setContentsMargins(24, 18, 24, 18)
        stats_layout.setSpacing(10)
        stats_layout.addWidget(self._card_title("Last Run"))

        self.stats_label = QLabel(
            "Files: -\n"
            "Lines: -\n"
            "Source Characters: -\n"
            "Output Characters: -\n"
            "Output Tokens: -\n"
            "Truncated: -\n"
            "Errors: -"
        )
        self.stats_label.setObjectName("StatsText")
        stats_layout.addWidget(self.stats_label)

        layout.addWidget(stats_card)

        layout.addItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        self.collect_button = QPushButton("Collect && Copy")
        self.collect_button.setObjectName("PrimaryButton")
        self.collect_button.setFixedHeight(46)

        layout.addWidget(self.collect_button)

        return page

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
        card.setMinimumHeight(96)
        return card

    def _apply_theme(self) -> None:
        self.setStyleSheet(
            """
            QMainWindow {
                background: #0E0E0E;
            }

            QWidget {
                background: #0E0E0E;
                color: #F2F2F2;
                font-family: Segoe UI;
                font-size: 13px;
            }

            #Header {
                background: #141414;
                border-bottom: 1px solid #2D2D2D;
            }

            #HeaderTitle {
                font-size: 20px;
                font-weight: 700;
                color: #F5C542;
            }

            #HeaderSubtitle {
                color: #A0A0A0;
            }

            #StatusCapsule,
            #HotkeyCapsule {
                background: #202020;
                border: 1px solid #3A3A3A;
                border-radius: 13px;
                padding: 5px 12px;
                color: #F2F2F2;
            }

            #HotkeyCapsule {
                color: #F5C542;
            }

            #Sidebar {
                background: #111111;
                border-right: 1px solid #2D2D2D;
                padding: 12px;
            }

            #Sidebar::item {
                padding: 12px 14px;
                border-radius: 8px;
                color: #BDBDBD;
            }

            #Sidebar::item:selected {
                background: #F5C542;
                color: #111111;
                font-weight: 700;
            }

            #Sidebar::item:hover {
                background: #202020;
                color: #F2F2F2;
            }

            #SectionTitle {
                font-size: 22px;
                font-weight: 700;
                color: #F2F2F2;
            }

            #Card {
                background: #171717;
                border: 1px solid #2D2D2D;
                border-radius: 12px;
                padding: 12px;
            }

            #CardTitle {
                color: #F5C542;
                font-weight: 700;
                margin-bottom: 6px;
            }

            QLineEdit {
                background: #0E0E0E;
                border: 1px solid #3A3A3A;
                border-radius: 8px;
                padding: 8px 10px;
                color: #F2F2F2;
            }

            QLineEdit:focus {
                border: 1px solid #F5C542;
            }

            QPushButton {
                background: #202020;
                border: 1px solid #3A3A3A;
                border-radius: 9px;
                padding: 9px 14px;
                color: #F2F2F2;
            }

            QPushButton:hover {
                background: #2A2A2A;
                border: 1px solid #F5C542;
            }

            #PrimaryButton {
                background: #F5C542;
                color: #111111;
                font-size: 15px;
                font-weight: 800;
                border: none;
            }

            #PrimaryButton:hover {
                background: #FFD95A;
            }

            QRadioButton,
            QCheckBox {
                spacing: 8px;
                padding: 4px 0;
            }

            #StatsText {
                color: #D8D8D8;
                line-height: 150%;
            }

            #StatusBar {
                background: #111111;
                border-top: 1px solid #2D2D2D;
                padding-left: 18px;
                color: #A0A0A0;
            }
            QRadioButton::indicator,
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
            }

            QRadioButton::indicator:unchecked,
            QCheckBox::indicator:unchecked {
                border: 1px solid #777777;
                background: #111111;
            }

            QRadioButton::indicator:checked,
            QCheckBox::indicator:checked {
                border: 1px solid #F5C542;
                background: #F5C542;
            }
            """
        )


def run_gui() -> None:
    app = QApplication(sys.argv)
    window = XccMainWindow()
    window.show()
    sys.exit(app.exec())