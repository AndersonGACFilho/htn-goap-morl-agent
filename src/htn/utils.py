from typing import TypeAlias, TypeGuard

WorldValue: TypeAlias = bool | int | float | str


def is_number(value: WorldValue) -> TypeGuard[int | float]:
    return type(value) in (int, float)


def check_condition(
    current_value: WorldValue, operator: str, expected_value: WorldValue
) -> bool:
    """
    Checks if the current value satisfies the given condition.
    :param current_value: The current value to check
    :param operator: The operator to use for the comparison
    :param expected_value: The expected value for the comparison
    :return: True if the condition is satisfied, False otherwise
    """
    if current_value is None or expected_value is None:
        raise ValueError("Cannot compare None values")

    if operator == "=":
        return current_value == expected_value

    if operator == "!=":
        return current_value != expected_value

    if operator in {">", "<", ">=", "<="}:
        if not is_number(current_value) or not is_number(expected_value):
            raise ValueError(
                f"Operator '{operator}' requires numeric values. "
                f"Got {type(current_value).__name__} and {type(expected_value).__name__}."
            )

        if operator == ">":
            return current_value > expected_value
        if operator == "<":
            return current_value < expected_value
        if operator == ">=":
            return current_value >= expected_value
        if operator == "<=":
            return current_value <= expected_value

    raise ValueError(f"Invalid condition operator: {operator}")


def apply_effect(
    current_value: WorldValue | None, operator: str, value: WorldValue
) -> WorldValue:
    """
    Applies the given effect to the current value based on the operator.
    :param current_value: The current value to apply the effect to
    :param operator: The operator to use for the effect
    :param value: The value to apply the effect with
    :return: The updated current value after applying the effect
    """
    if operator == "=":
        return value

    if current_value is None:
        raise ValueError(
            f"Cannot apply operator '{operator}' to a missing world state value."
        )

    if operator == "not":
        if not isinstance(current_value, bool):
            raise ValueError(
                f"Operator 'not' requires a bool value. "
                f"Got {type(current_value).__name__}."
            )
        return not current_value

    if operator in {"+", "-", "*", "/", "%", "**", "//"}:
        if not is_number(current_value) or not is_number(value):
            raise ValueError(
                f"Operator '{operator}' requires numeric values. "
                f"Got {type(current_value).__name__} and {type(value).__name__}."
            )

        if operator == "+":
            return current_value + value

        if operator == "-":
            return current_value - value

        if operator == "*":
            return current_value * value

        if operator == "/":
            if value == 0:
                raise ValueError("Cannot divide by zero")
            return current_value / value

        if operator == "%":
            if value == 0:
                raise ValueError("Cannot modulo by zero")
            return current_value % value

        if operator == "**":
            return current_value**value

        if operator == "//":
            if value == 0:
                raise ValueError("Cannot floor-divide by zero")
            return current_value // value

    raise ValueError(f"Invalid effect operator: {operator}")
