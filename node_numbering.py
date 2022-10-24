from typing import Any, Dict

from node import *


class NodeNumberer():
    """
    Value Numbering applied to Node
    """
    _next_vn: int
    # TODO serves as a cache, make it a LRU cache to avoid memory explosion,
    # because we create lots of intermediate nodes, but cache is meant for nodes
    # reused in user's original input graph
    _node_to_vn: Dict[Node, int]
    # TODO a canonical form class so we can do `Dict[CanonicalForm, int]`
    _constant_to_vn: Dict[int, int]
    _varname_to_vn: Dict[str, int]
    _binop_to_vn: Dict[Tuple[int, int, BinaryOp], int]

    def __init__(self):
        self._next_vn = 0
        self._node_to_vn = {}
        self._constant_to_vn = {}
        self._varname_to_vn = {}
        self._binop_to_vn = {}

    def get_number(self, node: Node) -> int:
        if node not in self._node_to_vn:
            self._node_to_vn[node] = self._gen_node_vn(node)
        return self._node_to_vn[node]

    def _gen_node_vn(self, node: Node) -> int:
        if isinstance(node, ConstantNode):
            return self._get_or_gen_vn(self._constant_to_vn, node.value())
        elif isinstance(node, VariableNode):
            return self._get_or_gen_vn(self._varname_to_vn, node.name())
        elif isinstance(node, BinaryNode):
            lhs_vn = self.get_number(node.lhs())
            rhs_vn = self.get_number(node.rhs())
            binop_key = (lhs_vn, rhs_vn, node.op())
            return self._get_or_gen_vn(self._binop_to_vn, binop_key)
        raise RuntimeError("Invalid node type: ", str(type(node)))

    def _get_or_gen_vn(self, generic_dict: Dict[Any, int], key: Any) -> int:
        if key not in generic_dict:
            generic_dict[key] = self._next_vn
            self._next_vn += 1
        return generic_dict[key]

if __name__ == '__main__':
    numberer = NodeNumberer()

    x = VariableNode("x")
    expr = x * 2 / 2

    print(numberer.get_number(x))
    print(numberer.get_number(expr))
    print(numberer.get_number(x * 2 / 2))
