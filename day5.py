""" Solution to day 5 of the 2018 Advent of Code """

import logging

from utils import read_input, assert_equal, parse_args

START = "<start>"
END = "<end>"


def should_react(lhs, rhs):
    """ Whether these two elements should react """

    return lhs.lower() == rhs.lower() and lhs != rhs


class Node:
    """ Node in a doubly-linked list """

    def __init__(self, value):
        self.value = value
        self.next = None
        self.prev = None

    @staticmethod
    def parse(text, exclude):
        """ Parses a linked list from the input """
        start = Node(START)
        current = start
        for value in text:
            if value.lower() == exclude:
                continue

            current.next = Node(value)
            current.next.prev = current
            current = current.next

        current.next = Node(END)
        current.next.prev = current
        return start

    def react(self):
        """ Reacts the list using the reaction rules """
        current = self
        while current.next.value != END:
            if should_react(current.value, current.next.value):
                current.prev.next = current.next.next
                current.next.next.prev = current.prev
                current = current.prev
            else:
                current = current.next

    def __len__(self):
        current = self
        num_nodes = 0
        while current.next.value != END:
            current = current.next
            num_nodes += 1

        return num_nodes


def react(polymer, exclude=None):
    """ Fully react the polymer and return the final length """
    polymer = Node.parse(polymer, exclude)
    polymer.react()
    return len(polymer)


def test_day5():
    """ Test for day 5 """
    test_input = 'dabAcCaCBAcCcaDA'
    actual = react(test_input)
    expected = 10

    assert_equal(actual, expected)

    cases = [
        ('a', 6),
        ('b', 8),
        ('c', 4),
        ('d', 6)
    ]

    for unit, expected in cases:
        actual = react(test_input, unit)
        assert_equal(actual, expected)

    expected = 4
    actual = improve(test_input)
    assert_equal(actual, expected)


def improve(polymer):
    """ Find which element to remove to best improve the polymer """
    unique_elements = set(polymer.lower())
    min_length = len(polymer)
    for element in unique_elements:
        length = react(polymer, element)
        if length < min_length:
            min_length = length

        logging.debug("element: %d length: %d", element, length)

    return min_length


def day5():
    """ Solution to day 5 """
    parse_args()

    polymer = read_input(5, no_split=True)
    print("Part 1")
    print(react(polymer))
    print("Part 2")
    print(improve(polymer))


if __name__ == "__main__":
    day5()
