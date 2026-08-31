from typing import List

from htn.tasks.types.task import Task


class Domain:
    """
    Represents a domain in the HTN planning framework.
    """

    tasks: List[Task]

    def __init__(self, tasks: List[Task]):
        """
        Initialize a new instance of Domain.
        Args:
            tasks: List of tasks in the domain.
        """
        self.tasks = tasks
