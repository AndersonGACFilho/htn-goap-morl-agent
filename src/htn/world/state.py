from htn.utils import WorldValue


class WorldState:
    """
    Represents the current state of the world in the HTN planning framework.
    """

    state_space: dict[str, WorldValue]

    def __init__(self):
        """
        Initialize a new instance of WorldState.
        """
        self.state_space = {}

    def get_state(self, key: str) -> WorldValue | None:
        """
        Retrieve the state value for the given key.

        Args:
            key: The key to retrieve the state value for
        Returns:
            The state value for the given key
        """
        return self.state_space.get(key)

    def set_state(self, key: str, value: WorldValue) -> None:
        """
        Set the state value for the given key.

        Args:
            key: The key to set the state value for
            value: The state value to set
        """
        self.state_space[key] = value

    def copy(self) -> "WorldState":
        """
        Create a copy of the current WorldState object.

        Returns:
            A new WorldState object with the same state space
        """
        new_state = WorldState()
        new_state.state_space = self.state_space.copy()
        return new_state

    def __str__(self):
        """
        String representation of the WorldState object.
        Returns:
            The string representation of the WorldState object.
        """
        return (
            f"WorldState(\n"
            f"{',\n    '.join(f'{key}: {value}' for key, value in self.state_space.items())}\n"
            f")"
        )

    def __repr__(self):
        """
        Representation of the WorldState object for debugging.
        Returns:
            The string representation of the WorldState object.
        """
        return f"WorldState({self.state_space!r})"
