from __future__ import annotations

import abc
from dataclasses import dataclass
from enum import Enum, auto
from typing import Tuple


@dataclass(eq=False)
class Node(abc.ABC):
    inputs_: Tuple[Node]

    def __init__(self, inputs):
        self.inputs_ = inputs

    def inputs(self) -> Tuple[Node]:
        return self.inputs_

    # NOTE the overloaded operators uses functions declared later because we
    # must reference subclass nodes like `BinaryNode`
    def __add__(self, other: Node) -> Node:
        return _add_maker(self, _node_converter(other))

    def __sub__(self, other: Node) -> Node:
        return _sub_maker(self, _node_converter(other))

    def __mul__(self, other: Node) -> Node:
        return _mul_maker(self, _node_converter(other))

    def __div__(self, other: Node) -> Node:
        return _div_maker(self, _node_converter(other))

    def __rshift__(self, other: Node) -> Node:
        return _rshift_maker(self, _node_converter(other))

    def __lshift__(self, other: Node) -> Node:
        return _lshift_maker(self, _node_converter(other))


@dataclass(eq=False)
class ConstantNode(Node):
    value_: int

    def __init__(self, value):
        inputs = ()
        super().__init__(inputs)
        self.value_ = value


@dataclass(eq=False)
class VariableNode(Node):
    name_: str

    def __init__(self, name):
        inputs = ()
        super().__init__(inputs)
        self.name_ = name


class BinaryOp(Enum):
    ADD = auto()
    SUB = auto()
    MUL = auto()
    DIV = auto()
    RSHIFT = auto()
    LSHIFT = auto()


@dataclass(eq=False)
class BinaryNode(Node):
    op_: BinaryOp

    def __init__(self, lhs: Node, rhs: Node, op: BinaryOp):
        inputs = (lhs, rhs)
        super().__init__(inputs)
        self.op_ = op

    def lhs(self) -> Node:
        return self.inputs_[0]

    def rhs(self) -> Node:
        return self.inputs_[1]


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
    num42 = ConstantNode()
    print(x)
    print(num42)
    print(x << 42)
