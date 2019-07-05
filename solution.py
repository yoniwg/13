'''

This source file is an empty solution file inheriting the required spec class for this assignmentself.
It also demonstrates one way of writing your parses to the required output file

See the spec that this class inherits, for the spec details

'''
from collections import defaultdict

from spec import Spec
from transformation.cnf_transformer import cnf_transformer
from transformation.derivations import UNKNOWN_T, is_terminal, UNKNOWN_NON_T
from util.tree.builders import node_tree_from_sequence


def reverse_dict(rules_dict):
    reversed_dict = defaultdict(lambda: defaultdict(float))
    for (non_t, prods) in rules_dict.items():
        for (prod, prob) in prods.items():
            reversed_dict[prod][non_t] = prob
    return reversed_dict


class Submission(Spec):

    def __init__(self, omit_unaries):
        super().__init__()
        self.raw_rules_dict = defaultdict(lambda: defaultdict(float))
        self._transformed_dic = dict()
        self._reversed_dict = dict()
        self._transformer = cnf_transformer(omit_unaries)

    def _count_occurrences(self, root, occurrences_dict):
        """ Abstract """

    def train(self, training_treebank_file='data/heb-ctrees.train'):
        ''' mock training function, learns nothing '''
        print("Starting Training")
        occurrences_dict = defaultdict(lambda: defaultdict(int))
        print("Reading from train bank file")
        with open(training_treebank_file, 'r') as train_set:
            for line in train_set:
                tree = node_tree_from_sequence(line)
                self._count_occurrences(tree, occurrences_dict)
        print("Calculating probabilities")
        for non_t_occur in occurrences_dict.items():
            non_t, productions = non_t_occur
            non_t_count = sum(productions.values())
            for prod_occur in productions.items():
                prod, prod_count = prod_occur
                self.raw_rules_dict[non_t][prod] = prod_count / non_t_count
        print("Transforming to CNF")
        self._transformed_dic = dict(self._transformer.transform(self.raw_rules_dict))
        print("Handling unknown rules")
        self._add_unknowns()
        print("Adding reversed rules")
        self._reversed_dict = reverse_dict(self._transformed_dic)

    def parse(self, sentence):
        ''' Abstract '''

    # '(TOP (S (VP (VB TM)) (NP (NNT MSE) (NP (H H) (NN HLWWIIH))) (yyDOT yyDOT)))'

    def write_parse(self, sentences, output_treebank_file='output/predicted.txt'):
        ''' function writing the parse to the output file '''
        print("Start parsing")
        with open(output_treebank_file, 'w') as f:
            for i, sentence in enumerate(sentences):
                print('\rParsing sentence #{}'.format(i+1), end='')
                f.write(self.parse(sentence))
                f.write('\n')
                f.flush()
        print("Finished parsing {} sentences".format(i+1))

    def get_only_terminal_prob(self, non_t):
        return sum(map(lambda prod: prod[1] if is_terminal(prod[0]) else 0, self._transformed_dic[non_t].items()))

    def _add_unknowns(self):
        terminal_derivation_probs = dict([(non_t, self.get_only_terminal_prob(non_t)) for non_t in self._transformed_dic])
        for rule, prods in self._transformed_dic.items():
            l_probs = defaultdict(lambda : [0, 0.0, 0.0])
            r_probs = defaultdict(lambda : [0, 0.0, 0.0])
            for prod, prob in prods.items():
                if ' ' in prod:
                    l_non_t, r_non_t = prod.split(' ')
                    prob_l_derives_t = terminal_derivation_probs[l_non_t]
                    prob_r_derives_t = terminal_derivation_probs[r_non_t]
                    l_probs[l_non_t][0] += 1
                    l_probs[l_non_t][1] += prob * prob_r_derives_t
                    l_probs[l_non_t][2] += prob * (1 - prob_r_derives_t)
                    r_probs[r_non_t][0] += 1
                    r_probs[r_non_t][1] += prob * prob_l_derives_t
                    r_probs[r_non_t][2] += prob * (1 - prob_l_derives_t)
            for l_prob, findings in l_probs.items():
                if findings[1]:
                    prods[' '.join([l_prob, UNKNOWN_T])] = findings[1] / findings[0]
                if findings[2]:
                    prods[' '.join([l_prob, UNKNOWN_NON_T])] = findings[2] / findings[0]
            for r_prob, findings in r_probs.items():
                if findings[1]:
                    prods[' '.join([UNKNOWN_T, r_prob])] = findings[1] / findings[0]
                if findings[2]:
                    prods[' '.join([UNKNOWN_NON_T, r_prob])] = findings[2] / findings[0]

