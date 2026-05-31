class WorldState:
    """
    Represents the current state of the world in the HTN planning framework.
    """

    state_space: dict[str, bool]

    def __init__(self):
        """
        Initialize a new instance of WorldState.
        """
        self.state_space = {}

    def get_state(self, key: str) -> bool:
        """
        Retrieve the state value for the given key.

        :param key: The key to retrieve the state value for
        :return: The state value for the given key
        """
        return self.state_space.get(key, False)

    def set_state(self, key: str, value: bool) -> None:
        """
        Set the state value for the given key.

        :param key: The key to set the state value for
        :param value: The state value to set
        """
        self.state_space[key] = value
