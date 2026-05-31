from htn.tasks.types.task import Task


class Method:
    """
    Method is a class that represents a method of a compound task.

    It contains preconditions, effects, and a list of tasks that
    can be executed in a specific order.
    """

    preconditions: dict[str, bool] = {}
    effects: dict[str, bool] = {}
    tasks: list[Task] = []

    def __init__(self):
        super().__init__()

    def get_preconditions(self) -> dict[str, bool]:
        return self.preconditions

    def get_effects(self) -> dict[str, bool]:
        return self.effects

    def get_task(self, index: int) -> Task:
        return self.tasks[index]

    def get_tasks(self) -> list[Task]:
        return self.tasks


class CompoundTask(Task):
    """
    A compound task is a task that contains other tasks.
    """

    methods: list[Method] = []

    # Constructor
    def __init__(self):
        """
        Initialize a compound task.
        """
        super().__init__()

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

    def get_method_by_preconditions(
        self, preconditions: dict[str, bool]
    ) -> Method | None:
        """
        Get a method by its preconditions.

        :param preconditions: The preconditions to search for
        :return: The method with matching preconditions, or None if not found
        """
        for method in self.methods:
            if method.get_preconditions() == preconditions:
                print(f"Method found for preconditions: {preconditions}")
                return method
        print(f"Method not found for preconditions: {preconditions}")
        return None
