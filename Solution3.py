from collections import defaultdict
from itertools import chain, product

from Solution1 import Solution1_1
from transformation.cnf_transformer2 import NonTerminal, CnfTransformer
from util.tree.node import Node


class Solution3(Solution1_1):

    def __init__(self, save_parent=False, h_lookback=0):
        super().__init__()
        self._save_parent = save_parent
        self._h_lookback = h_lookback
        self._transformer = CnfTransformer(save_parent, h_lookback, True)

    def get_terminal_or_non_t(self, parent, node_idx):
        if not parent.children[node_idx].children:
            return parent.children[node_idx].tag
        return NonTerminal(parent.children[node_idx].tag, parent.tag if self._save_parent else None,
                           tuple(map(lambda n: n.tag, parent.children[:node_idx][-self._h_lookback or len(parent.children):])))

    def _count_occurrences_relatively(self, parent, node_idx, occurrences_dict):
        child = parent.children[node_idx]
        if not child.children:
            return
        occurrences_dict[self.get_terminal_or_non_t(parent, node_idx)][
            tuple(map(lambda i: self.get_terminal_or_non_t(child, i),
                      range(len(child.children))))] += 1
        for grand_child_idx in range(len(child.children)):
            self._count_occurrences_relatively(child, grand_child_idx, occurrences_dict)

    def _count_occurrences(self, root, occurrences_dict):
        root_non_t = NonTerminal(root.tag, None, tuple())
        occurrences_dict[root_non_t][tuple(map(lambda i: self.get_terminal_or_non_t(root, i),
                                               range(len(root.children))))] += 1
        for i in range(len(root.children)):
            self._count_occurrences_relatively(root, i, occurrences_dict)

    def parse(self, sentence):
        table = [[defaultdict(float) for _ in sentence] for _ in sentence]
        nodes_table = [[defaultdict(lambda:None) for _ in sentence] for _ in sentence]

        for j in range(0, len(sentence)):
            for (l_rule, prob) in self._reversed_dict[(sentence[j],)].items():
                table[j][j][l_rule] = prob
                nodes_table[j-1][j][sentence[j]] = Node(sentence[j])
            for i in reversed(range(j)):
                for k in range(i, j):
                    for pair in set(product(table[i][k], table[k+1][j])).intersection(self._reversed_dict.keys()):
                        for (l_rule, prob) in self._reversed_dict[pair].items():
                            new_prob = prob * table[i][k][pair[0]] * table[k+1][j][pair[1]]
                            if table[i][j][l_rule] < new_prob:
                                table[i][j][l_rule] = new_prob
                                node = Node(l_rule.tag)
                                node.add_child(nodes_table[i][k][pair[0] if isinstance(pair[0],str) else pair[0].tag])
                                node.add_child(nodes_table[i][k][pair[1] if isinstance(pair[1],str) else pair[1].tag])
                                nodes_table[i][j][l_rule.tag] = node
        return nodes_table[0][len(sentence)-1]['TOP']
