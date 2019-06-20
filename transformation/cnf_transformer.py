from collections.__init__ import defaultdict
from copy import deepcopy

from transformation.derivations import is_terminal
from util.tree.node import Node


def assert_sum_to_one(prob_dict):
    for rule in prob_dict:
        prob_sum = sum(prob_dict[rule].values())
        assert prob_sum == 0 or abs(1 - prob_sum) < 0.02, rule + "'s products sum up to " + prob_sum


class cnf_transformer:
    def __init__(self, omit_unaries=True):
        super().__init__()
        self.cnf_rules_dict = dict()
        self.omit_unaries = omit_unaries

    @staticmethod
    def _is_unary(prod):
        return prod.count(' ') == 0 and not is_terminal(prod)

    @staticmethod
    def merge_non_terminals(parent, child):
        return parent + '+' + child

    def transform(self, raw_rules_dict):
        self.cnf_rules_dict = deepcopy(raw_rules_dict)
        assert_sum_to_one(self.cnf_rules_dict)
        if self.omit_unaries:
            for rule in list(self.cnf_rules_dict.items()):
                non_t, prods = rule
                for prod_prob in list(prods.items()):
                    prod, prob = prod_prob
                    if prob == 0:  # zero probability means it was removed
                        continue
                    if self._is_unary(prod):
                        self.cnf_rules_dict[non_t][prod] = 0
                        self._percolate(non_t, prod, prob)

        assert_sum_to_one(self.cnf_rules_dict)
        for rule in list(self.cnf_rules_dict.items()):
            non_t, prods = rule
            for prod_prob in list(prods.items()):
                prod, prob = prod_prob
                if prob == 0:  # zero probability means it was removed
                    continue
                tags_count = prod.count(' ') + 1
                if tags_count > 2:
                    self._binarize(prod, non_t)
        assert self._transformed(), "Found non-binary rules"
        assert_sum_to_one(self.cnf_rules_dict)

        clean_dict = defaultdict(lambda: defaultdict(float))
        for rule in self.cnf_rules_dict.items():
            non_t, prods = rule
            for prod_prob in prods.items():
                prod, prob = prod_prob
                if prob == 0:  # zero probability means it was removed
                    continue
                clean_dict[non_t][prod] = prob
        assert_sum_to_one(clean_dict)
        return clean_dict

    # def _percolate(self, prod, non_t_accum, prev_prod, prob):
    #     self.cnf_rules_dict[prev_prod][prod] = 0
    #     non_t_accum = self.merge_non_terminals(non_t_accum, prod)
    #     if prev_prod == prod:
    #         return
    #     for prod_prod_prob in self.cnf_rules_dict[prod].items():
    #         prod_prod, prod_prob = prod_prod_prob
    #         if prod_prob == 0:
    #             continue
    #         if self._is_unary(prod_prod):
    #             self._percolate(prod_prod, non_t_accum, prod, prod_prob * prob)
    #         else:
    #             self.cnf_rules_dict[non_t_accum][prod_prod] += prod_prob * prob

    def _percolate(self, rule_l, rule_r, prob, rules_chain=set()):
        if rule_l == rule_r:
            return
        rules_chain.add(rule_r)
        for prod_prod_prob in self.cnf_rules_dict[rule_r].items():
            prod_prod, prod_prob = prod_prod_prob
            if prod_prob == 0 or prod_prod in rules_chain:
                continue
            if self._is_unary(prod_prod):
                self._percolate(rule_l, prod_prod, prod_prob * prob)
            else:
                self.cnf_rules_dict[rule_l][prod_prod] += prod_prob * prob

    def _binarize(self, prod, non_t):
        split_prod = prod.split(' ')
        prob = self.cnf_rules_dict[non_t][prod]
        self.cnf_rules_dict[non_t][prod] = 0
        for i in range(len(split_prod) - 2):
            first = split_prod[i]
            remain = '-'.join(split_prod[:i + 1]) + '*' + '-'.join(split_prod[i + 1:])
            self.cnf_rules_dict[non_t][first + ' ' + remain] = prob
            non_t = remain
            prob = 1
        self.cnf_rules_dict[non_t][' '.join(split_prod[-2:])] = 1

    def _transformed(self):
        for rules in self.cnf_rules_dict.values():
            for prod in rules.items():
                if (prod[0].count(' ') > 2 or (self._is_unary(prod[0]) and self.omit_unaries)) \
                        and prod[1] != 0:
                    return False
        return True

    def detransform(self, root_node):
        if not root_node.children:
            return
        for child_idx in range(len(root_node.children)):
            child = root_node.children[child_idx]
            if child.count('+'):
                self._depercolate(child)
            if child.count('*'):
                self._debinarize(root_node, child_idx)

    @staticmethod
    def _depercolate(node):
        plus_idx = node.tag.index('+')
        new_node = Node(node.tag[plus_idx + 1:])
        new_node.children = node.children
        node.children = []
        node.tag = node.tag[:plus_idx]

    @staticmethod
    def _debinarize(parent, child_idx):
        node = parent.children.pop(child_idx)
        for gr_child in reversed(node.children):  # reversed since we push it in child_idx
            parent.children.insert(child_idx, gr_child)
