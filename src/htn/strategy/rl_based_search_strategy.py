from htn.strategy.method_selection_strategy import MethodSelectionStrategy
from htn.tasks.types.method import Method
from htn.world.state import WorldState


class RLBasedSearchStrategy(MethodSelectionStrategy):
    """Define the integration point for RL-guided method ordering.

    The strategy retains a reference to the RL agent, but does not prescribe
    a value function, policy interface, or ordering rule. Subclasses must
    implement :meth:`order_methods`. HTN feasibility checks and backtracking
    remain the responsibility of :class:`~htn.planner.planner.Planner`.
    """

    def __init__(
        self,
        agent,
    ):
        """Initialize the strategy with the RL agent used by a subclass."""
        self.agent = agent

    def order_methods(
        self,
        methods: list[Method],
        world_state: WorldState,
    ) -> list[Method]:
        """Order feasible methods according to an RL-specific policy.

        Subclasses define how the agent and symbolic state determine the
        ordering. The base implementation is intentionally not executable.
        """
        raise NotImplementedError
