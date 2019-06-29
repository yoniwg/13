from solution import Submission
from transformation.derivations import to_non_t, get_terminal_or_non_t
from collections import defaultdict

from util.tree.builders import sequence_from_tree
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
        root_node = Node('TOP')
        cell = chart[chartI][chartJ]
        maxProb = -1
        selectedRule = ""
        for rule, prob in cell.prob_dict.items():
            if (prob > maxProb):
                maxProb = prob
                selectedRule = rule

        start_node = Node(selectedRule)
        root_node.add_child(start_node)

        path = cell.path_dic[selectedRule]
        left, right = path
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
        left, right = path
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
            if terminal_deriver is  None:
                return ""
            for rule, prob in terminal_deriver.items():
                node = chart[1][x+1]
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
                            rule_deriver = self._reversed_dict.get(rules)
                            if rule_deriver is not None:
                                leavesProb = firstProb * secondProb
                                for source_rule, prob in rule_deriver.items():
                                    curentProb =  node.prob_dict[source_rule]
                                    newProb = prob * leavesProb
                                    if(newProb>curentProb):
                                        node.prob_dict[source_rule] = newProb
                                        node.path_dic[source_rule]=((firstRule, k, j), (secondRule, i-k, j+k))

        #create tree
        root_node = self.createTree(chart, lengh, 1)

        return sequence_from_tree(root_node)



class Solution1_2(Solution1):

    def __init__(self):
        super().__init__(False)
