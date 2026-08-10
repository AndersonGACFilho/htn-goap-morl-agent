from __future__ import annotations

import os
from typing import Protocol

from env import GridWorldEnv
from rich.align import Align
from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from themes import GridWorldTheme

Position = tuple[int, int]


class GridWorldLike(Protocol):
    """Protocol for objects that expose GridWorld rendering state."""

    width: int
    height: int

    agent_position: Position
    key_position: Position
    door_position: Position
    goal_position: Position
    obstacles: set[Position]

    has_key: bool
    door_open: bool
    done: bool


class RichGridWorldRenderer:
    """Centered terminal renderer for GridWorld using Rich.

    Every tick is rendered as a single Panel with fixed-height,
    fixed-width reserved lines for optional content (banner, plan
    announcement, step message, result message). This guarantees
    every exported SVG frame has identical dimensions, so no
    black-border padding is needed when assembling the GIF.
    """

    PANEL_WIDTH = 40

    def __init__(self, env: GridWorldEnv, theme: GridWorldTheme | None = None) -> None:
        """
        Initialize the renderer.

        :param: env: the current env config
        :param theme: color theme for SVG export. Defaults to GridWorldTheme(GridWorldTheme.ORANGE).
        """
        os.makedirs("images", exist_ok=True)
        self.console = Console(record=True, width=self.PANEL_WIDTH + 10, height=40)
        self.theme = theme or GridWorldTheme(GridWorldTheme.ORANGE)
        self.tick = 0
        self.config = []
        self.config.append(f"width={env.width}")
        self.config.append(f"height={env.height}")
        self.config.append(f"has_key={env.has_key}")
        self.config.append(f"door_open={env.door_open}")

    def render(
        self,
        env: GridWorldLike,
        *,
        banner: str | None = None,
        current_task: str | None = None,
        current_plan: list[str] | None = None,
        plan_announcement: list[str] | None = None,
        result_message: str | None = None,
        result_style: str = "bold white",
        clear: bool = True,
    ) -> None:
        """
        Render the GridWorld environment centered in the terminal.

        :param env: GridWorld-like environment.
        :param banner: Optional one-off banner line (e.g. "Initial world:").
        :param current_task: Optional currently executing task.
        :param current_plan: Optional current symbolic plan (for the status line).
        :param plan_announcement: Optional newly produced HTN plan to announce.
        :param result_message: Optional outcome message for this tick.
        :param result_style: the result line color
        :param clear: Whether to clear the terminal before rendering.
        :return: None
        """
        self.tick += 1

        if clear:
            self.console.clear()

        grid = self._build_grid(env)
        status = self._build_status(env, current_task, current_plan)

        banner_line = self._reserved_line(banner or "", style="bold cyan")

        plan_line = self._reserved_line(
            f"New plan: {' -> '.join(plan_announcement)}" if plan_announcement else "",
            style="bold yellow",
        )

        step_line = self._reserved_line(
            f"Tick {self.tick}: executing {current_task}" if current_task else "",
            style="bold green",
        )

        result_line = self._reserved_line(result_message or "", style=result_style)

        body = Group(
            banner_line,
            plan_line,
            step_line,
            Align.center(grid),
            result_line,
        )

        subtitle_text = Text(status, style="grey42", overflow="ellipsis")
        subtitle_text.no_wrap = True

        panel = Panel(
            body,
            title="[bold cyan]GridWorld[/bold cyan]",
            subtitle=subtitle_text,
            border_style="cyan",
            padding=(1, 3),
            width=self.PANEL_WIDTH,
        )

        self.console.print(Align.center(panel))

    @staticmethod
    def _reserved_line(content: str, *, style: str) -> Text:
        """
        Build a single, non-wrapping line that always occupies exactly
        one row of height, whether it has content or is blank.

        :param content: Line text, or "" to reserve a blank line.
        :param style: Rich style applied when content is present.
        :return: A centered, non-wrapping Text renderable.
        """
        text = Text(content, style=style if content else "", justify="center")
        text.no_wrap = True
        text.overflow = "ellipsis"
        return text

    def print_message(
        self,
        message: str,
        *,
        style: str = "bold white",
        clear: bool = False,
    ) -> None:
        """
        Print a standalone centered message (not part of an exported frame).
        Useful for final summaries or progress logs outside the tick loop.

        :param message: Message to print.
        :param style: Rich style for the message.
        :param clear: Whether to clear the terminal before printing.
        :return: None
        """
        if clear:
            self.console.clear()

        text = Text(message, style=style)
        self.console.print(Align.center(text))

    def print_plan(
        self,
        plan: list[str],
        *,
        clear: bool = False,
    ) -> None:
        """
        Print a standalone centered plan panel. Not used per-tick in the
        main loop anymore (folded into render() instead), kept for
        ad-hoc/debug use.

        :param plan: Current symbolic plan.
        :param clear: Whether to clear the terminal before printing.
        :return: None
        """
        if clear:
            self.console.clear()

        plan_text = " -> ".join(plan)
        panel = Panel.fit(
            Text(plan_text, style="bold yellow"),
            title="[bold]New HTN plan[/bold]",
            border_style="yellow",
            padding=(0, 2),
        )

        self.console.print(Align.center(panel))

    def print_step(
        self,
        tick: int,
        task_name: str,
    ) -> None:
        """
        Print a standalone centered execution step. Not used per-tick in
        the main loop anymore (folded into render() instead), kept for
        ad-hoc/debug use.

        :param tick: Current execution tick.
        :param task_name: Task being executed.
        :return: None
        """
        message = f"Tick {tick}: executing {task_name}"
        self.print_message(message, style="bold green")

    def _build_grid(self, env: GridWorldLike) -> Table:
        """
        Build the visual grid.

        :param env: GridWorld-like environment.
        :return: A Rich table representing the grid.
        """
        table = Table.grid(expand=False)

        for _ in range(env.width):
            table.add_column(justify="center", width=3)

        for y in range(env.height):
            row: list[Text] = []

            for x in range(env.width):
                row.append(self._cell(env, (x, y)))

            table.add_row(*row)

        return table

    def _cell(self, env: GridWorldLike, position: Position) -> Text:
        """
        Build one styled cell.

        :param env: GridWorld-like environment.
        :param position: Cell position.
        :return: Styled cell text.
        """
        if position == env.agent_position:
            return Text(" A ", style="bold white on blue")

        if position in env.obstacles:
            return Text(" X ", style="bold white on red")

        if position == env.key_position and not env.has_key:
            return Text(" K ", style="bold black on yellow")

        if position == env.door_position:
            if env.door_open:
                return Text(" O ", style="bold white on green")
            return Text(" D ", style="bold white on magenta")

        if position == env.goal_position:
            return Text(" G ", style="bold white on cyan")

        return Text(" . ", style="grey62")

    def _build_status(
        self,
        env: GridWorldLike,
        current_task: str | None,
        current_plan: list[str] | None,
    ) -> str:
        """
        Build the compact status line.

        :param env: GridWorld-like environment.
        :param current_task: Optional current task.
        :param current_plan: Optional symbolic plan.
        :return: A formatted status string.
        """
        status_parts = [
            f"tick={self.tick}",
            f"agent={env.agent_position}",
            f"key={env.has_key}",
            f"door={'open' if env.door_open else 'closed'}",
            f"done={env.done}",
        ]

        if current_task:
            status_parts.append(f"task={current_task}")

        if current_plan:
            status_parts.append(f"plan={' -> '.join(current_plan)}")

        return " | ".join(status_parts)

    def export(self):
        """
        Exports the current tick into svg images

        :return: the path to the generated image
        """
        title = f"{' '.join(self.config)} Tick {self.tick}"

        self.console.save_svg(
            f"images/{title}.svg",
            title=title,
            theme=self.theme.terminal_theme,
        )

        return f"images/{title}.svg"
