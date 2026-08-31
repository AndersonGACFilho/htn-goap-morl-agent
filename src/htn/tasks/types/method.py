from htn.tasks.types.preconditions import Preconditions
from htn.tasks.types.task import Task


class Method:
    """
    Method is a class that represents a method of a compound task.

    It contains preconditions and a list of tasks that
    can be executed in a specific order.
    """

    preconditions: Preconditions
    tasks: list[Task]

    def __init__(
        self,
        preconditions: Preconditions,
        tasks: list[Task],
    ):
        """
        Initialize a method with preconditions and tasks.

        Args:
            preconditions: The preconditions for the method
            tasks: The tasks to be executed in the method
        """
        self.tasks = tasks
        self.preconditions = preconditions

    def get_task(self, index: int) -> Task:
        """
        Get a task from the method by index.

        Args:
            index: The index of the task to retrieve
        Returns:
            The task at the specified index
        """
        return self.tasks[index]

    def get_tasks(self) -> list[Task]:
        """
        Get the tasks of the method.

        Returns:
            The tasks of the method
        """
        return self.tasks

    def get_preconditions(self) -> Preconditions:
        """
        Get the preconditions of the method.

        Returns:
            The preconditions of the method
        """
        return self.preconditions
