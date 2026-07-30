from __future__ import annotations

from dataclasses import dataclass
from textwrap import dedent


@dataclass(frozen=True, slots=True)
class UiPalette:
    """Semantic colors frozen by the v1.3.0 UI reference contract."""

    window_background: str = "#0E0F11"
    shell_surface: str = "#141517"
    sidebar_surface: str = "#111214"
    card_surface: str = "#17181A"
    raised_surface: str = "#1B1C1F"
    input_surface: str = "#101113"
    selected_surface: str = "#242016"
    hover_surface: str = "#1A1916"
    quiet_border: str = "#302D26"
    accent_border: str = "#57471F"
    accent: str = "#D2A533"
    accent_hover: str = "#E0B440"
    primary_text: str = "#F2F3F4"
    secondary_text: str = "#ADB1B7"
    muted_text: str = "#7F848C"
    success: str = "#69B985"
    warning: str = "#D5A13B"
    error: str = "#D86C6C"
    neutral: str = "#90959D"
    disabled_text: str = "#666A70"
    dark_text: str = "#111214"


@dataclass(frozen=True, slots=True)
class UiMetrics:
    """Shared geometry and typography values used across the supported GUI."""

    control_height: int = 40
    primary_action_height: int = 52
    footer_height: int = 36
    sidebar_width: int = 216
    metric_row_height: int = 58
    card_radius: int = 14
    control_radius: int = 10
    capsule_radius: int = 10
    page_margin: int = 28
    page_top_margin: int = 24
    standard_gap: int = 18
    compact_gap: int = 12
    page_title_size: int = 27
    card_title_size: int = 14
    body_size: int = 13
    helper_size: int = 12
    metric_value_size: int = 15


PALETTE = UiPalette()
METRICS = UiMetrics()


