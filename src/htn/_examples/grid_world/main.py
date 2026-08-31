from __future__ import annotations

from htn._examples.grid_world.actions import GridWorld
from htn._examples.grid_world.domain import build_grid_world_domain
from htn._examples.grid_world.env import GridWorldConfig, GridWorldEnv
from htn._examples.grid_world.gif_generator import create_gif
from htn._examples.grid_world.renderer import RichGridWorldRenderer
from htn._examples.grid_world.sensors import GridWorldSensor
from htn.actions.action_status import ActionStatus
from htn.agent.agent import Agent
from htn.planner.planner import Planner
from htn.sensors import SensorSystem
from htn.strategy.depth_first_search_strategy import DepthFirstSearchStrategy
from htn.world.state import WorldState


def run() -> None:
    """
    Run the GridWorld HTN example.

    This function acts as the composition root for the example:
    it creates the environment, planner, agent, sensors, and renderer,
    then executes the simulation loop.

    :return: None
    """
    config = GridWorldConfig(
        width=10,
        height=10,
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
        random_obstacle_count=10,
        initial_has_key=False,
        initial_door_open=False,
    )

    env = GridWorldEnv(config)

    env.reset(seed=42)

    world_state = WorldState()
    strategy = DepthFirstSearchStrategy()

    domain = build_grid_world_domain(env)
    planning_tasks = domain.tasks.copy()

    planner = Planner(domain, world_state, strategy)
    agent = Agent(planner, world_state, planning_tasks)
    world = GridWorld(env, world_state, agent)

    sensor_system: SensorSystem[GridWorld] = SensorSystem()
    sensor_system.add_sensor(GridWorldSensor())
    sensor_system.on_world_state_changed.add_handler(agent.handle_world_state_change)

    sensor_system.update(world, world_state)

    image_paths = []

    renderer = RichGridWorldRenderer(env)

    renderer.render(
        env,
        banner="Initial state:",
    )
    image_paths.append(renderer.export())

    max_ticks = 100
    tick = 0

    while not world.done and tick < max_ticks:
        tick += 1

        result = agent.tick(world)

        plan_announcement = None
        if result.replanned:
            if result.planned_tasks:
                plan_announcement = result.planned_tasks
            else:
                renderer.print_message("HTN: No valid plan.", style="bold red")
                break

        sensor_system.update(world, world_state)

        result_message = None
        result_style = "bold black"

        if result.status == ActionStatus.SUCCESS:
            result_message = f"Task succeeded: {result.task_name}"
            result_style = "bold green"
        elif result.status == ActionStatus.RUNNING:
            result_message = f"Task running: {result.task_name}"
            result_style = "bold black"
        elif result.status == ActionStatus.FAILURE:
            result_message = f"Task failed: {result.task_name}"
            result_style = "bold red"
        elif result.message:
            result_message = result.message
            result_style = "bold black"
        renderer.render(
            env,
            current_task=result.task_name,
            current_plan=agent.get_plan_names(),
            plan_announcement=plan_announcement,
            result_message=result_message,
            result_style=result_style,
        )

        image_paths.append(renderer.export())

    if world.done:
        renderer.print_message(
            f"Episode succeeded in {tick} ticks!", style="bold green"
        )
    else:
        renderer.print_message("Episode failed!", style="bold red")

    create_gif(image_paths, "gif", env, renderer)


if __name__ == "__main__":
    run()
