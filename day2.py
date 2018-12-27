""" Solution to day 2 of the 2018 Advent of Code """

from itertools import groupby
import logging
from utils import read_input, parse_args


def compute_checksum(tags):
    """ Compute the checksum for the tags """

    num_twos = 0
    num_threes = 0

    for tag in tags:
        has_two = False
        has_three = False
        for _, group in groupby(sorted(tag)):
            count = len(list(group))
            if count == 2:
                has_two = True
            if count == 3:
                has_three = True

        if has_two:
            num_twos += 1

        if has_three:
            num_threes += 1

    logging.debug("twos = %d", num_twos)
    logging.debug("threes = %d", num_threes)
    return num_twos * num_threes


def find_common_letters(tags):
    """ Find the common letters between the two most different tags """
    length = len(tags[0])

    for pos in range(length):
        subtags = set()
        found = None
        for tag in tags:
            subtag = tag[:pos] + tag[pos+1:]
            if subtag in subtags:
                found = subtag
                break
            else:
                subtags.add(subtag)

        if found:
            return found

    return None


def day2():
    """ Day 2 solution """
    parse_args()

    tags = read_input(2)
    print("Part 1")
    print(compute_checksum(tags))
    print("Part 2")
    print(find_common_letters(tags))


if __name__ == "__main__":
    day2()
