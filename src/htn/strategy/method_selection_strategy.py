from abc import ABC, abstractmethod

from htn.tasks.types.method import Method
from htn.world import WorldState


class MethodSelectionStrategy(ABC):
    """Define how a planner orders feasible methods before backtracking.

    A strategy only changes the order in which the planner explores methods.
    The planner still validates every candidate through normal HTN
    decomposition and continues with the next method after a failed branch.
    """

    @abstractmethod
    def order_methods(
        self, methods: list[Method], world_state: WorldState
    ) -> list[Method]:
        """Return ``methods`` in the order in which they should be explored.

        Args:
            methods: Methods whose preconditions hold in ``world_state``.
            world_state: Symbolic state used to rank the candidate methods.

        Returns:
            The candidate methods in exploration order.
        """
        raise NotImplementedError
