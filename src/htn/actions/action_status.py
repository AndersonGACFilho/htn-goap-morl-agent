from enum import Enum


class ActionStatus(Enum):
    """
    Enum class to represent actions status
    """

    RUNNING = "running"
    SUCCESS = "success"
    FAILURE = "failure"