# The stylesheet is retained as one application-level sheet, but it is now
# owned by this module rather than by XccMainWindow. Legacy literal colors are
# translated to the semantic palette so later UI milestones can calibrate one
# token without editing page implementation code.
_BASE_APPLICATION_STYLESHEET = r"""
QMainWindow {
    background: #0F0F10;
}

QWidget {
    background: #0F0F10;
    color: #F2F2F2;
    font-family: Segoe UI;
    font-size: 13px;
}

#CollectPage {
    background: qlineargradient(
        x1: 0, y1: 0, x2: 1, y2: 1,
        stop: 0 #0F1012,
        stop: 0.55 #101113,
        stop: 1 #0D0E10
    );
}

#PageHeaderActions {
    background: transparent;
}

#StatusCapsule {
    background: #1A1A1A;
    border: 1px solid #302A1D;
    border-radius: 10px;
    padding: 4px 12px;
    color: #F2F2F2;
}

#RuntimeStatusCapsule {
    background: #1A1A1A;
    border: 1px solid #302A1D;
    border-radius: 10px;
}

#RuntimeStatusText {
    color: #F2F2F2;
    background: transparent;
    font-size: 12px;
    font-weight: 700;
}

#RuntimeStatusDot {
    background: #90959D;
    border: none;
    border-radius: 4px;
}

#HotkeyCapsule {
    background: #171717;
    border: 1px solid #302A1D;
    border-radius: 10px;
    padding: 4px 11px;
    color: #ADB1B7;
    font-size: 11px;
}

#Sidebar {
    background: #121212;
    border-right: 1px solid #2F2A1C;
}

#SidebarList {
    background: transparent;
    border: none;
    outline: none;
    padding: 0px;
}

#SidebarList::item {
    background: transparent;
    border: none;
    padding: 0px;
    margin: 0px;
}

#PageHeader {
    background: transparent;
}

#SectionTitle {
    font-size: 27px;
    font-weight: 700;
    color: #F2F2F2;
    background: transparent;
}

#Card {
    background: qlineargradient(
        x1: 0, y1: 0, x2: 0, y2: 1,
        stop: 0 #191A1D,
        stop: 1 #161719
    );
    border: 1px solid #302A1D;
    border-radius: 14px;
}

#CardTitle {
    color: #D6A93A;
    font-size: 14px;
    font-weight: 800;
    background: transparent;
    padding: 0px;
    margin: 0px;
}
#CardTitleRow,
#MetricGroupHeader,
#CardTitleIcon,
#MetricGroupIcon {
    background: transparent;
}

#FieldLabel {
    color: #D6D6D6;
    font-size: 13px;
    font-weight: 700;
    background: transparent;
}

#FieldLabelSmall {
    color: #B8B8B8;
    background: transparent;
}

QLineEdit {
    background: #101010;
    border: 1px solid #5A4820;
    border-radius: 10px;
    padding: 8px 10px;
    color: #F2F2F2;
    selection-background-color: #D6A93A;
    selection-color: #111111;
}

QLineEdit:hover {
    border: 1px solid #C79A2E;
}

QLineEdit:focus {
    border: 1px solid #D6A93A;
}

QPushButton {
    background: #1A1A1A;
    border: 1px solid #5A4820;
    border-radius: 10px;
    padding: 9px 14px;
    color: #F2F2F2;
}

QPushButton:hover {
    background: #232323;
    border: 1px solid #D6A93A;
    color: #D6A93A;
}

QPushButton:pressed {
    background: #2A2412;
}

#PrimaryButton {
    background: qlineargradient(
        x1: 0, y1: 0, x2: 0, y2: 1,
        stop: 0 #D8AD42,
        stop: 1 #C5962B
    );
    color: #111111;
    font-size: 15px;
    font-weight: 800;
    border: 1px solid #C79A31;
    border-radius: 11px;
    padding: 9px 18px;
}

#PrimaryButton:hover {
    background: qlineargradient(
        x1: 0, y1: 0, x2: 0, y2: 1,
        stop: 0 #E5BA50,
        stop: 1 #D2A533
    );
    border: 1px solid #D6A93A;
    color: #111111;
}

#PrimaryButton:pressed {
    background: #B98A28;
    border: 1px solid #B98A28;
}

QRadioButton,
QCheckBox {
    spacing: 8px;
    padding: 2px 0;
    background: transparent;
    font-size: 13px;
}

QRadioButton:hover,
QRadioButton:focus,
QCheckBox:hover,
QCheckBox:focus {
    color: #D6A93A;
}

QRadioButton::indicator,
QCheckBox::indicator {
    width: 16px;
    height: 16px;
    background: #101010;
    border: 1px solid #5A4820;
}

QRadioButton::indicator {
    border-radius: 8px;
}

QCheckBox::indicator {
    border-radius: 4px;
}

QRadioButton::indicator:hover,
QCheckBox::indicator:hover {
    border: 1px solid #D6A93A;
}

QRadioButton::indicator:checked,
QCheckBox::indicator:checked {
    background: #D6A93A;
    border: 1px solid #D6A93A;
}

#MetricCapsule {
    background: #18191C;
    border: 1px solid #302A1D;
    border-radius: 10px;
}

#MetricCapsule:hover {
    background: #1C1D20;
    border: 1px solid #443820;
}

#MetricLabel {
    color: #AFAFAF;
    font-size: 12px;
    background: transparent;
}

#MetricValue {
    color: #F2F2F2;
    font-size: 15px;
    font-weight: 800;
    background: transparent;
}

#MetricDivider {
    background: #302A1D;
    border: none;
    min-width: 1px;
    max-width: 1px;
}

#LastRunState {
    color: #9A9A9A;
    font-size: 12px;
    background: #111111;
    border: 1px solid #3A311C;
    border-radius: 8px;
    padding: 4px 10px;
    min-width: 132px;
}

#StatusBar {
    background: #151515;
    border-top: 1px solid #2F2A1C;
}

#FooterStatusDot {
    background: #90959D;
    border: none;
    border-radius: 4px;
}

#StatusText {
    color: #AFAFAF;
    font-size: 12px;
    background: transparent;
}

#StatusVersion {
    color: #858585;
    font-size: 11px;
    background: transparent;
}
#MetricGroupTitle {
    color: #E0E0E0;
    font-size: 14px;
    font-weight: 700;
    background: transparent;
}
#TransparentWidget {
    background: transparent;
}
#HistoryEntry {
    background: #181818;
    border: 1px solid #3A3018;
    border-radius: 10px;
}

#HistoryEntry:hover {
    background: #1E1B12;
    border: 1px solid #D6A93A;
}

#HistoryTime {
    color: #D6A93A;
    font-size: 12px;
    font-weight: 800;
    background: transparent;
}

#HistoryModeCapsule,
#HistoryOutcomeCapsule {
    background: #101010;
    border: 1px solid #5A4820;
    border-radius: 8px;
    padding: 3px 10px;
    color: #F2F2F2;
    font-size: 11px;
    font-weight: 700;
}

#HistoryOutcomeCapsule {
    color: #D6A93A;
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
    background: #463817;
    min-height: 28px;
    border-radius: 5px;
}

QScrollBar::handle:vertical:hover {
    background: #D6A93A;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical {
    background: transparent;
}
#PageSubtitle {
    color: #8F8F8F;
    font-size: 13px;
    background: transparent;
    padding: 0px;
    margin: 0px;
}

#SettingsSectionTitle {
    color: #D6A93A;
    font-size: 12px;
    font-weight: 800;
    background: transparent;
    margin-top: 0px;
}
#SettingsToggle {
    background: transparent;
    border: none;
    color: #D6D6D6;
    font-size: 11px;
    font-weight: 700;
}

#SettingsToggle:hover {
    color: #D6A93A;
}
#SettingsGroup {
    background: #141414;
    border: 1px solid #2F2A1C;
    border-radius: 12px;
}

#SettingsGroup:hover {
    border: 1px solid #5A4820;
}

#SettingsRow {
    background: #181818;
    border: 1px solid #2F2A1C;
    border-radius: 10px;
}

#SettingsRow:hover {
    background: #1E1B12;
    border: 1px solid #5A4820;
}

#SettingsRowTitle {
    color: #F2F2F2;
    font-size: 12px;
    font-weight: 800;
    background: transparent;
}

#SettingsRowDescription {
    color: #8F8F8F;
    font-size: 11px;
    background: transparent;
}

#SettingsRowValue {
    color: #D6A93A;
    font-size: 13px;
    font-weight: 800;
    background: transparent;
    min-width: 110px;
}
#AboutCard {
    background: #161616;
    border: 1px solid #302A1D;
    border-radius: 14px;
}

#AboutAppIcon {
    background: transparent;
}

#AboutTitle {
    color: #F2F2F2;
    font-size: 22px;
    font-weight: 800;
    background: transparent;
}

#AboutSubtitle {
    color: #D6A93A;
    font-size: 14px;
    font-weight: 700;
    background: transparent;
}

#AboutVersion {
    color: #8F8F8F;
    font-size: 12px;
    background: transparent;
}

#AboutDescription {
    color: #C9C9C9;
    font-size: 13px;
    background: transparent;
}

#AboutBadge {
    background: #181818;
    border: 1px solid #2F2A1C;
    border-radius: 10px;
    padding: 4px 12px;
    color: #D6A93A;
    font-size: 11px;
    font-weight: 800;
}

#AboutBadge:hover {
    background: #1E1B12;
    border: 1px solid #5A4820;
}

#AboutSectionTitle {
    color: #D6A93A;
    font-size: 13px;
    font-weight: 800;
    background: transparent;
}

#AboutInfoRow {
    background: #181818;
    border: 1px solid #2F2A1C;
    border-radius: 10px;
}

#AboutInfoLabel {
    color: #AFAFAF;
    font-size: 11px;
    font-weight: 700;
    background: transparent;
}

#AboutInfoValue {
    color: #D6A93A;
    font-size: 12px;
    font-weight: 800;
    background: transparent;
}

#AboutFooter {
    color: #8F8F8F;
    font-size: 12px;
    background: transparent;
    padding-top: 4px;
}
#SourceInputBox {
    background: #101010;
    border: 1px solid #5A4820;
    border-radius: 10px;
}

#SourceInputBox:hover {
    border: 1px solid #C79A2E;
}

#SourceInputBox[reviewable="true"] {
    border: 1px solid #5A4820;
    background: #141414;
}

#SourceInputBox[reviewable="true"]:hover {
    border: 1px solid #D6A93A;
    background: #1E1B12;
}

#SourceHelperText,
#OptionsHelperText {
    color: #8F8F8F;
    font-size: 11px;
    background: transparent;
}

#PastePathsButton {
    background: #171717;
    border: 1px solid #3A311C;
    color: #D6A93A;
    font-weight: 700;
}

#PastePathsButton:hover,
#PastePathsButton:focus {
    background: #1E1B12;
    border: 1px solid #D6A93A;
    color: #F2F2F2;
}

#SelectSourceButton {
    background: #101010;
    border: 1px solid #5A4820;
    color: #F2F2F2;
    font-weight: 700;
}

#SelectSourceButton:hover,
#SelectSourceButton:focus {
    background: #1E1B12;
    border: 1px solid #D6A93A;
    color: #D6A93A;
}

#SourceInputEmbedded {
    background: transparent;
    border: none;
    border-radius: 0px;
    padding: 0px;
    color: #F2F2F2;
    selection-background-color: #D6A93A;
    selection-color: #111111;
}

#SourceInputEmbedded:hover,
#SourceInputEmbedded:focus {
    border: none;
}

#ClearSourceButton {
    background: transparent;
    border: 1px solid #5A4820;
    border-radius: 12px;
    color: #D6A93A;
    font-size: 14px;
    font-weight: 800;
    padding: 0px;
    margin: 0px;
    text-align: center;
}

#ClearSourceButton:hover {
    background: #2A2412;
    border: 1px solid #D6A93A;
    color: #F2F2F2;
}

#ClearSourceButton:pressed {
    background: #D6A93A;
    border: 1px solid #D6A93A;
    color: #111111;
}

#PastePathsDialog {
    background: #0F0F10;
}

#DialogTitle {
    color: #F2F2F2;
    font-size: 20px;
    font-weight: 800;
    background: transparent;
}

#DialogDescription {
    color: #AFAFAF;
    font-size: 12px;
    background: transparent;
}

#DialogSummary {
    color: #D6A93A;
    font-size: 12px;
    font-weight: 700;
    background: #171717;
    border: 1px solid #3A311C;
    border-radius: 8px;
    padding: 8px 10px;
}

#PathListInput {
    background: #101010;
    border: 1px solid #5A4820;
    border-radius: 10px;
    padding: 10px;
    color: #F2F2F2;
    selection-background-color: #D6A93A;
    selection-color: #111111;
    font-family: Consolas;
    font-size: 12px;
}

#PathListInput:hover,
#PathListInput:focus {
    border: 1px solid #D6A93A;
}

#DialogPrimaryButton {
    background: #C79A31;
    border: 1px solid #C79A31;
    color: #111111;
    font-weight: 800;
}

#DialogPrimaryButton:hover {
    background: #D6A93A;
    border: 1px solid #D6A93A;
    color: #111111;
}

#DialogPrimaryButton:disabled {
    background: #2A2A2A;
    border: 1px solid #3A3A3A;
    color: #777777;
}

#SelectedFilesReviewDialog {
    background: #0F0F10;
}

#SelectedFilesCount {
    color: #D6A93A;
    font-size: 12px;
    font-weight: 800;
    background: #171717;
    border: 1px solid #3A311C;
    border-radius: 8px;
    padding: 5px 10px;
}

#ReviewRootInput {
    color: #B9B9B9;
}

#SelectedFilesReviewList {
    background: #101010;
    border: 1px solid #5A4820;
    border-radius: 10px;
    padding: 6px;
    outline: none;
    color: #E7E7E7;
    font-family: Consolas;
    font-size: 12px;
}

#SelectedFilesReviewList::item {
    min-height: 30px;
    border-radius: 6px;
    padding: 3px 8px;
}

#SelectedFilesReviewList::item:hover {
    background: #211D12;
    color: #F2F2F2;
}

#SelectedFilesReviewList::item:selected {
    background: #242016;
    color: #F2F2F2;
    border: 1px solid #57471F;
}
"""


