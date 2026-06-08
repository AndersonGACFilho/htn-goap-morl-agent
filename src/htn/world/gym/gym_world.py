from abc import abstractmethod

import gymnasium as gym

from htn.agent.agent import Agent
from htn.world import World, WorldState


class GymWorld(World):
    """
    Extends World class with a live Gymnasium environment.
    So the env.step can be called by Actions
    """

    env: gym.Env
    last_obs: object
    last_reward: float
    done: bool

    def __init__(self, env: gym.Env, world_state: WorldState, agent: Agent):
        """
        Initializes GymWorld class
        :param env: Gym environment
        :param world_state: Gym world state
        :param agent: Agent in the world
        """
        super().__init__(world_state, agent)
        self.env = env
        self.last_reward = 0.0
        self.done = False
        self.last_obs = None

    @abstractmethod
    def update_from_obs(self, obs: object) -> None:
        """
        Override this method to update the GymWorld class
        :param obs: The observation from the Gym environment
        :return: None
        """
        raise NotImplementedError("Override this method to update the GymWorld class")
