from collections import defaultdict
from typing import Any, DefaultDict, Iterable, Optional, Set

from node import *
from node_numbering import *
from match import *
from pattern import *


@dataclass(frozen=True)
class Rule():
    lhs: Pattern
    rhs: Pattern


def _get_unique_nodes_in_tree(root: Node) -> Set[Node]:
    unique_nodes = set()
    def add_and_recur(node: Node):
        unique_nodes.add(node)
        for input_node in node.inputs():
            if input_node not in unique_nodes:
                add_and_recur(input_node)
    add_and_recur(root)
    return unique_nodes


class EGraph():
    # TODO speed things up (e.g., via union-find)
    _rules: Tuple[Rule]
    _nodes: Set[Node]
    _vn_to_nodes: DefaultDict[int, Set[Node]]
    _node_numberer: NodeNumberer

    def __init__(self, rules: Iterable[Rule], root: Node):
        self._rules = tuple(rules)
        self._node_numberer = NodeNumberer()
        self._nodes = set()
        self._vn_to_nodes = defaultdict(set)
        unique_nodes = _get_unique_nodes_in_tree(root)
        for node in unique_nodes:
            self._add_single_node(node)
        # TODO multiple iterations of interleaved rule application
        for rule in rules:
            # TODO bi-directional rewrite
            matcher = Matcher(rule.lhs)
            rewrite_results = []
            for node in self._nodes:
                opt_node = self._rewrite(matcher, rule.rhs, node)
                if opt_node is not None:
                    res = (node, opt_node)
                    rewrite_results.append(res)
            for old_node, new_node in rewrite_results:
                self._add_single_node(new_node)
                self._merge_nodes(old_node, new_node)

    def get_equivalent_nodes(self, node: Node) -> Iterable[Node]:
        vn = self._node_numberer.get_number(node)
        return self._vn_to_nodes[vn]

    def _add_single_node(self, node: Node):
        vn = self._node_numberer.get_number(node)
        if vn not in self._vn_to_nodes:
            self._vn_to_nodes[vn].add(node)
            self._nodes.add(node)

    def _merge_nodes(self, old_node: Node, new_node: Node):
        old_vn = self._node_numberer.get_number(old_node)
        new_vn = self._node_numberer.get_number(new_node)
        if old_vn != new_vn:
            self._vn_to_nodes[new_vn].update(self._vn_to_nodes[old_vn])
            self._vn_to_nodes[old_vn] = self._vn_to_nodes[new_vn]

    def _rewrite(self, matcher: Matcher, new_pattern: Pattern, old_node: Node) -> Optional[Tuple[Node, Node]]:
        opt_res = matcher.match(old_node)
        if opt_res is not None:
            return self._generate_node(opt_res, new_pattern)
        return None

    def _generate_node(self, res: MatchResult, new_pattern: Pattern) -> Node:
        # TODO visitor?
        def gen(pattern: Pattern) -> Node:
            if isinstance(pattern, ConstantPattern):
                return ConstantNode(pattern.value())
            elif isinstance(pattern, VariablePattern):
                pat_name = pattern.name()
                if pat_name in res.pat_varname_to_node:
                    return res.pat_varname_to_node[pat_name]
                return VariableNode(pat_name)
            elif isinstance(pattern, BinaryPattern):
                lhs = gen(pattern.lhs())
                rhs = gen(pattern.rhs())
                return BinaryNode(lhs, rhs, pattern.op())
            raise RuntimeError("Invalid pattern type: ", str(type(pattern)))
        return gen(new_pattern)


if __name__ == '__main__':
    # TODO make constant pattern capable of binding to values
    def get_mul_div_2_cancel_rule() -> Rule:
        x = VariablePattern("x")
        lhs = x * 2 / 2
        rhs = x
        return Rule(lhs, rhs)

    def get_mul_to_shift_rule() -> Rule:
        x = VariablePattern("x")
        lhs = x * 2
        rhs = x << 1
        return Rule(lhs, rhs)

    rules = [
        get_mul_to_shift_rule(),
        get_mul_div_2_cancel_rule(),
    ]

    x = VariableNode("x")
    expr = x * 2 / 2
    egraph = EGraph(rules, expr)
    print("\n-------nodes in egraph-------")
    for node in egraph._nodes:
        print(node)
    print("\n-------nodes equivalent to expr-------")
    for node in egraph.get_equivalent_nodes(expr):
        print(node)
