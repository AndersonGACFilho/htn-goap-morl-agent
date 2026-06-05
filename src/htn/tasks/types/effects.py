from typing import Literal, TypeAlias

from htn.utils import WorldValue

EffectOperator: TypeAlias = Literal["=", "+", "-", "*", "/", "%", "**", "//", "not"]
Effects: TypeAlias = dict[str, tuple[EffectOperator, WorldValue]]
