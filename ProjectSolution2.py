import operator
import sys

from math import log

from solution import Submission
from transformation.derivations import to_non_t, get_terminal_or_non_t, remove_non_t_pref, UNKNOWN_T, is_unary, \
    is_terminal

from util.tree.builders import sequence_from_tree
from util.tree.node import Node

class ProjectSolution:
    pass

class TerminalsHanler(ProjectSolution):
    def __init__(self, rulesList, delimitersList, NumFromBegin, NumFromEnd):
        self.rulesDict = {}

        for x in range(NumFromBegin):
            self.rulesDict[str(x+1) + "_FromBegin"] = 0;

        for x in range(NumFromEnd):
            self.rulesDict[str(x+1) + "_FromEnd"] = 0;

        for i, val in enumerate(rulesList):
            self.rulesDict["Uncle_" + val] = 0;

        for i, val in enumerate(rulesList):
            self.rulesDict["Uncle2_" + val] = 0;

        self.mNumFromBegin = NumFromBegin;
        self.mNumFromEnd = NumFromEnd;
        self.mDelimitersList = delimitersList;

    def createFeaturesList(self, uncle, uncle2, PlaceFromBegin, PlaceFromEnd):
        dic = self.rulesDict.copy();

        if (uncle != None):
            dic["Uncle_" + uncle] = 1;

        if (uncle2 != None):
            dic["Uncle2_" + uncle2] = 1;

        if(PlaceFromBegin<=self.mNumFromBegin):
            dic[str(PlaceFromBegin) + "_FromBegin"] = 1;

        if (PlaceFromEnd <= self.mNumFromEnd):
            dic[str(PlaceFromEnd) + "_FromEnd"] = 1;

        return dic.values();


    def createFeaturesListForNode(self, terminalsList, nodeIndex):
        uncle = None
        uncle2 = None
        if(nodeIndex>0):
            rule, terminnal = terminalsList[nodeIndex-1];
            uncle = rule;

        if (nodeIndex > 1):
            rule, terminnal = terminalsList[nodeIndex - 2];
            uncle2 = rule;

        preDelimeter, PostDelimeter = self.findDelimitersPlaceAroundInex(nodeIndex, terminalsList);

        return self.createFeaturesList(uncle, uncle2, nodeIndex-preDelimeter, PostDelimeter-nodeIndex);

    def createTerminalsListForTree(self, root):

        if (root.tag != "TOP"):
            print("ERROR: This isn't root");
            return None;

        node = root.children[0];
        terminalsList = list();
        self.getTerminals(node, terminalsList);

        return terminalsList;

    def getTerminals(self, node, TerminalsList):
        if (len(node.children) == 0):
            TerminalsList.append((node.parent.tag,node.tag))
            return;
        self.getTerminals(node.children[0], TerminalsList);

        if (len(node.children) == 2):
            self.getTerminals(node.children[1], TerminalsList);


    def findDelimitersPlaceAroundInex(self, index, TerminalsList):
        beforeIndex = -1
        afterIndex = len(TerminalsList);

        for idx, val in enumerate(TerminalsList):
            rule, terminal = val;
            if((idx<index) and  self.isDelimiter(terminal)):
                beforeIndex = idx;
            if ((idx > index) and self.isDelimiter(terminal)):
                afterIndex = idx;
                return (beforeIndex, afterIndex);

        return (beforeIndex, afterIndex);


    def isDelimiter(self, terminal):
        for word in self.mDelimitersList:
            if(terminal == word):
                return True;

        return False;



class RulesHanler(ProjectSolution):
    def __init__(self, rulesList, maxDeepFromEnd):
        self.rulesDict = {}

        for x in range(maxDeepFromEnd):
            self.rulesDict[str(x+1) + "_FromLeftEnd"] = 0;

        for x in range(maxDeepFromEnd):
            self.rulesDict[str(x+1) + "_FromRightEnd"] = 0;

        for i, val in enumerate(rulesList):
            self.rulesDict["Left_" + val] = 0;

        for i, val in enumerate(rulesList):
            self.rulesDict["Right_" + val] = 0;

        for i, val in enumerate(rulesList):
            self.rulesDict["Left_Left_" + val] = 0;

        for i, val in enumerate(rulesList):
            self.rulesDict["Left_Right_" + val] = 0;

        for i, val in enumerate(rulesList):
            self.rulesDict["Right_Left_" + val] = 0;

        for i, val in enumerate(rulesList):
            self.rulesDict["Right_Right_" + val] = 0;

        self.mMaxDeepFromEnd = maxDeepFromEnd;

    def createFeaturesList(self, leftRule, rightRule, leftLeftRule, leftRightRule, rightLeftRule, rightRightRule, leftDeepFromEnd, rightDeepFromEnd):
        dic = self.rulesDict.copy();

        if (leftRule != None):
            dic["Left_" + leftRule] = 1;

        if (rightRule != None):
            dic["Right_" + rightRule] = 1;

        if (leftLeftRule != None):
            dic["Left_Left_" + leftLeftRule] = 1;

        if (leftRightRule != None):
            dic["Left_Right_" + leftRightRule] = 1;

        if (rightLeftRule != None):
            dic["Right_Left_" + rightLeftRule] = 1;

        if (rightRightRule != None):
            dic["Right_Right_" + rightRightRule] = 1;

        if(leftDeepFromEnd<=self.mMaxDeepFromEnd):
            dic[str(leftDeepFromEnd) + "_FromLeftEnd"] = 1;

        if (rightDeepFromEnd <= self.mMaxDeepFromEnd):
            dic[str(rightDeepFromEnd) + "_FromRightEnd"] = 1;

        return dic.values();

    def createFeaturesListForNodes(self, leftNode, rightNode):
        leftRule = leftNode.tag;
        rightRule = rightNode.tag;

        leftLeftRule = None;
        leftRightRule = None;
        if (len(leftNode.children) == 2):
            leftLeftRule = leftNode.children[0].tag;
            leftRightRule = leftNode.children[1].tag;

        rightLeftRule = None;
        rightRightRule = None;
        if (len(rightNode.children) == 2):
            rightLeftRule = rightNode.children[0].tag;
            rightRightRule = rightNode.children[1].tag;

        leftDeepFromEnd = self.getDeep(leftNode);
        rightDeepFromEnd = self.getDeep(rightNode);

        return self.createFeaturesList(leftRule, rightRule, leftLeftRule, leftRightRule, rightLeftRule, rightRightRule, leftDeepFromEnd, rightDeepFromEnd);

    def getDeep(self, Node):
        return 3;
        #TODO YONI

