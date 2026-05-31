from htn.tasks.types.method import Method
from htn.tasks.types.preconditions import are_preconditions_satisfied
from htn.tasks.types.task import Task
from htn.world.state import WorldState


class CompoundTask(Task):
    """
    A compound task is a task that contains other tasks.
    """

    methods: list[Method]

    # Constructor
    def __init__(
        self,
        methods: list[Method],
    ):
        """
        Initialize a compound task.
        """
        self.methods = methods

    # Getters
    def get_methods(self) -> list[Method]:
        """
        Get the methods of the compound task.

        :return: The methods of the compound task
        """
        return self.methods

    def get_method(self, index: int) -> Method:
        """
        Get a method by its index.

        :param index: The index of the method to retrieve
        :return: The method at the specified index
        """
        return self.methods[index]

    def get_feasible_methods(self, world_state: WorldState) -> list[Method]:
        """
        Get the possible methods for the given world state, validated by preconditions.
        :param world_state: The world state to validate preconditions for
        :return: A list of applicable methods or an empty list if no applicable methods are found
        """
        feasible_methods = []
        for method in self.methods:
            method_preconditions = method.get_preconditions()
            if are_preconditions_satisfied(method_preconditions, world_state):
                feasible_methods.append(method)

        return feasible_methods
