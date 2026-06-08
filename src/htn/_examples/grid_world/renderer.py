from __future__ import annotations

from typing import Protocol

from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

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
    """Centered terminal renderer for GridWorld using Rich."""

    def __init__(self) -> None:
        """Initialize the renderer."""
        self.console = Console()
        self.tick = 0

    def render(
        self,
        env: GridWorldLike,
        *,
        current_task: str | None = None,
        current_plan: list[str] | None = None,
        clear: bool = True,
    ) -> None:
        """
        Render the GridWorld environment centered in the terminal.

        :param env: GridWorld-like environment.
        :param current_task: Optional currently executing task.
        :param current_plan: Optional current symbolic plan.
        :param clear: Whether to clear the terminal before rendering.
        :return: None
        """
        self.tick += 1

        if clear:
            self.console.clear()

        grid = self._build_grid(env)
        status = self._build_status(env, current_task, current_plan)

        panel = Panel.fit(
            Align.center(grid),
            title="[bold cyan]GridWorld[/bold cyan]",
            subtitle=f"[dim]{status}[/dim]",
            border_style="cyan",
            padding=(1, 3),
        )

        self.console.print(Align.center(panel))

    def print_message(
        self,
        message: str,
        *,
        style: str = "bold white",
        clear: bool = False,
    ) -> None:
        """
        Print a centered message.

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
        Print a centered plan line.

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
        Print a centered execution step.

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

        return Text(" . ", style="dim")

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
