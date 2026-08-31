from __future__ import annotations

from htn._examples.grid_world_multiobjective.actions import (
    NavigateToPositionAction,
    OpenDoorAction,
    PickupKeyAction,
)
from htn._examples.grid_world_multiobjective.env import GridWorldEnv, Position
from htn._examples.grid_world_multiobjective.pathfinder import GridPathfinder
from htn.tasks.domains.domain import Domain
from htn.tasks.types.compound_task import CompoundTask
from htn.tasks.types.effects import Effects
from htn.tasks.types.method import Method
from htn.tasks.types.primitive_task import PrimitiveTask


def _position_effects(
    position: Position,
    *,
    at_key: bool = False,
    at_door: bool = False,
    at_goal: bool = False,
) -> Effects:
    """
    Build symbolic movement effects for the HTN planner.

    :param position: Position reached by the navigation task.
    :param at_key: Whether the agent should be considered at the key.
    :param at_door: Whether the agent should be considered at the door.
    :param at_goal: Whether the agent should be considered at the goal.
    :return: Effects dictionary compatible with PrimitiveTask.
    """
    x, y = position

    return {
        "agent_x": ("=", x),
        "agent_y": ("=", y),
        "at_key": ("=", at_key),
        "at_door": ("=", at_door),
        "at_goal": ("=", at_goal),
    }


def build_grid_world_domain(env: GridWorldEnv) -> Domain:
    """
    Build the GridWorld HTN domain from the configured environment.

    The HTN still knows only symbolic intentions:
        - ensure the key is collected;
        - ensure the door is open;
        - reach the goal.

    Concrete coordinates are read from the current environment layout.

    :param env: Configured GridWorld environment.
    :return: HTN domain for the current GridWorld layout.
    """
    pathfinder = GridPathfinder()

    go_to_key_effects: Effects = _position_effects(
        env.key_position,
        at_key=True,
    )

    go_to_key = PrimitiveTask(
        name="go_to_key",
        action=NavigateToPositionAction(
            target=env.key_position,
            pathfinder=pathfinder,
        ),
        preconditions={
            "has_key": ("=", False),
        },
        effects=go_to_key_effects,
    )

    pickup_key = PrimitiveTask(
        name="pickup_key",
        action=PickupKeyAction(),
        preconditions={
            "at_key": ("=", True),
            "has_key": ("=", False),
        },
        effects={
            "has_key": ("=", True),
            "at_key": ("=", True),
        },
    )

    go_to_door_effects: Effects = _position_effects(
        env.door_position,
        at_door=True,
    )

    go_to_door = PrimitiveTask(
        name="go_to_door",
        action=NavigateToPositionAction(
            target=env.door_position,
            pathfinder=pathfinder,
        ),
        preconditions={
            "has_key": ("=", True),
            "door_open": ("=", False),
        },
        effects=go_to_door_effects,
    )

    open_door = PrimitiveTask(
        name="open_door",
        action=OpenDoorAction(),
        preconditions={
            "at_door": ("=", True),
            "has_key": ("=", True),
            "door_open": ("=", False),
        },
        effects={
            "door_open": ("=", True),
        },
    )

    go_to_goal_effects: Effects = _position_effects(
        env.goal_position,
        at_goal=True,
    )
    go_to_goal_effects["done"] = ("=", True)

    go_to_goal = PrimitiveTask(
        name="go_to_goal",
        action=NavigateToPositionAction(
            target=env.goal_position,
            pathfinder=pathfinder,
        ),
        preconditions={
            "door_open": ("=", True),
            "done": ("=", False),
        },
        effects=go_to_goal_effects,
    )

    ensure_has_key = CompoundTask(
        name="ensure_has_key",
        methods=[
            Method(
                preconditions={
                    "has_key": ("=", True),
                },
                tasks=[],
            ),
            Method(
                preconditions={
                    "has_key": ("=", False),
                },
                tasks=[
                    go_to_key,
                    pickup_key,
                ],
            ),
        ],
    )

    ensure_door_open = CompoundTask(
        name="ensure_door_open",
        methods=[
            Method(
                preconditions={
                    "door_open": ("=", True),
                },
                tasks=[],
            ),
            Method(
                preconditions={
                    "door_open": ("=", False),
                    "has_key": ("=", True),
                },
                tasks=[
                    go_to_door,
                    open_door,
                ],
            ),
        ],
    )

    escape_grid = CompoundTask(
        name="escape_grid",
        methods=[
            Method(
                preconditions={
                    "done": ("=", False),
                    "door_open": ("=", True),
                },
                tasks=[
                    go_to_goal,
                ],
            ),
            Method(
                preconditions={
                    "done": ("=", False),
                    "door_open": ("=", False),
                },
                tasks=[
                    ensure_has_key,
                    ensure_door_open,
                    go_to_goal,
                ],
            ),
        ],
    )

    return Domain(tasks=[escape_grid])
