from typing import Literal, TypeAlias

from htn.utils import WorldValue, check_condition
from htn.world.state import WorldState

ConditionOperator: TypeAlias = Literal["=", "!=", ">", "<", ">=", "<="]
Preconditions: TypeAlias = dict[str, tuple[ConditionOperator, WorldValue]]


def are_preconditions_satisfied(
    preconditions: Preconditions,
    world_state: WorldState,
) -> bool:
    """
    Checks whether all preconditions are satisfied by the given world state.

    :param preconditions: The preconditions to check
    :param world_state: The current world state
    :return: True if all preconditions are satisfied, False otherwise
    """
    for key, condition in preconditions.items():
        if key not in world_state.state_space:
            return False

        operator, expected_value = condition
        current_value = world_state.state_space[key]

        if not check_condition(current_value, operator, expected_value):
            return False

    return True
