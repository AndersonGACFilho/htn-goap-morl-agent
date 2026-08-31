from htn.strategy.method_selection_strategy import MethodSelectionStrategy
from htn.tasks.types.method import Method
from htn.world.state import WorldState


class HeuristicBasedSearchStrategy(MethodSelectionStrategy):
    """Order feasible methods by an application-provided heuristic.

    Subclasses implement :meth:`_heuristic` with a lower-is-better score.
    """

    def order_methods(
        self,
        methods: list[Method],
        world_state: WorldState,
    ) -> list[Method]:
        """Return methods in ascending heuristic-score order."""
        return sorted(
            methods,
            key=lambda method: self._heuristic(
                method,
                world_state,
            ),
        )

    def _heuristic(
        self,
        method: Method,
        world_state: WorldState,
    ) -> float:
        """Score one method for the current symbolic state.

        Returns:
            A lower score for a method that should be explored earlier.
        """
        raise NotImplementedError
