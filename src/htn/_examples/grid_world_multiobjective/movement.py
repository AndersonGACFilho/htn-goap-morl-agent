from __future__ import annotations

from htn._examples.grid_world_multiobjective.env import GridWorldEnv

Position = tuple[int, int]


def action_from_step(
    current: Position,
    next_position: Position,
) -> int:
    """
    Convert a neighboring grid step into a GridWorld action id.

    :param current: Current grid position.
    :param next_position: Adjacent grid position to move to.
    :return: GridWorld action id for the movement.
    """
    current_x, current_y = current
    next_x, next_y = next_position

    dx = next_x - current_x
    dy = next_y - current_y

    if dx == 1 and dy == 0:
        return GridWorldEnv.ACTION_RIGHT

    if dx == -1 and dy == 0:
        return GridWorldEnv.ACTION_LEFT

    if dx == 0 and dy == 1:
        return GridWorldEnv.ACTION_DOWN

    if dx == 0 and dy == -1:
        return GridWorldEnv.ACTION_UP

    raise ValueError(f"Invalid movement from {current} to {next_position}")
