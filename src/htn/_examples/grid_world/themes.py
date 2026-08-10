from __future__ import annotations

from rich.terminal_theme import DEFAULT_TERMINAL_THEME, TerminalTheme

_ORANGE_THEME = TerminalTheme(
    background=(255, 255, 255),
    foreground=(191, 54, 12),
    normal=[
        (33, 33, 33),
        (216, 67, 21),
        (1, 87, 155),
        (239, 108, 0),
        (21, 101, 192),
        (13, 71, 161),
        (2, 119, 189),
        (255, 255, 255),
    ],
    bright=[
        (0, 0, 0),
        (191, 54, 12),
        (13, 71, 161),
        (230, 81, 0),
        (13, 71, 161),
        (74, 20, 140),
        (1, 87, 155),
        (255, 255, 255),
    ],
)


class GridWorldTheme:
    """Named color theme for GridWorld SVG exports."""

    NORMAL = "normal"
    ORANGE = "orange"

    _PRESETS: dict[str, TerminalTheme] = {
        NORMAL: DEFAULT_TERMINAL_THEME,
        ORANGE: _ORANGE_THEME,
    }

    def __init__(self, name: str = ORANGE) -> None:
        """
        :param name: One of GridWorldTheme.NORMAL or GridWorldTheme.ORANGE.
        :raises ValueError: If `name` isn't a known preset.
        """
        if name not in self._PRESETS:
            available = ", ".join(self._PRESETS)
            raise ValueError(f"Unknown theme {name!r}. Available: {available}")

        self.name = name
        self.terminal_theme = self._PRESETS[name]
