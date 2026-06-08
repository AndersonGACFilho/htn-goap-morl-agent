from __future__ import annotations

from htn._examples.grid_world.actions import GridWorld
from htn._examples.grid_world.domain import build_grid_world_domain
from htn._examples.grid_world.env import GridWorldConfig, GridWorldEnv
from htn._examples.grid_world.renderer import RichGridWorldRenderer
from htn._examples.grid_world.sensors import GridWorldSensor
from htn.actions.action_status import ActionStatus
from htn.agent.agent import Agent
from htn.planner.planner import Planner
from htn.sensors import SensorSystem
from htn.world.state import WorldState

renderer = RichGridWorldRenderer()


def run() -> None:
    """
    Run the GridWorld HTN example.

    This function acts as the composition root for the example:
    it creates the environment, planner, agent, sensors, and renderer,
    then executes the simulation loop.

    :return: None
    """
    config = GridWorldConfig(
        width=8,
        height=6,
        start_position=None,
        key_position=None,
        door_position=None,
        goal_position=None,
        fixed_obstacles=frozenset(
            {
                (2, 2),
                (3, 2),
            }
        ),
        random_obstacle_count=5,
        initial_has_key=False,
        initial_door_open=True,
    )

    env = GridWorldEnv(config)

    env.reset(seed=42)

    world_state = WorldState()

    domain = build_grid_world_domain(env)
    planner = Planner(domain, world_state)
    agent = Agent(planner, world_state)
    world = GridWorld(env, world_state, agent)

    sensor_system: SensorSystem[GridWorld] = SensorSystem()
    sensor_system.add_sensor(GridWorldSensor())
    sensor_system.on_world_state_changed.add_handler(agent.handle_world_state_change)

    sensor_system.update(world, world_state)

    renderer.print_message("Initial world:", style="bold cyan")
    renderer.render(env)

    max_ticks = 100
    tick = 0

    while not world.done and tick < max_ticks:
        tick += 1

        result = agent.tick(world)

        if result.replanned:
            if result.planned_tasks:
                renderer.print_plan(result.planned_tasks)
            else:
                renderer.print_message("HTN: No valid plan.", style="bold red")
                break

        if result.task_name:
            renderer.print_step(tick, result.task_name)

        sensor_system.update(world, world_state)

        renderer.render(
            env,
            current_task=result.task_name,
            current_plan=agent.get_plan_names(),
        )

        if result.status == ActionStatus.SUCCESS:
            renderer.print_message(
                f"Task succeeded: {result.task_name}",
                style="bold green",
            )

        elif result.status == ActionStatus.RUNNING:
            renderer.print_message(f"Task running: {result.task_name}")

        elif result.status == ActionStatus.FAILURE:
            renderer.print_message(
                f"Task failed: {result.task_name}",
                style="bold red",
            )

        elif result.message:
            renderer.print_message(result.message, style="yellow")

    if world.done:
        renderer.print_message(
            f"Episode succeeded in {tick} ticks!", style="bold green"
        )
    else:
        renderer.print_message("Episode failed!", style="bold red")


if __name__ == "__main__":
    run()
