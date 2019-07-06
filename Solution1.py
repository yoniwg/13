import itertools
import operator

from solution import Submission
from transformation.derivations import to_non_t, get_terminal_or_non_t, remove_non_t_pref, UNKNOWN_T, is_unary, \
    is_terminal
from collections import defaultdict

from util.tree.builders import sequence_from_tree, node_tree_from_sequence
from util.tree.node import Node

class Solution1(Submission):

    def __init__(self, omit_unaries):
        super().__init__(omit_unaries)

    def _count_occurrences(self, node, occurrences_dict):
        if not node.children:
            return
        occurrences_dict[to_non_t(node.tag)][' '.join(map(get_terminal_or_non_t, node.children))] += 1
        for child in node.children:
            self._count_occurrences(child, occurrences_dict)

    def createTree(self, chart, chartI, chartJ):
        root_node = Node(to_non_t('TOP'))
        cell = chart[chartI][chartJ]
        maxProb = -1
        start_node = Node("")
        selected_info = None
        for rule, info in cell.items():
            if info[0] and info[0] > maxProb:
                maxProb = info[0]
                start_node.tag = rule
                selected_info = info
        root_node.add_child(start_node)
        if not selected_info:
            return root_node

        _, u_path, left, right = selected_info

        for non_t in u_path:
            u_node = Node(non_t)
            start_node.add_child(u_node)
            start_node = u_node

        leftRule, leftI, leftJ = left
        if (leftJ == 0):
            start_node.add_child(Node(leftRule))
            return root_node

        leftChild = Node(leftRule)
        start_node.add_child(leftChild)
        rightRule, rightI, rightJ = right
        rightChild = Node(rightRule)
        start_node.add_child(rightChild)

        self.addNodeToTree(chart, leftI, leftJ, leftChild)
        self.addNodeToTree(chart, rightI, rightJ, rightChild)

        return root_node

    def addNodeToTree(self, chart, chartI, chartJ, node):
        cell = chart[chartI][chartJ]
        maxProb = -1
        selected_info = None
        for rule, info in cell.items():
            if info[0] and info[0] > maxProb:
                maxProb = info[0]
                selected_info = info
        if not selected_info:
            return node

        _, u_path, left, right = selected_info

        for non_t in u_path:
            u_node = Node(non_t)
            node.add_child(u_node)
            node = u_node

        leftRule, leftI, leftJ = left
        if (leftJ == 0):
            node.add_child(Node(leftRule))
            return

        leftChild = Node(leftRule)
        node.add_child(leftChild)
        rightRule, rightI, rightJ = right
        rightChild = Node(rightRule)
        node.add_child(rightChild)

        self.addNodeToTree(chart, leftI, leftJ, leftChild)
        self.addNodeToTree(chart, rightI, rightJ, rightChild)


    def parse(self, sentence):
        lengh = len(sentence)
        chart = [[dict() for j in range(lengh+1)] for i in range(lengh+1)]

        #init
        for x in range(lengh):
            terminal_deriver = self._reversed_dict.get(sentence[x])
            node = chart[1][x + 1]
            if terminal_deriver is None:
                self.fill_node(node, UNKNOWN_T, 0.0001, 1, (sentence[x], x + 1, 0), ("", 0, 0))
            else:
                for rule, prob in terminal_deriver.items():
                    self.fill_node(node, rule, prob,1,(sentence[x], x+1, 0), ("", 0, 0))

        #main loop
        for i in range(2, lengh+1):
            for j in range(1, lengh+2-i):
                node = chart[i][j]
                for k in range(1, i):
                    firstNodeToCheck = chart[k][j]
                    secondNodeToCheck = chart[i-k][j+k]

                    for firstRule, (firstProb,_,_,_) in firstNodeToCheck.items():
                        for secondRule, (secondProb,_,_,_) in secondNodeToCheck.items():
                            rules = firstRule + " " + secondRule
                            rules_deriver = self._reversed_dict.get(rules)
                            if rules_deriver is not None:
                                leavesProb = firstProb * secondProb
                                for source_rule, prob in rules_deriver.items():
                                    self.fill_node(node, source_rule, prob, leavesProb,(firstRule, k, j), (secondRule, i-k, j+k))


                chart[i][j] = dict(sorted(node.items(), key=operator.itemgetter(1,0), reverse=True)[:300])
        #create tree
        root_node = self.createTree(chart, lengh, 1)


        self._transformer.detransform(root_node)
        remove_non_t_pref(root_node)
        return sequence_from_tree(root_node)

    def fill_node(self, node, source_rule, prob, leavesProb, l_child, r_child):
        '''abstract'''




class Solution1_1(Solution1):

    def __init__(self):
        super().__init__(True)

    def fill_node(self, node, source_rule, prob, leavesProb, l_child, r_child):
        newProb = prob * leavesProb
        if source_rule not in node or newProb > node[source_rule][0]:
            node[source_rule] = (newProb, tuple(), l_child, r_child)

class Solution1_2(Solution1):

    def __init__(self):
        super().__init__(False)
        self._unaries_dict = dict()

    def train(self, training_treebank_file='data/heb-ctrees.train'):
        super().train(training_treebank_file)
        print("Calculating unary rules paths")
        self.init_unaries_dict()

    def __find_unaries(self, source_rule, unaries):
        path_tup, source_prob = unaries[source_rule]
        new_rules = set()
        if source_rule not in self._reversed_dict:
            return unaries
        num_prev_path = len(path_tup)
        for rule, prob in self._reversed_dict[source_rule].items():
            merged_prob = (prob + source_prob * num_prev_path) / (num_prev_path + 1)
            if rule not in path_tup and (rule not in unaries or merged_prob > unaries[rule][1]):
                unaries[rule] = (path_tup + (source_rule,), merged_prob)
                new_rules.add(rule)
        for rule in new_rules:
            self.__find_unaries(rule, unaries)
        return unaries

    def init_unaries_dict(self):
        for rule in list(self._transformed_dic.keys()) + [UNKNOWN_T]:
            if not is_terminal(rule) and is_unary(rule):
                unaries = self.__find_unaries(rule, {rule: (tuple(), 1)})
                self._unaries_dict[rule] = unaries

    def fill_node(self, node, source_rule, prob, leavesProb, l_child, r_child):
        for unary_top, (u_path, u_prob) in self._unaries_dict[source_rule].items():
            newProb = leavesProb * (prob + u_prob * len(u_path)) / (len(u_path) + 1)
            if unary_top not in node or newProb > node[unary_top][0]:
                node[unary_top] = (newProb, u_path, l_child, r_child)