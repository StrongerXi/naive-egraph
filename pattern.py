from __future__ import annotations

import abc
from dataclasses import dataclass
from enum import Enum, auto
from typing import Tuple

from node import *


@dataclass()
class Pattern(abc.ABC):
    _inputs: Tuple[Pattern]

    def __init__(self, inputs):
        self._inputs = inputs

    def inputs(self) -> Tuple[Pattern]:
        return self._inputs

    # NOTE the overloaded operators uses functions declared later because we
    # must reference subclass nodes like `BinaryPattern`
    def __add__(self, other: Pattern) -> Pattern:
        return _add_maker(self, _node_converter(other))

    def __sub__(self, other: Pattern) -> Pattern:
        return _sub_maker(self, _node_converter(other))

    def __mul__(self, other: Pattern) -> Pattern:
        return _mul_maker(self, _node_converter(other))

    def __truediv__(self, other: Pattern) -> Pattern:
        return _div_maker(self, _node_converter(other))

    def __rshift__(self, other: Pattern) -> Pattern:
        return _rshift_maker(self, _node_converter(other))

    def __lshift__(self, other: Pattern) -> Pattern:
        return _lshift_maker(self, _node_converter(other))


@dataclass()
class ConstantPattern(Pattern):
    _value: int

    def __init__(self, value):
        inputs = ()
        super().__init__(inputs)
        self._value = value

    def value(self) -> int:
        return self._value


@dataclass()
class VariablePattern(Pattern):
    _name: str

    def __init__(self, name):
        inputs = ()
        super().__init__(inputs)
        self._name = name

    def name(self) -> str:
        return self._name


@dataclass()
class BinaryPattern(Pattern):
    _op: BinaryOp

    def __init__(self, lhs: Pattern, rhs: Pattern, op: BinaryOp):
        inputs = (lhs, rhs)
        super().__init__(inputs)
        self._op = op

    def op(self) -> BinaryOp:
        return self._op

    def lhs(self) -> Pattern:
        return self._inputs[0]

    def rhs(self) -> Pattern:
        return self._inputs[1]


def _add_maker(lhs: Pattern, rhs: Pattern) -> BinaryPattern:
    return BinaryPattern(lhs, rhs, BinaryOp.ADD)


def _sub_maker(lhs: Pattern, rhs: Pattern) -> BinaryPattern:
    return BinaryPattern(lhs, rhs, BinaryOp.SUB)


def _mul_maker(lhs: Pattern, rhs: Pattern) -> BinaryPattern:
    return BinaryPattern(lhs, rhs, BinaryOp.MUL)


def _div_maker(lhs: Pattern, rhs: Pattern) -> BinaryPattern:
    return BinaryPattern(lhs, rhs, BinaryOp.DIV)


def _rshift_maker(lhs: Pattern, rhs: Pattern) -> BinaryPattern:
    return BinaryPattern(lhs, rhs, BinaryOp.RSHIFT)


def _lshift_maker(lhs: Pattern, rhs: Pattern) -> BinaryPattern:
    return BinaryPattern(lhs, rhs, BinaryOp.LSHIFT)


def _node_converter(value: any) -> Pattern:
    if isinstance(value, Pattern):
        return value
    if isinstance(value, int):
        return ConstantPattern(int(value))
    raise RuntimeError("Can't convert to node: " + str(type(value)))


if __name__ == '__main__':
    x = VariablePattern("x")
    num42 = ConstantPattern(42)
    print(x)
    print(num42)
    print(x << 42)