_COLOR_REPLACEMENTS = {
    "#0F0F10": PALETTE.window_background,
    "#151515": PALETTE.shell_surface,
    "#121212": PALETTE.sidebar_surface,
    "#141414": PALETTE.card_surface,
    "#161616": PALETTE.card_surface,
    "#171717": PALETTE.raised_surface,
    "#181818": PALETTE.raised_surface,
    "#1A1A1A": PALETTE.raised_surface,
    "#101010": PALETTE.input_surface,
    "#2F2A1C": PALETTE.quiet_border,
    "#302A1D": PALETTE.quiet_border,
    "#3A3018": PALETTE.quiet_border,
    "#3A311C": PALETTE.quiet_border,
    "#40341D": PALETTE.accent_border,
    "#443820": PALETTE.accent_border,
    "#463817": PALETTE.accent_border,
    "#5A4820": PALETTE.accent_border,
    "#D6A93A": PALETTE.accent,
    "#C79A31": PALETTE.accent,
    "#C79A2E": PALETTE.accent_hover,
    "#F2F2F2": PALETTE.primary_text,
    "#D6D6D6": PALETTE.primary_text,
    "#E0E0E0": PALETTE.primary_text,
    "#E7E7E7": PALETTE.primary_text,
    "#AFAFAF": PALETTE.secondary_text,
    "#B8B8B8": PALETTE.secondary_text,
    "#B9B9B9": PALETTE.secondary_text,
    "#C9C9C9": PALETTE.secondary_text,
    "#8F8F8F": PALETTE.muted_text,
    "#858585": PALETTE.muted_text,
    "#9A9A9A": PALETTE.muted_text,
    "#777777": PALETTE.disabled_text,
    "#111111": PALETTE.dark_text,
}


