from __future__ import annotations

from typing import cast

from htn._examples.grid_world_multiobjective.env import GridWorldEnv
from htn._examples.grid_world_multiobjective.movement import action_from_step
from htn._examples.grid_world_multiobjective.pathfinder import (
    GridContext,
    GridPathfinder,
)
from htn.actions.action import Action
from htn.actions.action_status import ActionStatus
from htn.agent.agent import Agent
from htn.world.state import WorldState
from htn.world.world import World

Position = tuple[int, int]


class GridWorld(World):
    """
    Adapter between the HTN world abstraction and the Gymnasium GridWorld env.
    """

    env: GridWorldEnv

    @property
    def done(self) -> bool:
        return self.env.done

    def __init__(
        self,
        env: GridWorldEnv,
        world_state: WorldState,
        agent: Agent,
    ) -> None:
        """
        Initializes the GridWorld environment.
        :param env: the environment to use
        :param world_state: the world state to use
        :param agent: the agent to use
        """
        super().__init__(world_state, agent)
        self.env = env


class NavigateToPositionAction(Action):
    """
    Reactive navigation action.

    This action does not hardcode a sequence like:
        right, right, down, down

    Instead, each tick it:
        1. reads the current agent position;
        2. calculates a BFS path to the target;
        3. executes only the next step;
        4. returns RUNNING, SUCCESS, or FAILURE.
    """

    def __init__(
        self,
        target: Position,
        pathfinder: GridPathfinder,
    ) -> None:
        """
        Initializes the NavigateToPositionAction.
        :param target: the target position
        :param pathfinder: the pathfinder to use
        """
        self.target = target
        self.pathfinder = pathfinder

    def execute(self, world: World) -> ActionStatus:
        """
        Executes the action of Navigation to the target position.
        :param world: the world state to use
        :return: the status of the action execution
        """
        grid_world = cast(GridWorld, world)
        env = grid_world.env

        if env.agent_position == self.target:
            return ActionStatus.SUCCESS

        blocked = set(env.obstacles)

        if self.target != env.goal_position or not env.door_open:
            blocked.add(env.goal_position)

        context = GridContext(
            width=env.width,
            height=env.height,
            blocked=frozenset(blocked),
        )

        path = self.pathfinder.find_path(
            start=env.agent_position, goal=self.target, context=context
        )

        if len(path) < 2:
            return ActionStatus.FAILURE

        next_position = path[1]
        action_id = action_from_step(env.agent_position, next_position)

        env.step(action_id)

        if env.agent_position == self.target:
            return ActionStatus.SUCCESS

        return ActionStatus.RUNNING


class PickupKeyAction(Action):
    """
    Picks up the key if the agent is standing on the key tile.
    """

    def execute(self, world: World) -> ActionStatus:
        """
        Executes the action of picking up the key.
        :param world: the world state to use
        :return: the status of the action execution
        """
        grid_world = cast(GridWorld, world)
        env = grid_world.env

        env.step(GridWorldEnv.ACTION_PICKUP_KEY)

        if env.has_key:
            return ActionStatus.SUCCESS

        return ActionStatus.FAILURE


class OpenDoorAction(Action):
    """
    Opens the door if the agent is standing at the door and has the key.
    """

    def execute(self, world: World) -> ActionStatus:
        """
        Executes the action of opening the door.
        :param world: the world state to use
        :return: the status of the action execution
        """
        grid_world = cast(GridWorld, world)
        env = grid_world.env

        env.step(GridWorldEnv.ACTION_OPEN_DOOR)

        if env.door_open:
            return ActionStatus.SUCCESS

        return ActionStatus.FAILURE
