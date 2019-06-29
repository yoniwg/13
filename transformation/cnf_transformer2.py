import sys
from collections import defaultdict
from copy import deepcopy, copy


def assert_sum_to_one(prob_dict):
    for rule in prob_dict:
        prob_sum = sum(prob_dict[rule].values())
        assert prob_sum == 0 or abs(1 - prob_sum) < 0.01, rule.tag + "'s products sum up to " + prob_sum.__str__()


class Terminal(str):
    def __init__(self, tag):
        super().__init__(tag)
        self.tag = tag



class NonTerminal:

    def __init__(self, tag, parent, l_sisters):
        self.tag = tag
        self.parent = parent
        self.l_sisters = l_sisters

    def _key(self):
        return self.tag, self.parent, self.l_sisters

    def __hash__(self):
        return hash(self._key())

    def __eq__(self, other):
        return isinstance(self, type(other)) and self._key() == other._key()

    def __str__(self) -> str:
        return '|'.join(self.l_sisters) + '^' + self.tag + '@' + (self.parent or "")


class BinNonTerminal(NonTerminal):

    def __init__(self, prev_tags, next_tags, parent, h_lookback):
        combined_tag = '-'.join(map(lambda t: t.tag, prev_tags)) + '*' + '-'.join(map(lambda t: t.tag, next_tags))
        super().__init__(combined_tag, parent.tag if parent else None,
                         tuple(map(lambda t: t.tag, prev_tags[-h_lookback or sys.maxsize:])))


class CnfTransformer:
    def __init__(self, with_parent, h_lookback, omit_unaries=True):
        super().__init__()
        self.cnf_rules_dict = dict()
        self.omit_unaries = omit_unaries
        self.with_parent = with_parent
        self.h_lookback = h_lookback

    @staticmethod
    def _is_unary(prod):
        return len(prod) == 1 and isinstance(prod[0], NonTerminal)

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
                if prob == 0 or not isinstance(prod, tuple):  # zero probability means it was removed
                    continue
                if len(prod) > 2:
                    self._binarize(non_t, prod)
        assert_sum_to_one(self.cnf_rules_dict)
        assert self._transformed(), "Found non-binary rules"

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

    def _percolate(self, rule_l, rule_r_tup, prob, rules_chain=None):
        rule_r = rule_r_tup[0]  # always unary here
        if rule_l == rule_r:
            return
        if rules_chain is None:
            rules_chain = set()
        rules_chain.add(rule_r_tup)
        for prod_prod_prob in self.cnf_rules_dict[rule_r].items():
            prod_prod, prod_prob = prod_prod_prob
            if prod_prob == 0 or prod_prod in rules_chain:
                continue
            if self._is_unary(prod_prod):
                self._percolate(rule_l, prod_prod, prod_prob * prob, rules_chain)
            else:
                updated_rule = tuple(map(lambda t: NonTerminal(t.tag, rule_l.tag, t.l_sisters)
                                        if isinstance(t, NonTerminal) else t, prod_prod))
                self.cnf_rules_dict[rule_l][updated_rule] += prod_prob * prob

    def _binarize(self, rule_l, rule_r_tup):
        prob = self.cnf_rules_dict[rule_l][rule_r_tup]
        self.cnf_rules_dict[rule_l][rule_r_tup] = 0
        for i in range(len(rule_r_tup) - 1):
            if i < len(rule_r_tup) - 2:
                remain = BinNonTerminal(rule_r_tup[:i + 1], rule_r_tup[i + 1:], rule_l if self.with_parent else None,
                                        self.h_lookback)
            else:
                remain = NonTerminal(rule_r_tup[i + 1].tag, rule_l.tag if self.with_parent else None,
                                     tuple(map(lambda t: t.tag, rule_r_tup[:i + 1][-self.h_lookback or sys.maxsize:])))
            first = NonTerminal(rule_r_tup[i].tag, rule_l.tag if self.with_parent else None, tuple())
            if self.cnf_rules_dict[rule_l][(first, remain)] < 1:
                self.cnf_rules_dict[rule_l][(first, remain)] += prob
            rule_l = remain
            prob = 1

    def _transformed(self):
        for rules in self.cnf_rules_dict.values():
            for prod in rules.items():
                if (len(prod[0]) > 2 or (self._is_unary(prod[0]) and self.omit_unaries)) \
                        and prod[1] != 0:
                    return False
        return True

    def detransform(self, root_node):
        if not root_node.children:
            return
        for child_idx in range(len(root_node.children)):
            child = root_node.children[child_idx]
            if isinstance(child, BinNonTerminal):
                self._debinarize(root_node, child_idx)

    @staticmethod
    def _debinarize(parent, child_idx):
        node = parent.children.pop(child_idx)
        for gr_child in reversed(node.children):  # reversed since we push it in child_idx
            parent.children.insert(child_idx, gr_child)