def build_application_stylesheet() -> str:
    """Return the shared application stylesheet with semantic tokens applied."""

    stylesheet = dedent(_BASE_APPLICATION_STYLESHEET).strip()

    for source, replacement in _COLOR_REPLACEMENTS.items():
        stylesheet = stylesheet.replace(source, replacement)

    semantic_state_rules = _semantic_state_stylesheet()
    return f"{stylesheet}\n\n{semantic_state_rules}\n"


def build_tray_menu_stylesheet() -> str:
    """Return the tray-menu stylesheet using the same semantic palette."""

    template = r"""
    QMenu {
        background: @shell;
        border: 1px solid @accent_border;
        padding: 6px;
        color: @primary;
        font-family: Segoe UI;
        font-size: 12px;
    }

    QMenu::item {
        background: transparent;
        padding: 8px 28px 8px 22px;
        border-radius: 6px;
    }

    QMenu::item:selected {
        background: @accent;
        color: @dark_text;
    }

    QMenu::separator {
        height: 1px;
        background: @quiet_border;
        margin: 5px 4px;
    }
    """

    return (
        dedent(template)
        .replace("@shell", PALETTE.shell_surface)
        .replace("@accent_border", PALETTE.accent_border)
        .replace("@primary", PALETTE.primary_text)
        .replace("@accent", PALETTE.accent)
        .replace("@dark_text", PALETTE.dark_text)
        .replace("@quiet_border", PALETTE.quiet_border)
        .strip()
        + "\n"
    )


