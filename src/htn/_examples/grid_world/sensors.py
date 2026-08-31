from __future__ import annotations

from htn._examples.grid_world.actions import GridWorld
from htn.sensors import Sensor
from htn.world.state import WorldState


class GridWorldSensor(Sensor[GridWorld]):
    """
    Sensor that maps the concrete GridWorld environment into symbolic HTN facts.
    """

    def sense(self, world: GridWorld, world_state: WorldState) -> None:
        """
        Read GridWorldEnv and update the HTN WorldState.

        Args:
            world: GridWorld runtime adapter.
            world_state: Symbolic world state to update.
        Returns:
            None.
        """
        env = world.env

        agent_x, agent_y = env.agent_position
        key_x, key_y = env.key_position
        door_x, door_y = env.door_position
        goal_x, goal_y = env.goal_position

        world_state.set_state("agent_x", agent_x)
        world_state.set_state("agent_y", agent_y)

        world_state.set_state("key_x", key_x)
        world_state.set_state("key_y", key_y)

        world_state.set_state("door_x", door_x)
        world_state.set_state("door_y", door_y)

        world_state.set_state("goal_x", goal_x)
        world_state.set_state("goal_y", goal_y)

        world_state.set_state("has_key", env.has_key)
        world_state.set_state("door_open", env.door_open)
        world_state.set_state("done", env.done)

        world_state.set_state("at_key", env.agent_position == env.key_position)
        world_state.set_state("at_door", env.agent_position == env.door_position)
        world_state.set_state(
            "at_goal",
            env.agent_position == env.goal_position and env.door_open,
        )
