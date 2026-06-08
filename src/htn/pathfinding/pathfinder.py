from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

NodeT = TypeVar("NodeT")
ContextT = TypeVar("ContextT")


class Pathfinder(ABC, Generic[NodeT, ContextT]):
    """
    Generic pathfinder abstraction.

    NodeT:
        The type used to represent a point/node in the search space.
        Examples:
            - tuple[int, int] for grid positions
            - str for graph node ids
            - custom Node class for navigation meshes

    ContextT:
        Extra information required by the pathfinder.
        Examples:
            - grid width/height/blocked tiles
            - graph adjacency list
            - navmesh data
    """

    @abstractmethod
    def find_path(
        self,
        start: NodeT,
        goal: NodeT,
        context: ContextT,
    ) -> list[NodeT]:
        """
        Finds a path from start to goal.

        :param start: The initial node.
        :param goal: The target node.
        :param context: Extra pathfinding context.
        :return: A list containing the path from start to goal.
            Returns an empty list when no path exists.
        """
        pass
