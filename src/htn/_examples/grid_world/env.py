from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import gymnasium as gym
import numpy as np
from gymnasium import spaces

Position = tuple[int, int]


@dataclass(frozen=True, slots=True)
class GridWorldConfig:
    """
    Configuration object for the GridWorld environment.

    Use a fixed position when you want deterministic placement.
    Use None when you want the environment to randomly place that entity.

    Attributes:
        width: Grid width in tiles.
        height: Grid height in tiles.
        start_position: Initial agent position. If None, it is randomized.
        key_position: Key position. If None, it is randomized.
        door_position: Door position. If None, it is randomized.
        goal_position: Goal position. If None, it is randomized.
        fixed_obstacles: Obstacles that are always placed in the grid.
        random_obstacle_count: Number of additional random obstacles.
        initial_has_key: Whether the agent starts with the key.
        initial_door_open: Whether the door starts open.
    """

    width: int = 3
    height: int = 3

    start_position: Position | None = (0, 0)
    key_position: Position | None = (2, 0)
    door_position: Position | None = (2, 2)
    goal_position: Position | None = (0, 2)

    fixed_obstacles: frozenset[Position] = field(
        default_factory=lambda: frozenset({(1, 1)})
    )
    random_obstacle_count: int = 0

    initial_has_key: bool = False
    initial_door_open: bool = False


