from __future__ import annotations

import abc
from dataclasses import dataclass
from enum import Enum, auto
from typing import Tuple


@dataclass(eq=False)
class Node(abc.ABC):
    _inputs: Tuple[Node]

    def __init__(self, inputs):
        self._inputs = inputs

    def inputs(self) -> Tuple[Node]:
        return self._inputs

    # NOTE the overloaded operators uses functions declared later because we
    # must reference subclass nodes like `BinaryNode`
    def __add__(self, other: Node) -> Node:
        return _add_maker(self, _node_converter(other))

    def __sub__(self, other: Node) -> Node:
        return _sub_maker(self, _node_converter(other))

    def __mul__(self, other: Node) -> Node:
        return _mul_maker(self, _node_converter(other))

    def __truediv__(self, other: Node) -> Node:
        return _div_maker(self, _node_converter(other))

    def __rshift__(self, other: Node) -> Node:
        return _rshift_maker(self, _node_converter(other))

    def __lshift__(self, other: Node) -> Node:
        return _lshift_maker(self, _node_converter(other))


@dataclass(eq=False)
class ConstantNode(Node):
    _value: int

    def __init__(self, value):
        inputs = ()
        super().__init__(inputs)
        self._value = value

    def value(self) -> int:
        return self._value


@dataclass(eq=False)
class VariableNode(Node):
    _name: str

    def __init__(self, name):
        inputs = ()
        super().__init__(inputs)
        self._name = name

    def name(self) -> str:
        return self._name


class BinaryOp(Enum):
    ADD = auto()
    SUB = auto()
    MUL = auto()
    DIV = auto()
    RSHIFT = auto()
    LSHIFT = auto()


@dataclass(eq=False)
class BinaryNode(Node):
    _op: BinaryOp

    def __init__(self, lhs: Node, rhs: Node, op: BinaryOp):
        inputs = (lhs, rhs)
        super().__init__(inputs)
        self._op = op

    def op(self) -> BinaryOp:
        return self._op

    def lhs(self) -> Node:
        return self._inputs[0]

    def rhs(self) -> Node:
        return self._inputs[1]


def _add_maker(lhs: Node, rhs: Node) -> BinaryNode:
    return BinaryNode(lhs, rhs, BinaryOp.ADD)


def _sub_maker(lhs: Node, rhs: Node) -> BinaryNode:
    return BinaryNode(lhs, rhs, BinaryOp.SUB)


def _mul_maker(lhs: Node, rhs: Node) -> BinaryNode:
    return BinaryNode(lhs, rhs, BinaryOp.MUL)


def _div_maker(lhs: Node, rhs: Node) -> BinaryNode:
    return BinaryNode(lhs, rhs, BinaryOp.DIV)


def _rshift_maker(lhs: Node, rhs: Node) -> BinaryNode:
    return BinaryNode(lhs, rhs, BinaryOp.RSHIFT)


def _lshift_maker(lhs: Node, rhs: Node) -> BinaryNode:
    return BinaryNode(lhs, rhs, BinaryOp.LSHIFT)


def _node_converter(value: any) -> Node:
    if isinstance(value, Node):
        return value
    if isinstance(value, int):
        return ConstantNode(int(value))
    raise RuntimeError("Can't convert to node: " + str(type(value)))


if __name__ == '__main__':
    x = VariableNode("x")
    num42 = ConstantNode(42)
    print(x)
    print(num42)
    print(x << 42)
