from abc import ABC


class Task(ABC):
    """
    Base class for all tasks
    It contains the basic methods and fields.
    """

    def __init__(self, name: str):
        """
        Initialise the task
        :param name: Name of the task
        """
        self.name = name

    def __repr__(self) -> str:
        """
        String representation of the task
        :return: String representation of the task
        """
        return f"{self.__class__.__name__}(name={self.name!r})"
