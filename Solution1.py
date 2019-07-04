import itertools
import operator

from solution import Submission
from transformation.derivations import to_non_t, get_terminal_or_non_t, remove_non_t_pref, UNKNOWN_T
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


class DerivationInfo:
    def __init__(self):
        self.prob_dict = defaultdict(float)
        self.path_dic = dict()

class Solution1_1(Solution1):

    def __init__(self):
        super().__init__(True)

    def createTree(self, chart, chartI, chartJ):
        root_node = Node(to_non_t('TOP'))
        cell = chart[chartI][chartJ]
        maxProb = -1
        selectedRule = ''
        for rule, prob in cell.prob_dict.items():
            if (prob > maxProb):
                maxProb = prob
                selectedRule = rule
        start_node = Node(selectedRule)
        root_node.add_child(start_node)
        if not selectedRule:
            return root_node

        path = cell.path_dic[selectedRule]
        u_path, left, right = path

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
        selectedRule = ""
        for rule, prob in cell.prob_dict.items():
            if (prob > maxProb):
                maxProb = prob
                selectedRule = rule

        path = cell.path_dic[selectedRule]
        u_path, left, right = path

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
        chart = [[DerivationInfo() for j in range(lengh+1)] for i in range(lengh+1)]

        #init
        for x in range(lengh):
            terminal_deriver = self._reversed_dict.get(sentence[x])
            node = chart[1][x + 1]
            if terminal_deriver is None:
                node.prob_dict[UNKNOWN_T] = 0.0001
                node.path_dic[UNKNOWN_T] = ((sentence[x], x + 1, 0), ("", 0, 0))
            else:
                for rule, prob in terminal_deriver.items():
                    node.prob_dict[rule]=prob
                    node.path_dic[rule]=((sentence[x], x+1, 0), ("", 0, 0))

        #main loop
        for i in range(2, lengh+1):
            for j in range(1, lengh+2-i):
                node = chart[i][j]
                for k in range(1, i):
                    firstNodeToCheck = chart[k][j]
                    secondNodeToCheck = chart[i-k][j+k]

                    for firstRule, firstProb in firstNodeToCheck.prob_dict.items():
                        for secondRule, secondProb in secondNodeToCheck.prob_dict.items():
                            rules = firstRule + " " + secondRule
                            rules_deriver = self._reversed_dict.get(rules)
                            if rules_deriver is not None:
                                leavesProb = firstProb * secondProb
                                for source_rule, prob in rules_deriver.items():
                                    for unary_first, (u_path, u_prob) in self.find_unaries(source_rule, prob).items():
                                        curentProb = node.prob_dict[unary_first]
                                        newProb = u_prob * leavesProb
                                        if newProb > curentProb:
                                            node.prob_dict[source_rule] = newProb
                                            node.path_dic[source_rule]=(u_path, (firstRule, k, j), (secondRule, i-k, j+k))

                node.prob_dict = dict(sorted(node.prob_dict.items(), key=operator.itemgetter(1), reverse=True)[:100])
        #create tree
        root_node = self.createTree(chart, lengh, 1)


        self._transformer.detransform(root_node)
        remove_non_t_pref(root_node)
        return sequence_from_tree(root_node)

    def find_unaries(self, source_rule, source_prob, path_tup=tuple()):
        unaries = dict()
        for rule, prob in self._reversed_dict[source_rule].items():
            if prob > source_prob:
                path_tup += (rule,)
                unaries[source_rule] = (path_tup, prob)
        for rule, (path, prob) in list(unaries.items()):
            unaries += self.find_unaries(rule, path, prob).items()
        return unaries





class Solution1_2(Solution1):

    def __init__(self):
        super().__init__(False)
