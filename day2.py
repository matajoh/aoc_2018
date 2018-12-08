""" Solution to day 2 of the 2018 Advent of Code """

from itertools import groupby
from utils import read_input


def part1(tags):
    """ Solution to part 1 """
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

    print("twos:", num_twos)
    print("threes:", num_threes)
    print(num_twos * num_threes)


def part2(tags):
    """ Solution to part 2 """
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
            print(found)
            break


def day2():
    """ Day 2 solution """
    tags = read_input(2).split('\n')
    print("Part 1")
    part1(tags)
    print("Part 2")
    part2(tags)


if __name__ == "__main__":
    day2()
