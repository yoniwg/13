'''

Usage
-----

In your Anaconda terminal or other terminal where your python environment is available:

    python go.py

'''
import ProjectSolution2

from ProjectSolution2 import TerminalsHanler
from ProjectSolution2 import RulesHanler
from util.tree.node import Node
import Solution1
#from ProjectSolution import ProjectSolution
from Solution3 import Solution3
from parser_driver import drive
import solution

node0 = Node("TOP", 0);
node1 = Node("S", 0, node0);
node0.add_child(node1);

node2 = Node("NP", 0, node1);
node1.add_child(node2);
node3 = Node("VP", 1, node1);
node1.add_child(node3);

node4 = Node("NN", 0, node2);
node2.add_child(node4);
node5 = Node("NN", 1, node2);
node2.add_child(node5);

node6 = Node("Term1", 0, node4);
node4.add_child(node6);
node7 = Node("Term2", 0, node5);
node5.add_child(node7);

node8 = Node("V", 0, node3);
node3.add_child(node8);
node9 = Node("NP", 1, node3);
node3.add_child(node9);

node10 = Node("Term3", 0, node8);
node8.add_child(node10);

node11 = Node("DT", 0, node9);
node9.add_child(node11);
node12 = Node("NN", 1, node9);
node9.add_child(node12);

node13 = Node("Term4", 0, node11);
node11.add_child(node13);
node14 = Node("Term5", 0, node12);
node12.add_child(node14);



list = ["TOP","S", "NP", "VP", "NN", "V", "NP", "DT"];
list2 = ["Term1","Term4"]


test1 = TerminalsHanler(list, list2, 1, 1)


b = test1.createTerminalsListForTree(node0);

a = test1.createFeaturesListForNode(b,2);

test2 = RulesHanler(list, 4);
test2.createFeaturesListForNodes(node2, node9);


drive(Solution1.Solution1_2)