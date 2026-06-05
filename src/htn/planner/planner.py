from htn.tasks.domains.domain import Domain
from htn.tasks.types.compound_task import CompoundTask
from htn.tasks.types.primitive_task import PrimitiveTask
from htn.tasks.types.task import Task
from htn.world.state import WorldState


class Planner:
    """
    HTN planner for planning high-level tasks.
    """

    domain: Domain
    current_plan: list[Task]
    world_state_copy: WorldState

    def __init__(self, domain: Domain, world_state: WorldState):
        """
        Initializes the planner with a given domain.
        :param domain: The domain to plan for.
        :param world_state: The initial world state.
        :return: None
        """
        self.domain = domain
        self.current_plan = []
        self.world_state_copy = world_state.copy()

    def build_plan(self) -> list[Task]:
        """
        Plans a sequence of tasks based on the given domain and world state.
        :return: A list of tasks to be executed.
        """
        self.current_plan = []

        if not self.domain:
            raise ValueError("Domain is not set.")
        if not self.world_state_copy:
            raise ValueError("World State is not set.")

        working_state = self.world_state_copy.copy()

        for domain_task in self.domain.tasks:
            result = self.recursive_planning([], working_state, domain_task)
            if result:
                tasks_result, world_state_result = result
                self.current_plan.extend(tasks_result)
                working_state = world_state_result

        return self.current_plan

    def recursive_planning(
        self,
        task_list: list[Task],
        world_state: WorldState,
        task: Task,
    ) -> tuple[list[Task], WorldState] | None:
        """
        Plans a sequence of tasks based on the given domain and simulated world state.
        :param task_list: A list of tasks to be executed.
        :param world_state: The simulated world state for this planning branch.
        :param task: The task to be planned.
        :return: A tuple containing the planned tasks and resulting simulated world state,
        or None if the task cannot be planned.
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

            for method in feasible_methods:
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
        :param world_state: The new world state.
        :return: None
        """
        self.world_state_copy = world_state.copy()
        self.current_plan = []

    def __repr__(self) -> str:
        """
        Returns a string representation of the planner.
        :return: A string representation of the planner.
        """
        return f"Planner(domain={self.domain}, plan={self.current_plan}, world_state_copy={self.world_state_copy})"
