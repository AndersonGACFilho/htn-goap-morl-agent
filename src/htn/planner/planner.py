from htn.strategy.method_selection_strategy import MethodSelectionStrategy
from htn.tasks.domains.domain import Domain
from htn.tasks.types.compound_task import CompoundTask
from htn.tasks.types.primitive_task import PrimitiveTask
from htn.tasks.types.task import Task
from htn.world.state import WorldState


class Planner:
    """Build primitive-task plans by recursively decomposing HTN tasks.

    A :class:`MethodSelectionStrategy` ranks methods after feasibility checks
    and before recursive decomposition. A strategy influences exploration
    order, never the planner's symbolic validity checks or backtracking.
    """

    domain: Domain
    _current_plan: list[Task]
    _strategy: MethodSelectionStrategy
    world_state_copy: WorldState

    def __init__(
        self, domain: Domain, world_state: WorldState, strategy: MethodSelectionStrategy
    ):
        """
        Initialize the planner with a domain, state snapshot, and strategy.

        Args:
            domain: Domain that defines the available root tasks.
            world_state: Initial symbolic state to copy for planning.
            strategy: Policy that orders feasible methods during decomposition.
        """
        self.domain = domain
        self._current_plan = []
        self.world_state_copy = world_state.copy()
        self._strategy = strategy

    def build_plan(self, tasks: list[Task]) -> list[Task] | None:
        """
        Builds an executable plan for the given task sequence.

        Tasks are planned in order. If a later task cannot currently be
        planned, the successfully planned prefix is returned so execution
        can proceed and planning can be resumed from the updated world state.

        Args:
            tasks: Root tasks to plan in order. The caller owns this sequence.

        Returns:
            The successfully planned primitive-task prefix, or ``None`` when
            the first task cannot be planned.
        """
        working_state = self.world_state_copy.copy()

        plan_result: list[Task] = []
        for task in tasks:
            result = self.recursive_planning(plan_result, working_state, task)

            if result is None:
                break

            plan_result, working_state = result

        if not plan_result:
            return None

        self._current_plan = plan_result

        return plan_result

    def recursive_planning(
        self,
        task_list: list[Task],
        world_state: WorldState,
        task: Task,
    ) -> tuple[list[Task], WorldState] | None:
        """
        Extend a planning branch for one task using simulated state.

        Feasible methods are passed to the configured strategy before the
        planner attempts them recursively. A failed decomposition still
        backtracks to the next ordered method.

        Args:
            task_list: Primitive tasks already planned for this branch.
            world_state: Simulated state for this branch.
            task: Task to decompose or validate.

        Returns:
            The extended task list and simulated state, or ``None`` when no
            valid decomposition exists.
        """

        if isinstance(task, PrimitiveTask):
            if not task.check_preconditions(world_state):
                return None

            planned_tasks = task_list.copy()
            planned_world_state = world_state.copy()

            planned_tasks.append(task)
            task.apply_effects(planned_world_state)
            return planned_tasks, planned_world_state

        if isinstance(task, CompoundTask):
            feasible_methods = task.get_feasible_methods(world_state)
            ordered_methods = self._strategy.order_methods(
                feasible_methods, world_state
            )

            for method in ordered_methods:
                method_tasks = task_list.copy()
                method_world_state = world_state.copy()
                method_failed = False

                for subtask in method.tasks:
                    result = self.recursive_planning(
                        method_tasks,
                        method_world_state,
                        subtask,
                    )

                    if result is None:
                        method_failed = True
                        break

                    method_tasks, method_world_state = result

                if method_failed:
                    continue

                return method_tasks, method_world_state

        print(f"Task '{task.name}' ({task.__class__.__name__}) cannot be planned.")
        return None

    def update_world_state(self, world_state: WorldState) -> None:
        """
        Updates the world state of the planner.
        Args:
            world_state: The new world state.
        Returns:
            None
        """
        self.world_state_copy = world_state.copy()
        self._current_plan = []

    def __repr__(self) -> str:
        """
        Returns a string representation of the planner.
        Returns:
            A string representation of the planner.
        """
        return f"Planner(domain={self.domain}, plan={self._current_plan}, world_state_copy={self.world_state_copy})"
