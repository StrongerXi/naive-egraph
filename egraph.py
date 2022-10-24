import itertools
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


def _copy_node_with_new_inputs(old_node: Node, new_inputs: Iterable[Node]) -> Node:
    if isinstance(old_node, ConstantNode):
        assert(len(new_inputs) == 0)
        return old_node
    elif isinstance(old_node, VariableNode):
        assert(len(new_inputs) == 0)
        return old_node
    elif isinstance(old_node, BinaryNode):
        assert(len(new_inputs) == 2)
        new_lhs, new_rhs = new_inputs
        return BinaryNode(new_lhs, new_rhs, old_node.op())
    raise RuntimeError("Invalid node type: ", str(type(old_node)))


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
    # TODO speed things up (this is tricky, need to think more, I actually don't
    # see how union find will help us...)
    _rules: Tuple[Rule]
    _vn_to_enodes: DefaultDict[int, Set[Node]]
    _node_numberer: NodeNumberer

    def __init__(self, rules: Iterable[Rule], root: Node):
        self._rules = tuple(rules)
        self._node_numberer = NodeNumberer()
        self._vn_to_enodes = defaultdict(set)
        for node in _get_unique_nodes_in_tree(root):
            self._add_single_node(node)
        # TODO multiple iterations
        self._apply_rules_to_tree(rules, root)

    def get_equivalent_nodes(self, node: Node) -> Iterable[Node]:
        vn = self._node_numberer.get_number(node)
        return self._vn_to_enodes[vn]

    def get_all_nodes(self) -> Set[Node]:
        all_nodes = set()
        for _, enodes in self._vn_to_enodes.items():
            all_nodes.update(enodes)
        return all_nodes

    def _apply_rules_to_tree(self, rules: Iterable[Rule], root: Node):
        # TODO bi-directional rewrite?
        matchers_and_rules = [(Matcher(rule.lhs), rule) for rule in rules]
        applied_nodes_vns = set()
        def apply_and_recur(node: Node):
            vn = self._node_numberer.get_number(node)
            if vn in applied_nodes_vns:
                return
            applied_nodes_vns.add(vn)
            unique_equivalent_inputs : List[Set[Node]] = []
            # TODO god this is slow, I feel like we can simply doing this
            # eagerly (with this post-order traversal), whereas the paper can
            # rewrite any node and must recursively update its parents. Need to
            # think more.
            for input_node in node.inputs():
                # TODO what if we found input_node to be equivalent to some
                # nested input of this node? Then the users of that nested input
                # node might need update. I think this is why the paper uses a
                # worklist algorithm (we need to find a fixpoint)
                apply_and_recur(input_node)
                unique_equivalent_inputs.append(self.get_equivalent_nodes(input_node))
            for inputs_combo in itertools.product(*unique_equivalent_inputs):
                new_node = _copy_node_with_new_inputs(node, inputs_combo)
                # congruence -- x ~ y --> f(x) ~ f(y)
                self._merge_nodes(node, new_node)
            # TODO this is also slow, we really only want to traverse the newly
            # added enodes
            for enode in self.get_equivalent_nodes(node):
                for matcher, rule in matchers_and_rules:
                    opt_new_node = self._rewrite(matcher, rule.rhs, enode)
                    if opt_new_node is not None:
                        # TODO recur on new node? (tricky, may cause infinite loop)
                        self._add_single_node(opt_new_node)
                        self._merge_nodes(enode, opt_new_node)
        apply_and_recur(root)

    def _add_single_node(self, node: Node) -> bool:
        # NOTE speed up, only keep track of structurally different node
        vn = self._node_numberer.get_number(node)
        if vn not in self._vn_to_enodes:
            self._vn_to_enodes[vn].add(node)
            return True
        return False

    def _merge_nodes(self, old_node: Node, new_node: Node):
        old_vn = self._node_numberer.get_number(old_node)
        new_vn = self._node_numberer.get_number(new_node)
        from_enodes = self._vn_to_enodes[old_vn]
        to_enodes = self._vn_to_enodes[new_vn]
        if from_enodes is to_enodes: # already equivalent classes
            return
        if len(from_enodes) > len(to_enodes):
            from_enodes, to_enodes = to_enodes, from_enodes
        to_enodes.update(from_enodes)
        for node in from_enodes:
            vn = self._node_numberer.get_number(node)
            self._vn_to_enodes[vn] = to_enodes

    def _rewrite(self, matcher: Matcher, new_pattern: Pattern, old_node: Node) -> Optional[Node]:
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
    expr = x * 2 / 2 * 2 / 2
    egraph = EGraph(rules, expr)

    print("\n-------all nodes in egraph-------")
    for node in egraph.get_all_nodes():
        print(node)

    print("\n-------nodes equivalent to expr-------")
    for node in egraph.get_equivalent_nodes(expr):
        print(node)
