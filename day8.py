""" Solution to day 8 of the 2018 Advent of Code """

from collections import deque

from anytree import Node, RenderTree

from utils import read_input, parse_args


DEBUG = "2 3 0 3 10 11 12 1 1 0 1 99 2 1 1 2"


def parse_node(parent, tokens, node_count):
    """ Parse a node in the tree.

    Args:
        parent -- the parent of the node
        tokens -- the token stream
        node_count -- the number of nodes so far

    Returns node, node_count
    """
    node = Node(str(node_count), parent=parent)
    node_count += 1
    num_children = tokens.popleft()
    num_metadata = tokens.popleft()

    for _ in range(num_children):
        _, node_count = parse_node(node, tokens, node_count)

    node.metadata = []
    for _ in range(num_metadata):
        node.metadata.append(tokens.popleft())

    return node, node_count


def compute_metadata_sum(node):
    """Compute the sum of all the metadata in the tree"""
    metadata_sum = sum(node.metadata, 0)
    for child in node.children:
        metadata_sum += compute_metadata_sum(child)

    return metadata_sum


def part1(root):
    """ Solution to part 1 """
    print("Metadata sum:", compute_metadata_sum(root))


def compute_node_value(node):
    """ Compute the value of a node """
    value = 0
    if node.children:
        for index in node.metadata:
            if index == 0 or index > len(node.children):
                continue

            value += compute_node_value(node.children[index - 1])
    else:
        value = sum(node.metadata, 0)

    return value


def part2(root):
    """ Solution to part 2 """
    print("Root value:", compute_node_value(root))


def day8(debug):
    """ Solution to day 8 """
    if debug:
        tokens = deque([int(token) for token in DEBUG.split()])
    else:
        tokens = deque([int(token) for token in read_input(8).split()])

    root, node_count = parse_node(None, tokens, 0)
    assert not tokens

    print("Node Count:", node_count)
    print(RenderTree(root))

    print("Part 1")
    part1(root)

    print("Part 2")
    part2(root)


if __name__ == "__main__":
    ARGS = parse_args()
    day8(ARGS.debug)
