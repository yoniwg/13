'''

This source file is an empty solution file inheriting the required spec class for this assignmentself.
It also demonstrates one way of writing your parses to the required output file

See the spec that this class inherits, for the spec details

'''
from collections import defaultdict

from spec import Spec
from transformation.cnf_transformer import cnf_transformer
from transformation.derivations import UNKNOWN_NON_T
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
        occurrences_dict = defaultdict(lambda: defaultdict(int))
        with open(training_treebank_file, 'r') as train_set:
            for line in train_set:
                tree = node_tree_from_sequence(line)
                self._count_occurrences(tree, occurrences_dict)
        for non_t_occur in occurrences_dict.items():
            non_t, productions = non_t_occur
            non_t_count = sum(productions.values())
            for prod_occur in productions.items():
                prod, prod_count = prod_occur
                self.raw_rules_dict[non_t][prod] = prod_count / non_t_count
        self._transformed_dic = self._transformer.transform(self.raw_rules_dict)
        self._add_unknowns()
        self._reversed_dict = reverse_dict(self._transformed_dic)
        print("Training finished")

    def parse(self, sentence):
        ''' Abstract '''

    # '(TOP (S (VP (VB TM)) (NP (NNT MSE) (NP (H H) (NN HLWWIIH))) (yyDOT yyDOT)))'

    def write_parse(self, sentences, output_treebank_file='output/predicted.txt'):
        ''' function writing the parse to the output file '''
        with open(output_treebank_file, 'w') as f:
            for sentence in sentences:
                f.write(self.parse(sentence))
                f.write('\n')
                f.flush()

    def _add_unknowns(self):
        for rule, prods in self._transformed_dic.items():
            l_probs = defaultdict(lambda : [0, 0.0])
            r_probs = defaultdict(lambda : [0, 0.0])
            for prod, prob in prods.items():
                if ' ' in prod:
                    l_non_t, r_non_t = prod.split(' ')
                    l_probs[l_non_t][0] += 1
                    l_probs[l_non_t][1] += prob
                    r_probs[r_non_t][0] += 1
                    r_probs[r_non_t][1] += prob
            for l_prob in l_probs:
                prods[' '.join([l_prob, UNKNOWN_NON_T])] = l_probs[l_prob][1] / l_probs[l_prob][0]
            for r_prob in r_probs:
                prods[' '.join([UNKNOWN_NON_T, r_prob])] = r_probs[r_prob][1] / r_probs[r_prob][0]

