from solution import Submission
from transformations import to_non_t, get_terminal_or_non_t


class Solution1_1(Submission) :

    def __init__(self):
        super().__init__()


    def _count_occurrences(self, node, occurrences_dict):
        if not node.children:
            return
        occurrences_dict[to_non_t(node.tag)][' '.join(map(get_terminal_or_non_t, node.children))] += 1
        for child in node.children:
            self._count_occurrences(child, occurrences_dict)