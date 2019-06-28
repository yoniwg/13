from solution import Submission
from transformation.derivations import to_non_t, get_terminal_or_non_t
from collections import defaultdict


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

    def addNodeToTree(self, chart, chartI, chartJ, tree):
        cell = chart[chartI][chartJ]
        tree += "("
        maxProb = -1
        selectedRule = ""
        for rule, prob in cell.prob_dict.items():
            if(prob>maxProb):
                maxProb = prob
                selectedRule = rule

        tree +=  selectedRule
        path = cell.path_dic[selectedRule]
        left, right = path
        leftRule, leftI, leftJ = left
        if(leftJ==0):
            tree +=  leftRule
            tree +=  ")"
            return tree

        tree +=  self.addNodeToTree(chart, leftI, leftJ, tree)

        rightRule, rightI, rightJ = right
        tree +=  self.addNodeToTree(chart, rightI, rightJ, tree)

        tree +=  ")"
        return tree

    def parse(self, sentence):
        lengh = len(sentence)
        chart = [[DerivationInfo() for j in range(lengh+1)] for i in range(lengh+1)]

        #init
        for x in range(lengh):
            print(sentence[x])
            terminal_deriver = self._reversed_dict.get(sentence[x])
            if terminal_deriver is  None:
                return ""
            for rule, val in terminal_deriver.items():
                prob = val[1]
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
                                for source_rule, val in rule_deriver.items():
                                    prob = val[1]
                                    curentProb =  node.prob_dict[source_rule]
                                    newProb = prob * leavesProb
                                    if(newProb>curentProb):
                                        node.prob_dict[source_rule] = newProb
                                        node.path_dic[source_rule]=((firstRule, k, j), (secondRule, i-k, j+k))

        #create tree
        topNode = chart[lengh][1]
        tree = ""
        res = self.addNodeToTree(chart, lengh, 1, tee)


        b = 5



class Solution1_2(Solution1):

    def __init__(self):
        super().__init__(False)