def _semantic_state_stylesheet() -> str:
    """Selectors used by current and later reusable status components."""

    template = r"""
    QLabel[state="success"],
    #MetricValue[state="success"] {
        color: @success;
    }

    QLabel[state="warning"],
    #MetricValue[state="warning"] {
        color: @warning;
    }

    QLabel[state="error"],
    #MetricValue[state="error"] {
        color: @error;
    }

    QLabel[state="neutral"],
    #MetricValue[state="neutral"] {
        color: @neutral;
    }

    #RuntimeStatusDot[state="success"],
    #FooterStatusDot[state="success"] {
        background: @success;
    }

    #RuntimeStatusDot[state="warning"],
    #FooterStatusDot[state="warning"] {
        background: @warning;
    }

    #RuntimeStatusDot[state="error"],
    #FooterStatusDot[state="error"] {
        background: @error;
    }

    #RuntimeStatusDot[state="neutral"],
    #FooterStatusDot[state="neutral"] {
        background: @neutral;
    }

    #SecondaryButton {
        background: @raised;
        border: 1px solid @accent_border;
        border-radius: 10px;
        color: @primary;
    }

    #SecondaryButton:disabled {
        background: @raised;
        border: 1px solid @quiet_border;
        color: @disabled;
    }

    #HelperText {
        color: @muted;
        font-size: 12px;
        background: transparent;
    }
    """

    return (
        dedent(template)
        .replace("@success", PALETTE.success)
        .replace("@warning", PALETTE.warning)
        .replace("@error", PALETTE.error)
        .replace("@neutral", PALETTE.neutral)
        .replace("@raised", PALETTE.raised_surface)
        .replace("@accent_border", PALETTE.accent_border)
        .replace("@quiet_border", PALETTE.quiet_border)
        .replace("@primary", PALETTE.primary_text)
        .replace("@disabled", PALETTE.disabled_text)
        .replace("@muted", PALETTE.muted_text)
        .strip()
    )
