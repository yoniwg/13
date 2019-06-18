from collections import defaultdict
from copy import deepcopy

from util.tree.node import Node

NON_T_PREF = '$@$'


def to_non_t(tag):
    return NON_T_PREF + tag

def is_terminal(tag):
    return tag[:len(NON_T_PREF)] != NON_T_PREF


def get_terminal_or_non_t(node):
    if node.children:
        return to_non_t(node.tag)
    return node.tag


def remove_non_t_pref(node):
    if not is_terminal(node.tag):
        node.tag = node.tag[len(NON_T_PREF):]
        for child in node.children:
            remove_non_t_pref(child)


def reverse_dict(rules_dict):
    reversed_dict = defaultdict(lambda: defaultdict(float))
    for rule in rules_dict.items():
        non_t, prods = rule
        for prod_prob in prods.items():
            prod, prob = prod_prob
            reversed_dict[prod][non_t] = prod_prob
    return reversed_dict


class CNF_transformer:
    def __init__(self, omit_unaries=False):
        super().__init__()
        self.cnf_rules_dict = dict()
        self.omit_unaries = omit_unaries

    @staticmethod
    def _is_unary(prod):
        return prod.count(' ') == 0 and not is_terminal(prod)

    def transform(self, raw_rules_dict):
        self.cnf_rules_dict = deepcopy(raw_rules_dict)
        if self.omit_unaries:
            for rule in list(self.cnf_rules_dict.items()):
                non_t, prods = rule
                for prod_prob in list(prods.items()):
                    prod, prob = prod_prob
                    if prob == 0:  # zero probability means it was removed
                        continue
                    if self._is_unary(prod):
                        self._binarize(prod, non_t, non_t, prob)

        for rule in list(self.cnf_rules_dict.items()):
            non_t, prods = rule
            for prod_prob in list(prods.items()):
                prod, prob = prod_prob
                if prob == 0:  # zero probability means it was removed
                    continue
                tags_count = prod.count(' ') + 1
                if tags_count > 2:
                    self._percolate(prod, non_t)
        assert self._transformed(), "Found non-binary rules"

        clean_dict = defaultdict(lambda: defaultdict(float))
        for rule in self.cnf_rules_dict.items():
            non_t, prods = rule
            for prod_prob in prods.items():
                prod, prob = prod_prob
                if prob == 0:  # zero probability means it was removed
                    continue
                clean_dict[non_t][prod] = prod_prob
        return clean_dict

    def _binarize(self, prod, non_t_accum, prev_prod, prob):
        self.cnf_rules_dict[prev_prod][prod] = 0
        non_t_accum += '+' + prod
        if prev_prod == prod:
            return
        for prod_prod_prob in self.cnf_rules_dict[prod].items():
            prod_prod, prod_prob = prod_prod_prob
            if prod_prob == 0:
                continue
            if self._is_unary(prod_prod):
                self._binarize(prod_prod, non_t_accum, prod, prod_prob * prob)
            else:
                self.cnf_rules_dict[non_t_accum][prod_prod] += prod_prob * prob

    def _percolate(self, prod, non_t):
        split_prod = prod.split(' ')
        prob = self.cnf_rules_dict[non_t][prod]
        self.cnf_rules_dict[non_t][prod] = 0
        for i in range(len(split_prod) - 2):
            first = split_prod[i]
            remain = '-'.join(split_prod[:i + 1]) + '*' + '-'.join(split_prod[i + 1:])
            self.cnf_rules_dict[non_t][first + ' ' + remain] = prob
            non_t = remain
            prod = 1
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
                self._debinarize(child)
            if child.count('*'):
                self._depercolate(root_node, child_idx)

    @staticmethod
    def _debinarize(node):
        plus_idx = node.tag.index('+')
        new_node = Node(node.tag[plus_idx + 1:])
        new_node.children = node.children
        node.children = []
        node.tag = node.tag[:plus_idx]

    @staticmethod
    def _depercolate(parent, child_idx):
        node = parent.children.pop(child_idx)
        for gr_child in reversed(node.children):  # reversed since we push it in child_idx
            parent.children.insert(child_idx, gr_child)