class GridWorldEnv(gym.Env):
    """
    Configurable deterministic GridWorld used as a simulation sandbox.

    The environment does not decide what to do.
    The HTN planner decides the symbolic intention.
    The action classes translate HTN tasks into environment steps.

    Actions:
        0 = up
        1 = right
        2 = down
        3 = left
        4 = pickup_key
        5 = open_door
    """

    metadata = {"render_modes": ["human"]}

    ACTION_UP = 0
    ACTION_RIGHT = 1
    ACTION_DOWN = 2
    ACTION_LEFT = 3
    ACTION_PICKUP_KEY = 4
    ACTION_OPEN_DOOR = 5

    def __init__(self, config: GridWorldConfig | None = None) -> None:
        """
        Initialize the GridWorld environment.

        Args:
            config: Optional GridWorld configuration. If omitted, the original 3x3 example layout is used.
        """
        super().__init__()

        self.config = config or GridWorldConfig()

        self.width = self.config.width
        self.height = self.config.height

        self.start_position: Position = (0, 0)
        self.key_position: Position = (0, 0)
        self.door_position: Position = (0, 0)
        self.goal_position: Position = (0, 0)

        self.obstacles: set[Position] = set()

        self.agent_position: Position = (0, 0)
        self.has_key = False
        self.door_open = False
        self.done = False

        self._validate_static_config()

        self.action_space = spaces.Discrete(6)

        self.observation_space = spaces.Dict(
            {
                "agent": self._position_space(),
                "key": self._position_space(),
                "door": self._position_space(),
                "goal": self._position_space(),
                "has_key": spaces.Discrete(2),
                "door_open": spaces.Discrete(2),
                "done": spaces.Discrete(2),
            }
        )

    def reset(
        self,
        *,
        seed: int | None = None,
        options: dict[str, Any] | None = None,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        """
        Reset the environment.

        Random positions are resolved here, not in __init__, so each reset can
        create a new layout. Passing a seed makes the layout reproducible.

        Args:
            seed: Optional random seed.
            options: Optional Gymnasium reset options.
        Returns:
            The initial observation and an empty info dictionary.
        """
        super().reset(seed=seed)

        self._resolve_layout()

        self.agent_position = self.start_position
        self.has_key = self.config.initial_has_key
        self.door_open = self.config.initial_door_open
        self.done = self.agent_position == self.goal_position and self.door_open

        return self._get_obs(), {}

    def step(
        self,
        action: int,
    ) -> tuple[dict[str, Any], float, bool, bool, dict[str, Any]]:
        """
        Execute one action in the environment.

        Args:
            action: Integer action id.
        Returns:
            Observation, reward, terminated flag, truncated flag and info.
        """
        if self.done:
            return self._get_obs(), 0.0, True, False, {}

        action = int(action)

        if action == self.ACTION_UP:
            self._try_move(0, -1)
        elif action == self.ACTION_RIGHT:
            self._try_move(1, 0)
        elif action == self.ACTION_DOWN:
            self._try_move(0, 1)
        elif action == self.ACTION_LEFT:
            self._try_move(-1, 0)
        elif action == self.ACTION_PICKUP_KEY:
            self._try_pickup_key()
        elif action == self.ACTION_OPEN_DOOR:
            self._try_open_door()
        else:
            raise ValueError(f"Invalid action: {action}")

        self.done = self.agent_position == self.goal_position and self.door_open

        reward = 1.0 if self.done else 0.0
        terminated = self.done
        truncated = False

        return self._get_obs(), reward, terminated, truncated, {}

    def _resolve_layout(self) -> None:
        """
        Resolve fixed and random entity positions for the current episode.

        Positions configured as None are sampled from valid free cells.
        Special entities cannot overlap obstacles or each other.
        """
        reserved: set[Position] = set()

        self.obstacles = set(self.config.fixed_obstacles)

        self.start_position = self._resolve_position(
            self.config.start_position,
            reserved,
            name="start_position",
        )
        reserved.add(self.start_position)

        self.key_position = self._resolve_position(
            self.config.key_position,
            reserved,
            name="key_position",
        )
        reserved.add(self.key_position)

        self.door_position = self._resolve_position(
            self.config.door_position,
            reserved,
            name="door_position",
        )
        reserved.add(self.door_position)

        self.goal_position = self._resolve_position(
            self.config.goal_position,
            reserved,
            name="goal_position",
        )
        reserved.add(self.goal_position)

        self._add_random_obstacles(reserved)

    def _resolve_position(
        self,
        configured_position: Position | None,
        reserved: set[Position],
        *,
        name: str,
    ) -> Position:
        """
        Resolve either a fixed or random position.

        Args:
            configured_position: Fixed position or None for random placement.
            reserved: Positions already occupied by other special entities.
            name: Human-readable position name for error messages.
        Returns:
            A valid position.
        Raises:
            ValueError: If the fixed position is invalid.
        """
        if configured_position is not None:
            if not self._is_inside_grid(configured_position):
                raise ValueError(f"{name} is outside the grid: {configured_position}")

            if configured_position in self.obstacles:
                raise ValueError(f"{name} overlaps an obstacle: {configured_position}")

            if configured_position in reserved:
                raise ValueError(
                    f"{name} overlaps another special position: {configured_position}"
                )

            return configured_position

        return self._sample_free_position(reserved)

    def _add_random_obstacles(self, reserved: set[Position]) -> None:
        """
        Add random obstacles without overlapping special entities.

        Args:
            reserved: Positions occupied by agent, key, door and goal.
        Raises:
            ValueError: If there are not enough free cells.
        """
        if self.config.random_obstacle_count < 0:
            raise ValueError("random_obstacle_count cannot be negative.")

        for _ in range(self.config.random_obstacle_count):
            obstacle = self._sample_free_position(reserved | self.obstacles)
            self.obstacles.add(obstacle)

    def _sample_free_position(self, blocked: set[Position]) -> Position:
        """
        Sample one free position from the grid.

        Args:
            blocked: Positions that cannot be selected.
        Returns:
            A randomly selected free position.
        Raises:
            ValueError: If no free position is available.
        """
        candidates = [
            position
            for position in self._all_positions()
            if position not in blocked and position not in self.obstacles
        ]

        if not candidates:
            raise ValueError("There are no free cells available for random placement.")

        index = int(self.np_random.integers(0, len(candidates)))
        return candidates[index]

    def _all_positions(self) -> list[Position]:
        """
        Return all positions inside the grid.

        Returns:
            A list of all valid grid coordinates.
        """
        return [(x, y) for y in range(self.height) for x in range(self.width)]

    def _try_move(self, dx: int, dy: int) -> None:
        """
        Try to move the agent by a delta.

        Movement is ignored if the target tile is outside the grid, blocked by
        an obstacle, or is the locked goal tile.

        Args:
            dx: Horizontal movement delta.
            dy: Vertical movement delta.
        Returns:
            None
        """
        x, y = self.agent_position
        next_position = (x + dx, y + dy)

        if not self._is_inside_grid(next_position):
            return

        if next_position in self.obstacles:
            return

        if next_position == self.goal_position and not self.door_open:
            return

        self.agent_position = next_position

    def _try_pickup_key(self) -> None:
        """
        Pick up the key if the agent is standing on the key tile.
        """
        if self.agent_position == self.key_position:
            self.has_key = True

    def _try_open_door(self) -> None:
        """
        Open the door if the agent is standing at the door and has the key.
        """
        if self.agent_position == self.door_position and self.has_key:
            self.door_open = True

    def _is_inside_grid(self, position: Position) -> bool:
        """
        Check whether a position is inside the configured grid.

        Args:
            position: Position to validate.
        Returns:
            True if the position is inside the grid.
        """
        x, y = position
        return 0 <= x < self.width and 0 <= y < self.height

    def _position_space(self) -> spaces.Box:
        """
        Build the observation space for grid positions.

        Returns:
            A Gymnasium Box with dynamic bounds based on grid size.
        """
        return spaces.Box(
            low=np.array([0, 0], dtype=np.int32),
            high=np.array([self.width - 1, self.height - 1], dtype=np.int32),
            shape=(2,),
            dtype=np.int32,
        )

    def _get_obs(self) -> dict[str, Any]:
        """
        Build the current observation.

        Returns:
            Dictionary containing concrete environment state.
        """
        return {
            "agent": np.array(self.agent_position, dtype=np.int32),
            "key": np.array(self.key_position, dtype=np.int32),
            "door": np.array(self.door_position, dtype=np.int32),
            "goal": np.array(self.goal_position, dtype=np.int32),
            "has_key": int(self.has_key),
            "door_open": int(self.door_open),
            "done": int(self.done),
        }

    def _validate_static_config(self) -> None:
        """
        Validate static configuration values.

        Raises:
            ValueError: If dimensions or fixed obstacles are invalid.
        """
        if self.width <= 0:
            raise ValueError("Grid width must be greater than zero.")

        if self.height <= 0:
            raise ValueError("Grid height must be greater than zero.")

        for obstacle in self.config.fixed_obstacles:
            if not self._is_inside_grid(obstacle):
                raise ValueError(f"Obstacle is outside the grid: {obstacle}")

    def render(self) -> None:
        """
        Print an ANSI representation of the current grid.
        """
        rows: list[str] = []

        for y in range(self.height):
            row: list[str] = []

            for x in range(self.width):
                position = (x, y)

                if position == self.agent_position:
                    row.append("A")
                elif position in self.obstacles:
                    row.append("X")
                elif position == self.key_position and not self.has_key:
                    row.append("K")
                elif position == self.door_position:
                    row.append("O" if self.door_open else "D")
                elif position == self.goal_position:
                    row.append("G")
                else:
                    row.append(".")

            rows.append(" ".join(row))

        print("\n".join(rows))
        print(
            f"agent={self.agent_position}, "
            f"has_key={self.has_key}, "
            f"door_open={self.door_open}, "
            f"done={self.done}"
        )
        print()
