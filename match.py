from typing import Dict

from node import *
from pattern import *


class Matcher():
    _pattern: Pattern
    _pat_varname_to_node: Dict[str, VariableNode]

    def __init__(self, pattern):
        self._pattern = pattern
        self._pat_varname_to_node = {}

    def match(self, root: Node) -> bool:
        pat_to_node_varname_ = {}
        return self._match(self._pattern, root)

    def _match(self, pattern: Pattern, root: Node) -> bool:
        if not self._match_single(pattern, root):
            return False
        if len(pattern.inputs()) != len(root.inputs()):
            return False
        for pattern, node in zip(pattern.inputs(), root.inputs()):
            if not self._match(pattern, node):
                return False
        return True

    def _match_single(self, pattern: Pattern, node: Node) -> bool:
        if isinstance(pattern, ConstantPattern):
            return self._match_constant(pattern, node)
        elif isinstance(pattern, VariablePattern):
            return self._match_variable(pattern, node)
        elif isinstance(pattern, BinaryPattern):
            return self._match_binary(pattern, node)
        raise RuntimeError("Invalid pattern type: ", str(type(pattern)))

    def _match_constant(self, pattern: ConstantPattern, node: Node) -> bool:
        return isinstance(node, ConstantNode) and node.value() == pattern.value()

    def _match_variable(self, pattern: VariablePattern, node: Node) -> bool:
        if not isinstance(node, VariableNode):
            return False
        # bind upon first encounter
        pat_name = pattern.name()
        if pat_name not in self._pat_varname_to_node:
            self._pat_varname_to_node[pat_name] = node
        return self._pat_varname_to_node[pat_name] == node

    def _match_binary(self, pattern: BinaryPattern, node: Node) -> bool:
        return isinstance(node, BinaryNode) and node.op() == pattern.op()


if __name__ == '__main__':
    pat = VariablePattern("x") + VariablePattern("x") * ConstantPattern(42)
    matcher = Matcher(pat)

    x = VariableNode("x")
    print(matcher.match(x + x * 42))
    print(matcher.match(x + x * 41))
    print(matcher.match(x * 42 + x))
