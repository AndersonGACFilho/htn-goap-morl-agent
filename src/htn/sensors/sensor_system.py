from __future__ import annotations

from typing import Callable, Generic, TypeVar

from htn.delegates import MulticastDelegate
from htn.sensors.sensor import Sensor
from htn.world.state import WorldState

WorldT = TypeVar("WorldT")


class SensorSystem(Generic[WorldT]):
    """
    Coordinates sensors and notifies listeners when the symbolic world state
    has been refreshed.

    This is the owner of the world-state-change delegate.
    """

    sensors: list[Sensor[WorldT]]
    on_world_state_changed: MulticastDelegate[Callable[[WorldState], None]]

    def __init__(self) -> None:
        """Initialize the sensor system."""
        self.sensors = []
        self.on_world_state_changed = MulticastDelegate()

    def add_sensor(self, sensor: Sensor[WorldT]) -> None:
        """
        Register a sensor.

        Args:
            sensor: Sensor to register.
        Returns:
            None.
        """
        self.sensors.append(sensor)

    def update(self, world: WorldT, world_state: WorldState) -> None:
        """
        Run all sensors and notify listeners after the symbolic state is updated.

        Args:
            world: Runtime world/environment adapter.
            world_state: Symbolic HTN world state.
        Returns:
            None.
        """
        for sensor in self.sensors:
            sensor.sense(world, world_state)

        self.on_world_state_changed.invoke_handlers(world_state)
