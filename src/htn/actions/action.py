from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from htn.world.world import World


class Action(ABC):
    """
    Base class for all actions
    It contains the basic methods and fields.
    """

    @abstractmethod
    def execute(self, world: World) -> None:
        """
        This method is used to execute the action
        :return: None
        """
        pass
