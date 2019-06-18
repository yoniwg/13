import random
from collections import defaultdict

from transformations import is_terminal
from util.tree.node import Node

used_rules = defaultdict(int)


def randomize_tree(cnf_dict, tag, tree_root=None):
    node = Node(tag)
    if tree_root is None:
        tree_root = node
    if not is_terminal(tag):
        rules = list(cnf_dict[tag].keys())
        while rules:
            for used_rule in used_rules:
                if used_rules[used_rule] and rules.count(used_rule) > 0:
                    rules.remove(used_rule)
            if not rules:
                return None
            rule = random.choice(rules)
            if not is_terminal(rule):
                used_rules[rule] += 1
            for child_tag in rule.split(' '):
                rand_child = randomize_tree(cnf_dict, child_tag, tree_root)
                if rand_child is None:
                    used_rules[rule] = 4
                    node.children = []
                    break
                node.children.append(rand_child)
            if node.children:
                break
    return node
