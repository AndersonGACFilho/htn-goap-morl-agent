from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from htn.world.state import WorldState

WorldT = TypeVar("WorldT")


class Sensor(ABC, Generic[WorldT]):
    """
    Base abstraction for sensors.

    A sensor reads concrete runtime data from a world/environment and writes
    symbolic facts into the HTN WorldState.

    Sensors do not decide actions.
    Sensors do not plan.
    Sensors only observe and update the symbolic blackboard.
    """

    @abstractmethod
    def sense(self, world: WorldT, world_state: WorldState) -> None:
        """
        Read the concrete world and update the symbolic world state.

        :param world: Runtime world/environment adapter.
        :param world_state: Symbolic HTN world state to update.
        :return: None.
        """
        pass
