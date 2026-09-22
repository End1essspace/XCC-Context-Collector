from __future__ import annotations

from dataclasses import dataclass

_MODIFIER_ALIASES = {
    "ctrl": "ctrl",
    "control": "ctrl",
    "alt": "alt",
    "shift": "shift",
    "win": "win",
    "windows": "win",
    "meta": "win",
}
_KEY_ALIASES = {
    "return": "enter",
    "esc": "escape",
    "ins": "insert",
    "del": "delete",
}
_NAMED_KEYS = {
    "backspace",
    "tab",
    "enter",
    "escape",
    "space",
    "pageup",
    "pagedown",
    "end",
    "home",
    "left",
    "up",
    "right",
    "down",
    "insert",
    "delete",
}
_MODIFIER_ORDER = ("ctrl", "alt", "shift", "win")


class HotkeyValidationError(ValueError):
    """Raised when a persisted/global hotkey string is not supported by XCC."""


@dataclass(frozen=True, slots=True)
class HotkeySpec:
    modifiers: tuple[str, ...]
    key: str

    @property
    def canonical(self) -> str:
        return "+".join((*self.modifiers, self.key))


def parse_hotkey_spec(hotkey: str) -> HotkeySpec:
    if not isinstance(hotkey, str):
        raise HotkeyValidationError("Hotkey must be a string.")

    raw_parts = [part.strip().casefold() for part in hotkey.split("+") if part.strip()]
    if len(raw_parts) < 2:
        raise HotkeyValidationError(f"Invalid hotkey: {hotkey}")

    modifiers: set[str] = set()
    key: str | None = None

    for part in raw_parts:
        modifier = _MODIFIER_ALIASES.get(part)
        if modifier is not None:
            if modifier in modifiers:
                raise HotkeyValidationError(
                    f"Invalid hotkey with duplicate modifier: {hotkey}"
                )
            modifiers.add(modifier)
            continue

        candidate = _KEY_ALIASES.get(part, part)
        if key is not None:
            raise HotkeyValidationError(
                f"Invalid hotkey with multiple keys: {hotkey}"
            )
        key = candidate

    if not modifiers:
        raise HotkeyValidationError(
            f"Global hotkey requires at least one modifier: {hotkey}"
        )
    if key is None:
        raise HotkeyValidationError(
            f"Invalid hotkey without a main key: {hotkey}"
        )
    if not _is_supported_key(key):
        raise HotkeyValidationError(f"Unsupported hotkey key: {key}")

    ordered = tuple(name for name in _MODIFIER_ORDER if name in modifiers)
    return HotkeySpec(ordered, key)


def normalize_hotkey(hotkey: str) -> str:
    return parse_hotkey_spec(hotkey).canonical


def _is_supported_key(key: str) -> bool:
    if len(key) == 1 and ("a" <= key <= "z" or "0" <= key <= "9"):
        return True
    if key.startswith("f") and key[1:].isdigit():
        return 1 <= int(key[1:]) <= 24
    return key in _NAMED_KEYS
