import decimal
from typing import Any, Optional

Decimal = decimal.Decimal
ZERO: Any
HALF: Any
ONE: Any

class MISSING: ...

NUMBER_RE: str

def D(strord: Optional[Any] = ...): ...
def round_to(number: Any, increment: Any): ...
def same_sign(number1: Any, number2: Any): ...
