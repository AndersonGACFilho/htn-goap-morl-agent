from typing import Callable, List

from agent.agent_base import AgentBase

from htn.delegates import MulticastDelegate
from htn.planner.planner import Planner
from htn.tasks.types.task import Task
from htn.world.state import WorldState


class Agent(AgentBase):
    """
    Agent that can plan and execute high-level tasks.
    """

    planner: Planner
    world_state: WorldState
    plan: List[Task]
    on_world_state_change: MulticastDelegate[Callable[[WorldState], None]]

    def __init__(self, planner: Planner, world_state: WorldState):
        """
        The constructor for the Agent class.

        Initializes the agent with a planner, by:
        - Setting the planner property.
        - Setting the world state property to the world state of the planner.
        - Setting the plan property to an empty list
        - Setting the on_world_state_change property to a MulticastDelegate.

        :param planner: The planner to use for planning.
        """
        self.planner = planner
        self.world_state = world_state
        self.plan = []
        self.on_world_state_change = MulticastDelegate()

        self.on_world_state_change.add_handler(planner.update_world_state)
