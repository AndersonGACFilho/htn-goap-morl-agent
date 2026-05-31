from htn.actions.action import Action
from htn.tasks.types.task import Task


class PrimitiveTask(Task):
    """
    A primitive task is a task that cannot be decomposed further and represents a basic action or operation.
    """

    preconditions: dict[str, bool] = {}
    effects: dict[str, bool] = {}
    actions: list[Action] = []

    # Constructor
    def __init__(self):
        """
        Initialize the new instance of the Task class.
        """
        pass

    def get_preconditions(self) -> dict[str, bool]:
        """
        Get the preconditions of the task.
        :return: The list of preconditions
        """
        return self.preconditions

    def get_effects(self) -> dict[str, bool]:
        """
        Get the effects of the task.
        :return: The list of effects
        """
        return self.effects

    def get_actions(self) -> list[Action]:
        """
        Get the actions that can be performed by the task.
        :return: The list of actions
        """
        return self.actions

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
