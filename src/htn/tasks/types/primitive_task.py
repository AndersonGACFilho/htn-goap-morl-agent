from typing import TypeAlias

from htn.actions.action import Action
from htn.tasks.types.preconditions import Preconditions, are_preconditions_satisfied
from htn.tasks.types.task import Task
from htn.utils import WorldValue, apply_effect
from htn.world.state import WorldState

Effects: TypeAlias = dict[str, tuple[str, WorldValue]]


class PrimitiveTask(Task):
    """
    A primitive task is a task that cannot be decomposed further and represents a basic action or operation.
    """

    preconditions: Preconditions
    effects: Effects
    action: Action

    # Constructor
    def __init__(
        self,
        action: Action,
        preconditions: Preconditions | None = None,
        effects: Effects | None = None,
    ):
        """
        Initialize the new instance of the Task class.
        :param action: The action that can be performed by the task
        :param preconditions: The preconditions of the task
        :param effects: The effects of the task
        """
        self.action = action
        self.preconditions = preconditions or {}
        self.effects = effects or {}

    def get_action(self) -> Action:
        """
        Get the action that can be performed by the task.
        :return: The action
        """
        return self.action

    def get_preconditions(self) -> Preconditions:
        """
        Get the preconditions of the task.

        :return: The preconditions of the task
        """
        return self.preconditions

    def get_effects(self) -> Effects:
        """
        Get the effects of the task.

        :return: The effects of the task
        """
        return self.effects

    def apply_effects(self, world_state: WorldState) -> None:
        """
        Applies the effects of the element to the given world state.
        :param world_state: The world state to apply the effects to
        """
        for key, effect in self.effects.items():
            operator, value = effect
            current_value = world_state.get_state(key)

            world_state.set_state(
                key,
                apply_effect(current_value, operator, value),
            )

    def check_preconditions(self, world_state: WorldState) -> bool:
        """
        Checks whether all preconditions are satisfied by the given world state.
        :param world_state: The current world state
        :return: True if all preconditions are satisfied, False otherwise
        """
        return are_preconditions_satisfied(self.preconditions, world_state)

    # Representation methods
    def __str__(self):
        """
        ToString method
        :return: A string representation of the task
        """
        return str(
            {
                "type": self.__class__.__name__,
                "preconditions": self.preconditions,
                "effects": self.effects,
            }
        )

    def __repr__(self):
        """
        Representation method
        :return: A string representation of the task
        """
        return str(self)
