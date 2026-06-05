from htn.agent.agent import Agent
from htn.world.state import WorldState


class World:
    """
    This class represents the world in which the HTN planner operates.
    It contains the state of the world and provides methods to interact with it.
    """

    world_state: WorldState
    agent: Agent

    def __init__(self, world_state: WorldState, agent: Agent):
        self.world_state = world_state
        self.agent = agent
