'''

This source file is an empty solution file inheriting the required spec class for this assignmentself.
It also demonstrates one way of writing your parses to the required output file

See the spec that this class inherits, for the spec details

'''
from collections import defaultdict

from RandomTree import randomize_tree
from spec import Spec
from time import sleep

from transformations import get_terminal_or_non_t, CNF_transformer, to_non_t, remove_non_t_pref, reverse_dict
from util.tree.builders import node_tree_from_sequence, sequence_from_tree


class Submission(Spec):

    def __init__(self):
        super().__init__()
        self.raw_rules_dict = defaultdict(lambda: defaultdict(float))
        self._transformed_dic = dict()
        self._reversed_dict = dict()

    def _count_occurrences(self, node, occurrences_dict):
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
        self._transformed_dic = CNF_transformer().transform(self.raw_rules_dict)
        self._reversed_dict = reverse_dict(self._transformed_dic)
        print("Training finished")



    
    def parse(self, sentence):
        ''' mock parsing function, returns a constant parse unrelated to the input sentence '''
        return '(TOP (S (VP (VB TM)) (NP (NNT MSE) (NP (H H) (NN HLWWIIH))) (yyDOT yyDOT)))'
    
    def write_parse(self, sentences, output_treebank_file='output/predicted.txt'):
        ''' function writing the parse to the output file '''
        with open(output_treebank_file, 'w') as f:
            for sentence in sentences:
                f.write(self.parse(sentence))
                f.write('\n')
                