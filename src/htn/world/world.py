from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING

from htn.world.state import WorldState

if TYPE_CHECKING:
    from htn.agent.agent import Agent


class World(ABC):
    """
    Base world abstraction used by the HTN runtime.

    World must not import Agent at runtime, otherwise it creates a circular
    import between Agent -> Planner -> Preconditions -> World -> Agent.
    """

    world_state: WorldState
    agent: Agent

    def __init__(self, world_state: WorldState, agent: Agent):
        """
        Initialize the world with shared state and an agent.

        :param world_state: The world state used by the runtime.
        :param agent: The agent acting in the world.
        """
        self.world_state = world_state
        self.agent = agent
