import os.path as path
from os import remove
import time

from util.tree.get_yield import get_yield
from util.tree.builders import list_tree_from_sequence


def get_sentences():
    # return [['W', 'EL', 'KK', 'TEID', 'H', 'HISJWRIH', 'yyCM', 'W', 'IEIDW', 'EFRWT', 'H', 'LWXMIM', 'F', 'NFARW', 'B', 'H', 'XIIM', 'W', 'HCLIXW', 'LBCE', 'AT', 'MFIMTM', 'EL', 'AP', 'H', 'ABDWT', 'H', 'KBDWT', 'yyDOT']]
    with open('data/heb-ctrees.gold') as fd:
        lines = fd.readlines()
        for line in lines:
            yield get_yield(list_tree_from_sequence(line))


def drive(parser_class_under_test, output_treebank_file='output/predicted.txt'):
    ''' a simplified version of the solution driver to be used for testing all submissions '''
    
    parser = parser_class_under_test()
    
    # invoke the training
    before = time.time()
    parser.train()
    print(f'training took {time.time() - before:.1f} seconds')
    
    if path.exists(output_treebank_file):
        remove(output_treebank_file)
    
    # parse
    before = time.time()
    parser.write_parse(
        get_sentences(),
        output_treebank_file)
    print(f'parsing took {time.time() - before:.1f} seconds')
    
    # you can use other output paths for your experiments,
    # but for the final submission, you must to use the
    # default one used here:                    
    assert path.exists(output_treebank_file), 'your write_parse method did not write its output!' 
    
    print('thanks for the parsing!\n')
    