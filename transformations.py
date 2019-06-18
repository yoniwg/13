from collections import defaultdict
from copy import deepcopy

NON_T_PREF = '$@$'


def to_non_t(tag):
    return NON_T_PREF + tag


def is_terminal(tag):
    return tag[:3] != NON_T_PREF


def get_terminal_or_non_t(node):
    if node.children:
        return to_non_t(node.tag)
    return node.tag





class CNF_transformer:
    def __init__(self, raw_rules_dict):
        super().__init__()
        self.cnf_rules_dict = deepcopy(raw_rules_dict)

    @staticmethod
    def _is_unary(prod):
        return prod.count(' ') == 0 and not is_terminal(prod)

    def transform(self):
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
        assert self._only_binaries(), "Found non-binary rules"

        revered_dict = defaultdict(lambda: defaultdict(float))
        for rule in self.cnf_rules_dict.items():
            non_t, prods = rule
            for prod_prob in prods.items():
                prod, prob = prod_prob
                if prob == 0:  # zero probability means it was removed
                    continue
                revered_dict[prod][non_t] = prod_prob
        return revered_dict

    def _binarize(self, prod, head_non_t, prev_prod, prob):
        self.cnf_rules_dict[prev_prod][prod] = 0
        if prev_prod == prod:
            return
        for prod_prod_prob in self.cnf_rules_dict[prod].items():
            prod_prod, prod_prob = prod_prod_prob
            if prod_prob == 0:
                continue
            if self._is_unary(prod_prod):
                self._binarize(prod_prod, head_non_t, prod, prod_prob * prob)
            else:
                self.cnf_rules_dict[head_non_t][prod_prod] += prod_prob * prob

    def _percolate(self, prod, non_t):
        split_prod = prod.split(' ')
        prob = self.cnf_rules_dict[non_t][prod]
        self.cnf_rules_dict[non_t][prod] = 0
        for i in range(len(split_prod) - 2):
            first = split_prod[i]
            remain = '-'.join(split_prod[:i+1]) + '*' + '-'.join(split_prod[i+1:])
            self.cnf_rules_dict[non_t][first + ' ' + remain] = prob
            non_t = remain
            prod = 1
        self.cnf_rules_dict[non_t][' '.join(split_prod[-2:])] = 1

    def _only_binaries(self):
        for rules in self.cnf_rules_dict.values():
            for prod in rules.items():
                if (prod[0].count(' ') > 2 or self._is_unary(prod[0])) and prod[1] != 0:
                    return False
        return True

