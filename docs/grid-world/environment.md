# Environment and configuration

## `GridWorldConfig`

`GridWorldConfig` is an immutable dataclass (`frozen=True`, `slots=True`) that supports deterministic and random scenarios.

| Group         | Parameters                                                         |
|---------------|--------------------------------------------------------------------|
| Dimensions    | `width`, `height`                                                  |
| Entities      | `start_position`, `key_position`, `door_position`, `goal_position` |
| Obstacles     | `fixed_obstacles`, `random_obstacle_count`                         |
| Initial state | `initial_has_key`, `initial_door_open`                             |

A `None` position is resolved randomly in `reset()`. Fixed positions are appropriate for tests and reproducible demonstrations; use a seed in `reset(seed=...)` when the configuration includes randomness.

```python
config = GridWorldConfig(
    width=8,
    height=6,
    start_position=None,
    key_position=None,
    door_position=None,
    goal_position=None,
    fixed_obstacles=frozenset({(2, 2), (3, 2)}),
    random_obstacle_count=5,
    initial_has_key=False,
    initial_door_open=False,
)
env = GridWorldEnv(config)
obs, info = env.reset(seed=42)
```

## Gymnasium interface

`GridWorldEnv` is a `gym.Env`. Its `action_space` is discrete and its `observation_space` is a `spaces.Dict` that represents the environment state.

|  Id | Constant            | Operation                        |
|----:|---------------------|----------------------------------|
|   0 | `ACTION_UP`         | moves up                         |
|   1 | `ACTION_RIGHT`      | moves right                      |
|   2 | `ACTION_DOWN`       | moves down                       |
|   3 | `ACTION_LEFT`       | moves left                       |
|   4 | `ACTION_PICKUP_KEY` | picks up the key when applicable |
|   5 | `ACTION_OPEN_DOOR`  | opens the door when applicable   |

`reset()` resolves the layout, restores `has_key` and `door_open` according to the configuration, and returns `(observation, {})`. `step(action)` returns the five-item Gymnasium contract: observation, reward, `terminated`, `truncated`, and `info`.

!!! tip "Termination"
    The example uses `env.done` to control the loop. The goal is completing navigation to the objective, reflected first by the concrete state and then by the sensor.

## Layout validation

The environment places entities and obstacles without allowing invalid collisions. Obstacles are consulted both by the environment when processing movement and by the pathfinder when finding routes. A random configuration is reliable only if enough space is available for the selected entities and barriers.

## Observation versus HTN facts

The observation object is the environment interface; it does not populate `WorldState` directly. `GridWorldSensor` performs this translation and exposes the facts required by the domain. This separation lets the observation shape change without rewriting the planner, provided the sensor preserves the symbolic contract.
