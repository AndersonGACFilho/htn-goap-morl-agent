from htn.strategy.method_selection_strategy import MethodSelectionStrategy
from htn.tasks.types.method import Method
from htn.world.state import WorldState


class DepthFirstSearchStrategy(MethodSelectionStrategy):
    """Preserve domain declaration order for depth-first HTN search."""

    def order_methods(
        self,
        methods: list[Method],
        world_state: WorldState,
    ) -> list[Method]:
        """Return feasible methods without changing their declaration order."""
        return methods
