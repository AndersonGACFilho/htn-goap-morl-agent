from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from htn.actions.action_status import ActionStatus

if TYPE_CHECKING:
    from htn.world.world import World


class Action(ABC):
    """
    Base class for all executable actions.

    Actions return a status because some actions can take multiple ticks,
    such as navigation/pathfinding actions.
    """

    @abstractmethod
    def execute(self, world: "World") -> ActionStatus:
        """
        Execute the action against the world.

        :param world: The world where the action will be executed.
        :return: ActionStatus.RUNNING if the action is still in progress.
            ActionStatus.SUCCESS if the action finished successfully.
            ActionStatus.FAILURE if the action failed.
        """
        pass
