from collections import defaultdict

NON_T_PREF = '$@$'


def to_non_t(tag):
    return NON_T_PREF + tag


def is_terminal(tag):
    return tag[:len(NON_T_PREF)] != NON_T_PREF


def get_terminal_or_non_t(node):
    if node.children:
        return to_non_t(node.tag)
    return node.tag


def remove_non_t_pref(node):
    if not is_terminal(node.tag):
        node.tag = node.tag[len(NON_T_PREF):]
        for child in node.children:
            remove_non_t_pref(child)
